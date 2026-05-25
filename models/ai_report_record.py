from sqlalchemy import Column, BIGINT, String, Integer, Text, DateTime, func, DECIMAL
from db.database import Base

class AiReportRecord(Base):
    __tablename__ = "ai_report_record"

    id = Column(BIGINT, primary_key=True, autoincrement=True)
    report_type = Column(String(50), nullable=False, comment="报告类型")
    period = Column(String(20), comment="周期")
    title = Column(String(200), nullable=False, comment="标题")
    content = Column(Text, comment="内容")
    new_resumes = Column(Integer, default=0)
    match_count = Column(Integer, default=0)
    avg_score = Column(DECIMAL(5,2))
    status = Column(Integer, default=1, comment="状态")
    created_at = Column(DateTime, default=func.now())