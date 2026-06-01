from fastapi import APIRouter, Depends, Response, HTTPException, Query
from sqlalchemy.orm import Session
from core.config import settings
from db.database import get_db
from models.matching_task import MatchingTask
from models.matching_result import MatchingResult
from models.candidate import Candidate
from models.job import Job
from models.resume import Resume
from schemas.matching_schema import MatchingRunSchema
import json

router = APIRouter(prefix=settings.API_PREFIX)


@router.post("/matching/run")
def run_matching(query: MatchingRunSchema,
                 db: Session = Depends(get_db)):

    print(f"开始执行人岗匹配:jobId={query.jobId},resumeIds={query.resumeIds}")

    # 校验岗位是否存在
    job = db.query(Job).filter(Job.id == query.jobId).first()
    if not job:
        raise HTTPException(status_code=settings.RES_CODE["404"], detail="岗位不存在！")

    # 校验简历是否存在
    resumes = db.query(Resume).filter(Resume.id.in_(query.resumeIds)).all()
    if len(resumes) != len(query.resumeIds):
        raise HTTPException(status_code=settings.RES_CODE["400"], detail="部分简历不存在！")

    if len(query.resumeIds) > 100:
        raise HTTPException(status_code=settings.RES_CODE["400"], detail="单次最多匹配100份简历！")

    # 创建匹配任务
    new_task = MatchingTask(
        job_id=query.jobId,
        resume_ids=query.resumeIds,
        status="pending",
        total_count=len(query.resumeIds),
        completed_count=0,
        progress=0
    )

    db.add(new_task)
    db.commit()
    db.refresh(new_task)

    return Response(
        content=json.dumps({
            "code": settings.RES_CODE["200"],
            "msg": "匹配任务已创建！",
            "data": {
                "taskId": new_task.id
            }
        }, ensure_ascii=False),
        media_type="application/json"
    )


@router.get("/matching/resultList")
def matching_result_list(jobId: int = Query(...),
                         page: int = Query(1, ge=1),
                         pageSize: int = Query(10, ge=1),
                         db: Session = Depends(get_db)):

    print(f"开始查询匹配结果列表:jobId={jobId}")

    query = db.query(MatchingResult).filter(MatchingResult.job_id == jobId)

    total = query.count()

    results = query.order_by(MatchingResult.total_score.desc()).offset((page - 1) * pageSize).limit(pageSize).all()

    result_list = []
    for r in results:
        candidate = db.query(Candidate).filter(Candidate.id == r.candidate_id).first()
        result_list.append({
            "id": r.id,
            "candidateId": r.candidate_id,
            "candidateName": candidate.name if candidate else "",
            "totalScore": float(r.total_score) if r.total_score else 0,
            "skillScore": float(r.skill_score) if r.skill_score else 0,
            "experienceScore": float(r.experience_score) if r.experience_score else 0,
            "educationScore": float(r.education_score) if r.education_score else 0,
            "projectScore": float(r.project_score) if r.project_score else 0,
            "highlights": r.highlights or [],
            "shortcomings": r.shortcomings or []
        })

    return Response(
        content=json.dumps({
            "code": settings.RES_CODE["200"],
            "msg": "查询成功！",
            "data": {
                "list": result_list,
                "total": total,
                "page": page,
                "pageSize": pageSize
            }
        }, ensure_ascii=False),
        media_type="application/json"
    )


@router.get("/matching/report/{id}")
def get_matching_report(id: int,
                        db: Session = Depends(get_db)):

    print(f"开始查询匹配报告:{id}")

    result = db.query(MatchingResult).filter(MatchingResult.id == id).first()

    if not result:
        raise HTTPException(status_code=settings.RES_CODE["404"], detail="匹配结果不存在！")

    job = db.query(Job).filter(Job.id == result.job_id).first()
    candidate = db.query(Candidate).filter(Candidate.id == result.candidate_id).first()

    return Response(
        content=json.dumps({
            "code": settings.RES_CODE["200"],
            "msg": "查询成功！",
            "data": {
                "id": result.id,
                "jobInfo": {
                    "id": job.id if job else None,
                    "name": job.name if job else "",
                    "jobType": job.job_type if job else "",
                    "department": job.department if job else ""
                } if job else {},
                "candidateInfo": {
                    "id": candidate.id if candidate else None,
                    "name": candidate.name if candidate else "",
                    "phone": candidate.phone if candidate else "",
                    "email": candidate.email if candidate else "",
                    "education": candidate.education if candidate else "",
                    "workYears": candidate.work_years if candidate else 0,
                    "skills": candidate.skills if candidate else []
                } if candidate else {},
                "totalScore": float(result.total_score) if result.total_score else 0,
                "dimensionScores": {
                    "skill": float(result.skill_score) if result.skill_score else 0,
                    "experience": float(result.experience_score) if result.experience_score else 0,
                    "education": float(result.education_score) if result.education_score else 0,
                    "project": float(result.project_score) if result.project_score else 0
                },
                "highlights": result.highlights or [],
                "shortcomings": result.shortcomings or [],
                "suggestions": result.suggestions or []
            }
        }, ensure_ascii=False),
        media_type="application/json"
    )
