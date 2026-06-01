from typing import Optional
from pydantic import BaseModel

# 添加部门接收
class DepartmentAddSchema(BaseModel):
    name: str
    description: Optional[str] = None

# 更新部门接收
class DepartmentUpdateSchema(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    status: Optional[int] = None
