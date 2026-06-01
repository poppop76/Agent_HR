from sqlalchemy import Column, BIGINT, DECIMAL, DateTime, func, ForeignKey
from db.database import Base

class MatchingWeight(Base):
    __tablename__ = "matching_weight"

    id = Column(BIGINT, primary_key=True, autoincrement=True)
    category_id = Column(BIGINT, ForeignKey("job_category.id"), nullable=False, comment="关联类别ID")
    skill_weight = Column(DECIMAL(3,2), nullable=False, comment="技能权重")
    experience_weight = Column(DECIMAL(3,2), nullable=False, comment="经验")
    education_weight = Column(DECIMAL(3,2), nullable=False, comment="学历")
    project_weight = Column(DECIMAL(3,2), nullable=False, comment="项目")
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())