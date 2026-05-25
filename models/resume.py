from sqlalchemy import Column, BIGINT, String, Text, DateTime, func
from db.database import Base

class Resume(Base):
    __tablename__ = "resume"

    id = Column(BIGINT, primary_key=True, autoincrement=True)
    file_name = Column(String(255), nullable=False, comment="文件名")
    file_path = Column(String(512), nullable=False, comment="路径")
    file_type = Column(String(20), comment="类型 pdf/doc")
    file_size = Column(BIGINT, comment="大小")
    parse_status = Column(String(20), default="pending", comment="解析状态")
    parse_progress = Column(BIGINT, default=0, comment="进度")
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())