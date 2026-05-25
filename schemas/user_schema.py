from pydantic import BaseModel

# 接收登录的 JSON 数据
class UserLoginSchema(BaseModel):
    username: str
    password: str