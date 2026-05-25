from sqlalchemy import Column, BIGINT, String, Integer, Text, JSON, DateTime, func
from db.database import Base

class MatchingTask(Base):
    __tablename__ = "matching_task"

    id = Column(BIGINT, primary_key=True, autoincrement=True)
    job_id = Column(BIGINT, nullable=False, comment="岗位ID")
    resume_ids = Column(JSON, nullable=False, comment="简历ID列表")
    status = Column(String(20), default="pending", comment="状态")
    progress = Column(Integer, default=0, comment="进度")
    total_count = Column(Integer, comment="总数")
    completed_count = Column(Integer, comment="完成数")
    error_message = Column(Text, comment="错误信息")
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())
    completed_at = Column(DateTime, comment="完成时间")