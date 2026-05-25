from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from core.jwt_config import JwtUtil

# 绑定登录接口地址，等同于拦截注册
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/user/login")

# 全局拦截校验方法
def login_interceptor(token: str = Depends(oauth2_scheme)) -> str:
    username = JwtUtil.parse_token(token)
    if not username:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="令牌无效、过期，请重新登录"
        )
    return username