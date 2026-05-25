from typing import Optional

from pydantic import BaseModel

class UserLoginInfo(BaseModel):
    id: int
    username: str
    name: str
    role: str


class UserLoginRequestSchema(BaseModel):
    token: str
    user: UserLoginInfo
