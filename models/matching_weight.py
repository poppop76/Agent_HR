from sqlalchemy import Column, BIGINT, String, DECIMAL, DateTime, func
from db.database import Base

class MatchingWeight(Base):
    __tablename__ = "matching_weight"

    id = Column(BIGINT, primary_key=True, autoincrement=True)
    job_type = Column(String(50), unique=True, nullable=False, comment="岗位类别")
    job_type_desc = Column(String(100), comment="描述")
    skill_weight = Column(DECIMAL(3,2), nullable=False, comment="技能权重")
    experience_weight = Column(DECIMAL(3,2), nullable=False, comment="经验")
    education_weight = Column(DECIMAL(3,2), nullable=False, comment="学历")
    project_weight = Column(DECIMAL(3,2), nullable=False, comment="项目")
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())