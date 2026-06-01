from sqlalchemy import Column, BIGINT, String, Integer, DateTime, func
from db.database import Base

class JobCategory(Base):
    __tablename__ = "job_category"

    id = Column(BIGINT, primary_key=True, autoincrement=True)
    code = Column(String(50), unique=True, nullable=False, comment="类别编码")
    name = Column(String(100), nullable=False, comment="类别名称")
    description = Column(String(500), comment="类别描述")
    status = Column(Integer, default=1, comment="状态")
    sort_order = Column(Integer, default=0, comment="排序")
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())
