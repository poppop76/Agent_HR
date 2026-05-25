from sqlalchemy import Column, BIGINT, DECIMAL, JSON, DateTime, func
from db.database import Base

class MatchingResult(Base):
    __tablename__ = "matching_result"

    id = Column(BIGINT, primary_key=True, autoincrement=True)
    task_id = Column(BIGINT, nullable=False)
    job_id = Column(BIGINT, nullable=False)
    candidate_id = Column(BIGINT, nullable=False)
    resume_id = Column(BIGINT, nullable=False)
    total_score = Column(DECIMAL(5,2), comment="总分")
    skill_score = Column(DECIMAL(5,2))
    experience_score = Column(DECIMAL(5,2))
    education_score = Column(DECIMAL(5,2))
    project_score = Column(DECIMAL(5,2))
    highlights = Column(JSON, comment="亮点")
    shortcomings = Column(JSON, comment="短板")
    suggestions = Column(JSON, comment="建议")
    weight_info = Column(JSON, comment="权重信息")
    created_at = Column(DateTime, default=func.now())