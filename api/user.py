import json
from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException,Response
from sqlalchemy.orm import Session
from core.config import settings
from db.database import get_db
from models.user import SysUser
import json

from schemas.user_response_schema import UserAddResponseSchema, UserUpdateResponseSchema

router = APIRouter(prefix = settings.API_PREFIX)

@router.get("/user/list")
def getUserList(db: Session = Depends(get_db)):

    print("开始查询所有用户列表")

    # 查询所有用户，返回 SysUser 对象列表
    user_list = db.query(SysUser).all()

    return Response(
        content=json.dumps({
            "code": settings.RES_CODE["200"],
            "msg": "查询成功！",
            "data": user_list.dict()
        }, ensure_ascii=False),
        media_type="application/json"
    )



@router.post("/user/add")
def addUser(user_info : UserAddResponseSchema,
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
               user_info: UserUpdateResponseSchema,
               db: Session = Depends(get_db)):

    print("开始更新用户信息")

    user = db.query(SysUser).filter(SysUser.id == id).first()

    if user is None:
        raise HTTPException(status_code=settings.RES_CODE["404"], detail="用户不存在")

