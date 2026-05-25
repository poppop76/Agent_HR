import json
from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException,Response
from sqlalchemy.orm import Session
from core.config import settings
from db.database import get_db
from models.user import SysUser
import json

from schemas.user_schema import UserAddInfo, UserUpdate

router = APIRouter(prefix = settings.API_PREFIX)

@router.get("/user/list")
def getUserList(db: Session = Depends(get_db)):

    print("开始查询所有用户列表")

    # 查询所有用户，返回 SysUser 对象列表
    user_list = db.query(SysUser).all()

    data = []
    for u in user_list:
        data.append({
            "id": u.id,
            "username": u.username,
            "name": u.name,
            "role": u.role,
            "status": u.status,
            "created_at": u.created_at.isoformat() if u.created_at else None,
            "updated_at": u.updated_at.isoformat() if u.updated_at else None
        })

    return Response(
        content=json.dumps({
            "code": settings.RES_CODE["200"],
            "msg": "查询成功！",
            "data": data
        }, ensure_ascii=False),
        media_type="application/json"
    )



@router.post("/user/add")
def addUser(user_info : UserAddInfo,
            db: Session = Depends(get_db)):

    print(f"开始添加用户:{user_info}")
    # 校验角色是否合法
    if user_info.role not in ["admin", "hr"]:
        raise HTTPException(status_code=settings.RES_CODE["400"], detail="角色只能是 admin 或 hr")

    # 检查用户名是否已存在
    exists = db.query(SysUser).filter(SysUser.username == user_info.username).first()
    if exists:
        raise HTTPException(status_code=settings.RES_CODE["400"], detail="用户名已存在")

    # 创建用户对象
    new_user = SysUser(
        username=user_info.username,
        name=user_info.name,
        password=user_info.password,
        role=user_info.role,
        status= "1"
    )

    # 保存到数据库
    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    return Response(
        content=json.dumps({
            "code": settings.RES_CODE["200"],
            "msg": "添加成功！",
            "data": None
        }, ensure_ascii=False),
        media_type="application/json"
    )


@router.put("/user/update/{id}")
def updateUser(id: int,
               user_info: UserUpdate,
               db: Session = Depends(get_db)):

    print(f"开始更新用户信息:{id},{user_info}")

    user = db.query(SysUser).filter(SysUser.id == id).first()

    if user is None:
        raise HTTPException(status_code=settings.RES_CODE["404"], detail="用户不存在")

    # 更新字段
    if user_info.name is not None:
        user.name = user_info.name

    if user_info.role is not None:
        if user_info.role not in ["admin", "hr"]:
            raise HTTPException(status_code=400, detail="角色只能是 admin 或 hr")
        user.role = user_info.role

    if user_info.status is not None:
        user.status = str(user_info.status)

    db.commit()

    return Response(
        content=json.dumps({
            "code": settings.RES_CODE["200"],
            "msg": "更新成功！",
            "data": None
        }, ensure_ascii=False),
        media_type="application/json"
    )


@router.delete("/user/delete/{id}")
def deleteUser(id: int,
               db: Session = Depends(get_db)):

    print(f"开始删除用户:{id}")

    user = db.query(SysUser).filter(SysUser.id == id).first()

    if not user:
        raise HTTPException(status_code=settings.RES_CODE["404"],detail="用户不存在")

    #删除用户
    db.delete(user)
    db.commit()

    return Response(
        content=json.dumps({
            "code": settings.RES_CODE["200"],
            "msg":"删除成功！",
            "data": None
        },ensure_ascii=False),
        media_type="application/json"
    )