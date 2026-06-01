from fastapi import APIRouter, Depends, Response, HTTPException
from sqlalchemy.orm import Session
from core.config import settings
from db.database import get_db
from models.job_category import JobCategory
from models.matching_weight import MatchingWeight
from schemas.category_schema import CategoryAddSchema, CategoryUpdateSchema, CategoryUpdateWeightSchema
import json

router = APIRouter(prefix=settings.API_PREFIX)


@router.get("/category/list")
def category_list(db: Session = Depends(get_db)):

    print("开始查询岗位类别列表")

    categories = db.query(JobCategory).order_by(JobCategory.sort_order).all()

    result_list = []
    for c in categories:
        weight = db.query(MatchingWeight).filter(MatchingWeight.category_id == c.id).first()
        result_list.append({
            "id": c.id,
            "code": c.code,
            "name": c.name,
            "description": c.description,
            "status": c.status,
            "sortOrder": c.sort_order,
            "weight": {
                "skillWeight": float(weight.skill_weight) if weight else 0,
                "experienceWeight": float(weight.experience_weight) if weight else 0,
                "educationWeight": float(weight.education_weight) if weight else 0,
                "projectWeight": float(weight.project_weight) if weight else 0
            } if weight else None
        })

    return Response(
        content=json.dumps({
            "code": settings.RES_CODE["200"],
            "msg": "查询成功！",
            "data": result_list
        }, ensure_ascii=False),
        media_type="application/json"
    )


@router.post("/category/add")
def add_category(query: CategoryAddSchema,
                 db: Session = Depends(get_db)):

    print(f"开始新增岗位类别:{query}")

    exist = db.query(JobCategory).filter(JobCategory.code == query.code).first()
    if exist:
        raise HTTPException(status_code=settings.RES_CODE["400"], detail="该类别编码已存在！")

    new_category = JobCategory(
        code=query.code,
        name=query.name,
        description=query.description,
        sort_order=query.sortOrder or 0,
        status=1
    )

    db.add(new_category)
    db.commit()
    db.refresh(new_category)

    # 自动创建默认权重配置
    default_weight = MatchingWeight(
        category_id=new_category.id,
        skill_weight=0.30,
        experience_weight=0.30,
        education_weight=0.20,
        project_weight=0.20
    )
    db.add(default_weight)
    db.commit()

    return Response(
        content=json.dumps({
            "code": settings.RES_CODE["200"],
            "msg": "类别添加成功！",
            "data": {
                "id": new_category.id
            }
        }, ensure_ascii=False),
        media_type="application/json"
    )


@router.put("/category/update/{id}")
def update_category(id: int,
                    query: CategoryUpdateSchema,
                    db: Session = Depends(get_db)):

    print(f"开始更新岗位类别:{id}")

    category = db.query(JobCategory).filter(JobCategory.id == id).first()

    if not category:
        raise HTTPException(status_code=settings.RES_CODE["404"], detail="类别不存在！")

    if query.name is not None:
        category.name = query.name
    if query.description is not None:
        category.description = query.description
    if query.status is not None:
        category.status = query.status
    if query.sortOrder is not None:
        category.sort_order = query.sortOrder

    db.commit()

    return Response(
        content=json.dumps({
            "code": settings.RES_CODE["200"],
            "msg": "类别更新成功！",
            "data": None
        }, ensure_ascii=False),
        media_type="application/json"
    )


@router.delete("/category/delete/{id}")
def delete_category(id: int,
                    db: Session = Depends(get_db)):

    print(f"开始删除岗位类别:{id}")

    category = db.query(JobCategory).filter(JobCategory.id == id).first()

    if not category:
        raise HTTPException(status_code=settings.RES_CODE["404"], detail="类别不存在！")

    # 检查是否有关联岗位
    from models.job import Job
    job_count = db.query(Job).filter(Job.job_type == category.code).count()
    if job_count > 0:
        raise HTTPException(status_code=settings.RES_CODE["400"], detail=f"该类别下还有{job_count}个岗位，无法删除！")

    # 删除关联权重
    db.query(MatchingWeight).filter(MatchingWeight.category_id == id).delete()

    db.delete(category)
    db.commit()

    return Response(
        content=json.dumps({
            "code": settings.RES_CODE["200"],
            "msg": "类别删除成功！",
            "data": None
        }, ensure_ascii=False),
        media_type="application/json"
    )


@router.put("/category/weight/{id}")
def update_category_weight(id: int,
                           query: CategoryUpdateWeightSchema,
                           db: Session = Depends(get_db)):

    print(f"开始更新类别权重:{id}")

    weight = db.query(MatchingWeight).filter(MatchingWeight.category_id == id).first()

    if not weight:
        raise HTTPException(status_code=settings.RES_CODE["404"], detail="权重配置不存在！")

    if query.skillWeight is not None:
        weight.skill_weight = query.skillWeight
    if query.experienceWeight is not None:
        weight.experience_weight = query.experienceWeight
    if query.educationWeight is not None:
        weight.education_weight = query.educationWeight
    if query.projectWeight is not None:
        weight.project_weight = query.projectWeight

    db.commit()

    return Response(
        content=json.dumps({
            "code": settings.RES_CODE["200"],
            "msg": "权重更新成功！",
            "data": None
        }, ensure_ascii=False),
        media_type="application/json"
    )
