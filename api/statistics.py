from fastapi import APIRouter, Depends, Response, Query
from sqlalchemy.orm import Session
from sqlalchemy import func
from core.config import settings
from db.database import get_db
from models.resume import Resume
from models.job import Job
from models.matching_task import MatchingTask
from datetime import datetime, timedelta
import json

router = APIRouter(prefix=settings.API_PREFIX)


@router.get("/statistics/overview")
def statistics_overview(period: str = Query("week"),
                        db: Session = Depends(get_db)):

    print(f"开始查询概览统计:period={period}")

    # 简历总数
    resume_count = db.query(Resume).count()

    # 岗位总数
    job_count = db.query(Job).count()

    # 匹配任务数
    matching_task_count = db.query(MatchingTask).count()

    # 解析率统计
    success_count = db.query(Resume).filter(Resume.parse_status == "success").count()
    fail_count = db.query(Resume).filter(Resume.parse_status == "fail").count()
    processing_count = db.query(Resume).filter(Resume.parse_status == "processing").count()

    total_parsed = success_count + fail_count
    parse_rate = round((success_count / total_parsed * 100), 1) if total_parsed > 0 else 0

    # 上传趋势
    today = datetime.now().date()
    if period == "day":
        days = 7
    elif period == "month":
        days = 30
    else:
        days = 7

    upload_trend = []
    for i in range(days - 1, -1, -1):
        day = today - timedelta(days=i)
        day_start = datetime.combine(day, datetime.min.time())
        day_end = datetime.combine(day, datetime.max.time())

        count = db.query(Resume).filter(
            Resume.created_at >= day_start,
            Resume.created_at <= day_end
        ).count()

        upload_trend.append({
            "date": day.strftime("%m-%d"),
            "count": count
        })

    return Response(
        content=json.dumps({
            "code": settings.RES_CODE["200"],
            "msg": "查询成功！",
            "data": {
                "resumeCount": resume_count,
                "jobCount": job_count,
                "matchingTaskCount": matching_task_count,
                "parseRate": {
                    "rate": parse_rate,
                    "successCount": success_count,
                    "failCount": fail_count,
                    "processingCount": processing_count
                },
                "uploadTrend": upload_trend
            }
        }, ensure_ascii=False),
        media_type="application/json"
    )
