from fastapi import APIRouter, Depends,Response,HTTPException
from sqlalchemy.orm import Session
from core.config import settings
from db.database import get_db
from models.department import Department
from schemas.department_schema import DepartmentAddSchema, DepartmentUpdateSchema
import json

router = APIRouter(prefix = settings.API_PREFIX)

@router.get("/department/list")
def get_department(db: Session = Depends(get_db)):

    print("开始查询部门")

    department_list = db.query(Department).all()

    data = []
    for d in department_list:
        data.append({
            "id": d.id,
            "name": d.name,
            "description": d.description,
            "status": d.status
        })

    return Response(
        content=json.dumps({
            "code": settings.RES_CODE["200"],
            "msg": "查询成功！",
            "data": data
        }, ensure_ascii=False),
        media_type="application/json"
    )


@router.post("/department/add")
def add_department(query: DepartmentAddSchema,
                   db: Session = Depends(get_db)):

    print(f"开始新增部门:{query}")

    dept = db.query(Department).filter(Department.name == query.name).first()

    if dept:
        raise HTTPException(status_code=settings.RES_CODE["400"], detail="该部门已存在！不可重复创建")

    new_dept = Department(
        name=query.name,
        description=query.description,
        status=1
    )

    db.add(new_dept)
    db.commit()
    db.refresh(new_dept)

    return Response(
        content=json.dumps({
            "code": settings.RES_CODE["200"],
            "msg": "部门添加成功！",
            "data": {
                "id": new_dept.id
            }
        }, ensure_ascii=False),
        media_type="application/json"
    )


@router.put("/department/update/{id}")
def update_department(id: int,
                      query: DepartmentUpdateSchema,
                      db: Session = Depends(get_db)):

    print(f"开始更新部门:{id} {query}")

    dept = db.query(Department).filter(Department.id == id).first()

    if not dept:
        raise HTTPException(status_code=settings.RES_CODE["404"], detail="部门不存在！")

    if query.name:
        # 检查新名称是否与其他部门重复
        exist = db.query(Department).filter(Department.name == query.name, Department.id != id).first()
        if exist:
            raise HTTPException(status_code=settings.RES_CODE["400"], detail="部门名称已存在！")
        dept.name = query.name

    if query.description is not None:
        dept.description = query.description

    if query.status is not None:
        dept.status = query.status

    db.commit()

    return Response(
        content=json.dumps({
            "code": settings.RES_CODE["200"],
            "msg": "部门更新成功！",
            "data": None
        }, ensure_ascii=False),
        media_type="application/json"
    )


@router.delete("/department/delete/{id}")
def delete_department(id: int,
                      db: Session = Depends(get_db)):

    print(f"开始删除部门:{id}")

    dept = db.query(Department).filter(Department.id == id).first()

    if not dept:
        raise HTTPException(status_code=settings.RES_CODE["404"], detail="部门不存在！")

    db.delete(dept)
    db.commit()

    return Response(
        content=json.dumps({
            "code": settings.RES_CODE["200"],
            "msg": "部门删除成功！",
            "data": None
        }, ensure_ascii=False),
        media_type="application/json"
    )

