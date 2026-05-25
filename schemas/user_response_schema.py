from typing import Optional

from pydantic import BaseModel


class UserLoginInfo(BaseModel):
    id: int
    username: str
    name: str
    role: str


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

#登录接收
class UserLoginResponseSchema(BaseModel):
    token: str
    user: UserLoginInfo

#添加接收
class UserAddResponseSchema(BaseModel):
    user : UserAddInfo

#更新接收
class UserUpdateResponseSchema(BaseModel):
    user: UserUpdate