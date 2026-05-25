from typing import Optional

from pydantic import BaseModel

# 接收登录的 JSON 数据
class UserLoginSchema(BaseModel):
    username: str
    password: str

#添加接收
class UserAddInfo(BaseModel):
    username: str
    name: str
    password: str
    role: str

#更新接收
class UserUpdate(BaseModel):
    name: Optional[str] = None
    role: Optional[str] = None
    status: Optional[int] = None