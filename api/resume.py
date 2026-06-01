from fastapi import APIRouter, Depends, Response, HTTPException, UploadFile, File, Query
from sqlalchemy.orm import Session
from sqlalchemy import func
from core.config import settings
from db.database import get_db
from models.resume import Resume
from models.candidate import Candidate
import json
import os
import uuid

router = APIRouter(prefix=settings.API_PREFIX)

UPLOAD_DIR = "uploads/resumes"
ALLOWED_TYPES = {".pdf", ".doc", ".docx", ".txt"}
MAX_SIZE = 20 * 1024 * 1024  # 20MB


@router.post("/resume/upload")
def upload_resume(file: UploadFile = File(...),
                  db: Session = Depends(get_db)):

    print(f"开始上传简历:{file.filename}")

    # 校验文件类型
    ext = os.path.splitext(file.filename)[1].lower()
    if ext not in ALLOWED_TYPES:
        raise HTTPException(status_code=settings.RES_CODE["400"], detail=f"不支持的文件类型，仅支持：{', '.join(ALLOWED_TYPES)}")

    # 校验文件大小
    file.file.seek(0, 2)
    size = file.file.tell()
    file.file.seek(0)
    if size > MAX_SIZE:
        raise HTTPException(status_code=settings.RES_CODE["400"], detail="文件大小超过20MB限制")

    # 保存文件
    os.makedirs(UPLOAD_DIR, exist_ok=True)
    unique_name = f"{uuid.uuid4().hex}{ext}"
    file_path = os.path.join(UPLOAD_DIR, unique_name)

    with open(file_path, "wb") as f:
        f.write(file.file.read())

    # 创建简历记录
    new_resume = Resume(
        file_name=file.filename,
        file_path=file_path,
        file_type=ext.lstrip("."),
        file_size=size,
        parse_status="pending"
    )

    db.add(new_resume)
    db.commit()
    db.refresh(new_resume)

    return Response(
        content=json.dumps({
            "code": settings.RES_CODE["200"],
            "msg": "简历上传成功！",
            "data": {
                "id": new_resume.id,
                "fileName": new_resume.file_name,
                "filePath": new_resume.file_path,
                "parseStatus": new_resume.parse_status
            }
        }, ensure_ascii=False),
        media_type="application/json"
    )


@router.get("/resume/list")
def resume_list(page: int = Query(1, ge=1),
                pageSize: int = Query(10, ge=1),
                keyword: str = Query(""),
                parseStatus: str = Query(""),
                name: str = Query(""),
                status: str = Query(""),
                db: Session = Depends(get_db)):

    print(f"开始查询简历列表:page={page},pageSize={pageSize},keyword={keyword}")

    query = db.query(Resume).outerjoin(Candidate, Resume.id == Candidate.resume_id)

    if keyword:
        query = query.filter(Resume.file_name.like(f"%{keyword}%"))
    if parseStatus:
        query = query.filter(Resume.parse_status == parseStatus)
    if name:
        query = query.filter(Candidate.name.like(f"%{name}%"))
    if status:
        query = query.filter(Resume.parse_status == status)

    total = query.count()

    resumes = query.order_by(Resume.created_at.desc()).offset((page - 1) * pageSize).limit(pageSize).all()

    result_list = []
    for r in resumes:
        candidate = db.query(Candidate).filter(Candidate.resume_id == r.id).first()
        result_list.append({
            "id": r.id,
            "fileName": r.file_name,
            "fileType": r.file_type,
            "parseStatus": r.parse_status,
            "name": candidate.name if candidate else "",
            "phone": candidate.phone if candidate else "",
            "email": candidate.email if candidate else "",
            "education": candidate.education if candidate else "",
            "workYears": candidate.work_years if candidate else 0,
            "uploadedAt": r.created_at.strftime("%Y-%m-%d %H:%M:%S") if r.created_at else ""
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


@router.delete("/resume/delete/{id}")
def delete_resume(id: int,
                  db: Session = Depends(get_db)):

    print(f"开始删除简历:{id}")

    resume = db.query(Resume).filter(Resume.id == id).first()

    if not resume:
        raise HTTPException(status_code=settings.RES_CODE["404"], detail="简历不存在！")

    # 删除文件
    if os.path.exists(resume.file_path):
        os.remove(resume.file_path)

    # 删除关联候选人
    db.query(Candidate).filter(Candidate.resume_id == id).delete()

    db.delete(resume)
    db.commit()

    return Response(
        content=json.dumps({
            "code": settings.RES_CODE["200"],
            "msg": "简历删除成功！",
            "data": None
        }, ensure_ascii=False),
        media_type="application/json"
    )
