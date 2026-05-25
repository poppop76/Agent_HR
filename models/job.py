from sqlalchemy import Column, BIGINT, String, Text, DateTime, func
from db.database import Base

class Job(Base):
    __tablename__ = "job"

    id = Column(BIGINT, primary_key=True, autoincrement=True)
    name = Column(String(100), nullable=False, comment="岗位名称")
    job_type = Column(String(50), comment="岗位类别")
    department = Column(String(50), comment="部门")
    salary = Column(String(50), comment="薪资")
    location = Column(String(100), comment="地点")
    requirements = Column(Text, comment="任职要求")
    responsibilities = Column(Text, comment="岗位职责")
    status = Column(String(20), default="unpublished", comment="状态")
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())