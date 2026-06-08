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
import re

router = APIRouter(prefix=settings.API_PREFIX)


def get_candidate_info(candidate: Candidate) -> str:
    """获取候选人信息文本"""
    return f"""姓名：{candidate.name}
学历：{candidate.education or ''}
工作年限：{candidate.work_years or 0}年
技能：{str(candidate.skills or [])}
目标岗位：{candidate.target_position or ''}
专业技能描述：{candidate.skill_description or ''}"""


def get_job_info(job: Job) -> str:
    """获取岗位信息文本"""
    return f"""岗位名称：{job.name}
岗位类别：{job.job_type or ''}
部门：{job.department or ''}
薪资：{job.salary or ''}
地点：{job.location or ''}"""


def execute_matching(job: Job, candidate: Candidate) -> dict:
    """执行单次人岗匹配"""
    from agent.react_agent import ReactAgent
    from agent.model.factory import chat_model
    import re
    
    prompt_template = """你是一个资深HR专家。请根据以下岗位要求和候选人信息进行人岗匹配评估。

【岗位要求】
{requirements}

【岗位职责】
{responsibilities}

【候选人信息】
{name}

请从以下四个维度打分（0-100分），并给出亮点、短板和建议。
必须严格按以下JSON格式返回，不要包含任何解释性文字：
{{
  "skill_score": 85,
  "experience_score": 70,
  "education_score": 90,
  "project_score": 80,
  "highlights": ["亮点1", "亮点2"],
  "shortcomings": ["短板1"],
  "suggestions": ["建议1"]
}}"""

    prompt = prompt_template.format(
        requirements=job.requirements or '',
        responsibilities=job.responsibilities or '',
        name=get_candidate_info(candidate)
    )
    
    try:
        # 使用 load_tools=False 避免加载工具（避免触发Milvus连接）
        agent = ReactAgent(load_tools=False)
        result = agent.execute_once(prompt, response_format={"type": "json_object"})
        
        # 清理JSON格式
        clean_json = re.sub(r'^```json\s*|\s*```$', '', result.strip(), flags=re.MULTILINE)
        data = json.loads(clean_json)
        
        return {
            "skill_score": data.get("skill_score", 0),
            "experience_score": data.get("experience_score", 0),
            "education_score": data.get("education_score", 0),
            "project_score": data.get("project_score", 0),
            "total_score": (data.get("skill_score", 0) + data.get("experience_score", 0) + 
                          data.get("education_score", 0) + data.get("project_score", 0)) / 4,
            "highlights": data.get("highlights", []),
            "shortcomings": data.get("shortcomings", []),
            "suggestions": data.get("suggestions", [])
        }
    except Exception as e:
        print(f"匹配失败: {str(e)}")
        # 返回默认分数
        return {
            "skill_score": 50,
            "experience_score": 50,
            "education_score": 50,
            "project_score": 50,
            "total_score": 50,
            "highlights": [],
            "shortcomings": [],
            "suggestions": []
        }


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
        status="running",
        total_count=len(query.resumeIds),
        completed_count=0,
        progress=0
    )

    db.add(new_task)
    db.commit()
    db.refresh(new_task)
    
    task_id = new_task.id
    print(f"匹配任务创建成功: taskId={task_id}")

    # ========== 实际执行匹配 ==========
    success_count = 0
    error_count = 0
    
    for idx, resume_id in enumerate(query.resumeIds):
        try:
            # 获取候选人信息
            candidate = db.query(Candidate).filter(Candidate.resume_id == resume_id).first()
            if not candidate:
                print(f"跳过：简历 {resume_id} 没有对应的候选人")
                error_count += 1
                continue
            
            print(f"正在匹配: {idx+1}/{len(query.resumeIds)} - 候选人: {candidate.name}")
            
            # 执行AI匹配
            match_result = execute_matching(job, candidate)
            
            # 保存匹配结果
            result = MatchingResult(
                task_id=task_id,
                job_id=query.jobId,
                candidate_id=candidate.id,
                resume_id=resume_id,
                total_score=match_result["total_score"],
                skill_score=match_result["skill_score"],
                experience_score=match_result["experience_score"],
                education_score=match_result["education_score"],
                project_score=match_result["project_score"],
                highlights=match_result["highlights"],
                shortcomings=match_result["shortcomings"],
                suggestions=match_result["suggestions"]
            )
            db.add(result)
            
            success_count += 1
            
        except Exception as e:
            print(f"匹配失败 resumeId={resume_id}: {str(e)}")
            error_count += 1
        
        # 更新任务进度
        new_task.completed_count = success_count + error_count
        new_task.progress = int((new_task.completed_count / new_task.total_count) * 100)
        db.commit()
    
    # 更新任务状态
    new_task.status = "completed"
    db.commit()
    
    print(f"匹配完成: 成功={success_count}, 失败={error_count}")

    return Response(
        content=json.dumps({
            "code": settings.RES_CODE["200"],
            "msg": f"匹配完成！成功{success_count}人，失败{error_count}人",
            "data": {
                "taskId": task_id,
                "successCount": success_count,
                "errorCount": error_count
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


@router.get("/matching/task/{id}")
def get_matching_task(id: int,
                      db: Session = Depends(get_db)):
    """查询匹配任务状态"""
    task = db.query(MatchingTask).filter(MatchingTask.id == id).first()
    
    if not task:
        raise HTTPException(status_code=settings.RES_CODE["404"], detail="任务不存在！")
    
    return Response(
        content=json.dumps({
            "code": settings.RES_CODE["200"],
            "msg": "查询成功！",
            "data": {
                "id": task.id,
                "jobId": task.job_id,
                "status": task.status,
                "progress": task.progress,
                "totalCount": task.total_count,
                "completedCount": task.completed_count,
                "errorMessage": task.error_message,
                "createdAt": task.created_at.isoformat() if task.created_at else None,
                "completedAt": task.completed_at.isoformat() if task.completed_at else None
            }
        }, ensure_ascii=False),
        media_type="application/json"
    )
