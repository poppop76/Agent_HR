from fastapi import APIRouter, Depends, HTTPException,Response
from sqlalchemy.orm import Session
from passlib.context import CryptContext
from core.config import settings
from db.database import get_db
from models.user import SysUser
from schemas import user_response_schema
from schemas.user_schema import UserLoginSchema
from core.jwt_config import create_access_token
from datetime import timedelta
from core.redis_client import redis_client
from schemas.user_response_schema import UserLoginResponseSchema
import json
# import logging
#
# logger = logging.getLogger(__name__)

router = APIRouter(prefix = settings.API_PREFIX)

# pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

@router.post("/auth/login")
def login(user_login: UserLoginSchema,
          db: Session = Depends(get_db)
):
    print("用户开始登录：%s", user_login.username)

    user = db.query(SysUser).filter(SysUser.username == user_login.username).first()
    if not user:
        print("登录失败：用户不存在 -> %s", user_login.username)
        raise HTTPException(status_code=settings.RES_CODE["404"],detail=settings.RES_MSG["404"])

    if user_login.password != user.password:
        print("登录失败：密码错误 -> %s", user_login.username)
        raise HTTPException(status_code=settings.RES_CODE["401"],detail="用户名或密码错误")

    token = create_access_token(
        data={"sub": user.username},  # 用户名
        expires_delta=timedelta(minutes=settings.EXPIRE_MINUTES)  # 传有效期
    )

    redis_client.setex(
        f"token:{user.username}",  # key
        timedelta(minutes=settings.EXPIRE_MINUTES),  # 过期时间
        token  # value
    )

    print("登录成功：%s", user_login.username)

    userInfo = {
        "id": user.id,
        "username": user.username,
        "name": user.name,
        "role": user.role
    }

    result = UserLoginResponseSchema(
        token = token,
        user = userInfo,
    )

    return Response(
        content=json.dumps({
            "code": settings.RES_CODE["200"],
            "msg": "登录成功",
            "data": result.dict()
        }, ensure_ascii=False),
        media_type="application/json"
    )