from typing import Optional
from pydantic import BaseModel


class CategoryAddSchema(BaseModel):
    code: str
    name: str
    description: Optional[str] = None
    sortOrder: Optional[int] = 0


class CategoryUpdateSchema(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    status: Optional[int] = None
    sortOrder: Optional[int] = None


class CategoryUpdateWeightSchema(BaseModel):
    skillWeight: Optional[float] = None
    experienceWeight: Optional[float] = None
    educationWeight: Optional[float] = None
    projectWeight: Optional[float] = None
