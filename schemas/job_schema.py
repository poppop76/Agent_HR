from typing import Optional
from datetime import datetime
from pydantic import BaseModel

#查询岗位接收
class JobListSchema(BaseModel):
    page: int = 1
    pageSize: int = 10
    keyword: Optional[str] = None
    department: Optional[str] = None
    status: Optional[str] = None
    jobType: Optional[str] = None


class JobItem(BaseModel):
    id: int
    name: str
    jobType: Optional[str] = None
    department: Optional[str] = None
    salary: Optional[str] = None
    location: Optional[str] = None
    requirements: Optional[str] = None
    responsibilities: Optional[str] = None
    status: Optional[str] = None
    createdAt: Optional[datetime] = None

    # ORM 模式 → 可以直接接收数据库对象
    class Config:
        orm_mode = True
        

#添加岗位接收
class JobAddSchema(BaseModel):
    name: str
    jobType: str
    department: str
    salary: Optional[str] = None
    location: Optional[str] = None
    requirements: str
    responsibilities: str
    status: Optional[str] = None

#更新岗位接收
class JobUpdateSchema(BaseModel):
    name: Optional[str] = None
    jobType: Optional[str] = None
    department: Optional[str] = None
    salary: Optional[str] = None
    location: Optional[str] = None
    requirements: Optional[str] = None
    responsibilities: Optional[str] = None
    status: Optional[str] = None


# 关联简历项
class RelatedResumeItem(BaseModel):
    id: int
    name: str
    matchScore: int
    createdAt: Optional[str] = None

    class Config:
        orm_mode = True


# 分数分布项
class ScoreDistributionItem(BaseModel):
    range: str
    count: int


# 申请趋势项
class ApplicationTrendItem(BaseModel):
    date: str
    count: int


# 岗位详情返回
class JobDetailResponse(BaseModel):
    id: int
    name: str
    jobType: Optional[str] = None
    department: Optional[str] = None
    salary: Optional[str] = None
    location: Optional[str] = None
    requirements: Optional[str] = None
    responsibilities: Optional[str] = None
    status: Optional[str] = None
    relatedResumes: list = []
    scoreDistribution: list = []
    applicationTrend: list = []

    class Config:
        orm_mode = True
