from fastapi import APIRouter, Depends, Response,HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import func
from core.config import settings
from db.database import get_db
from models.job import Job
from models.matching_result import MatchingResult
from models.candidate import Candidate
from schemas.job_schema import JobListSchema, JobAddSchema, JobUpdateSchema
import json
from datetime import datetime, timedelta

router = APIRouter(prefix = settings.API_PREFIX)


@router.post("/job/list")
def job_list(query : JobListSchema,
             db: Session = Depends(get_db)):

    print(f"开始查询岗位列表:{query}")

    db_query = db.query(Job)

    #动态条件筛选
    if query.keyword:
        db_query = db_query.filter(Job.name.like(f"%{query.keyword}%"))
    if query.department:
        db_query = db_query.filter(Job.department == query.department)
    if query.status:
        db_query = db_query.filter(Job.status == query.status)
    if query.jobType:
        db_query = db_query.filter(Job.job_type == query.jobType)

    #分页
    total = db_query.count()
    skip = (query.page - 1) * query.pageSize
    job_list = db_query.offset(skip).limit(query.pageSize).all()

    result = []
    for job in job_list:
        result.append({
            "id": job.id,
            "name": job.name,
            "jobType": job.job_type,
            "department": job.department,
            "salary": job.salary,
            "location": job.location,
            "requirements": job.requirements,
            "responsibilities": job.responsibilities,
            "status": job.status,
            "createdAt": job.created_at.isoformat() if job.created_at else None
        })


    return Response(
        content=json.dumps({
            "code": settings.RES_CODE["200"],
            "msg": "查询成功！",
            "data": {
                "list": result,
                "total": total,
                "page": query.page,
                "pageSize": query.pageSize
                }
        }, ensure_ascii=False),
        media_type="application/json"
    )


@router.post("/job/add")
def add_job(query : JobAddSchema,
            db: Session = Depends(get_db)):

    print(f"开始新增岗位:{query}")

    job = db.query(Job).filter(Job.name == query.name , Job.job_type == query.jobType).first()

    if job :
        raise HTTPException(status_code=settings.RES_CODE["400"], detail="该岗位已存在！不可重复创建")

    new_job = Job(
        name=query.name,
        department= query.department,
        job_type= query.jobType,
        salary = query.salary,
        location = query.location,
        requirements = query.requirements,
        responsibilities = query.responsibilities,
        status = "unpublished"
        )

    db.add(new_job)
    db.commit()
    db.refresh(new_job)

    return Response(
        content=json.dumps({
            "code": settings.RES_CODE["200"],
            "msg" : "岗位添加成功！",
            "data": new_job.id
        }, ensure_ascii=False),
        media_type="application/json"
    )


@router.put("/job/update/{id}")
def update_job(id: int,
               query: JobUpdateSchema,
               db: Session = Depends(get_db)):

    print(f"开始更新岗位:{id} {query}")

    job = db.query(Job).filter(Job.id == id).first()

    if not job:
        raise HTTPException(status_code=settings.RES_CODE["404"], detail="岗位不存在！")

    if query.name:
        job.name = query.name
    if query.jobType:
        job.job_type = query.jobType
    if query.department:
        job.department = query.department
    if query.salary:
        job.salary = query.salary
    if query.location:
        job.location = query.location
    if query.requirements:
        job.requirements = query.requirements
    if query.responsibilities:
        job.responsibilities = query.responsibilities
    if query.status:
        job.status = query.status

    db.commit()

    return Response(
        content=json.dumps({
            "code": settings.RES_CODE["200"],
            "msg": "岗位更新成功！",
            "data": None
        }, ensure_ascii=False),
        media_type="application/json"
    )


@router.delete("/job/delete/{id}")
def delete_job(id: int,
               db: Session = Depends(get_db)):

    print(f"开始删除岗位:{id}")

    job = db.query(Job).filter(Job.id == id).first()

    if not job:
        raise HTTPException(status_code=settings.RES_CODE["404"], detail="岗位不存在！")

    db.delete(job)
    db.commit()

    return Response(
        content=json.dumps({
            "code": settings.RES_CODE["200"],
            "msg": "岗位删除成功！",
            "data": None
        }, ensure_ascii=False),
        media_type="application/json"
    )


@router.put("/job/status/{id}")
def toggle_job_status(id: int,
                      db: Session = Depends(get_db)):

    print(f"开始切换岗位状态:{id}")

    job = db.query(Job).filter(Job.id == id).first()

    if not job:
        raise HTTPException(status_code=settings.RES_CODE["404"], detail="岗位不存在！")

    # 状态切换：published <-> unpublished
    job.status = "unpublished" if job.status == "published" else "published"

    db.commit()

    return Response(
        content=json.dumps({
            "code": settings.RES_CODE["200"],
            "msg": f"岗位已{job.status == 'published' and '上架' or '下架'}！",
            "data": None
        }, ensure_ascii=False),
        media_type="application/json"
    )


@router.get("/job/detail/{id}")
def get_job_detail(id: int,
                   db: Session = Depends(get_db)):

    print(f"开始查询岗位详情:{id}")

    job = db.query(Job).filter(Job.id == id).first()

    if not job:
        raise HTTPException(status_code=settings.RES_CODE["404"], detail="岗位不存在！")

    # 1. 查询关联简历（通过匹配结果关联）
    matching_results = db.query(
        MatchingResult, Candidate.name, Candidate.created_at
    ).join(
        Candidate, MatchingResult.candidate_id == Candidate.id
    ).filter(
        MatchingResult.job_id == id
    ).order_by(
        MatchingResult.total_score.desc()
    ).limit(10).all()

    related_resumes = []
    for mr, name, created_at in matching_results:
        related_resumes.append({
            "id": mr.candidate_id,
            "name": name,
            "matchScore": int(float(mr.total_score)) if mr.total_score else 0,
            "createdAt": created_at.strftime("%Y-%m-%d") if created_at else ""
        })

    # 2. 分数分布
    score_ranges = [
        {"min": 80, "max": 100, "range": "80-100分"},
        {"min": 60, "max": 79, "range": "60-79分"},
        {"min": 0, "max": 59, "range": "60分以下"}
    ]

    score_distribution = []
    for r in score_ranges:
        count = db.query(MatchingResult).filter(
            MatchingResult.job_id == id,
            MatchingResult.total_score >= r["min"],
            MatchingResult.total_score <= r["max"]
        ).count()
        score_distribution.append({
            "range": r["range"],
            "count": count
        })

    # 3. 申请趋势（近7天）
    today = datetime.now().date()
    application_trend = []
    for i in range(6, -1, -1):
        day = today - timedelta(days=i)
        day_start = datetime.combine(day, datetime.min.time())
        day_end = datetime.combine(day, datetime.max.time())

        count = db.query(MatchingResult).filter(
            MatchingResult.job_id == id,
            MatchingResult.created_at >= day_start,
            MatchingResult.created_at <= day_end
        ).count()

        application_trend.append({
            "date": day.strftime("%m-%d"),
            "count": count
        })

    return Response(
        content=json.dumps({
            "code": settings.RES_CODE["200"],
            "msg": "查询成功！",
            "data": {
                "id": job.id,
                "name": job.name,
                "jobType": job.job_type,
                "department": job.department,
                "salary": job.salary,
                "location": job.location,
                "requirements": job.requirements,
                "responsibilities": job.responsibilities,
                "status": job.status,
                "relatedResumes": related_resumes,
                "scoreDistribution": score_distribution,
                "applicationTrend": application_trend
            }
        }, ensure_ascii=False),
        media_type="application/json"
    )

