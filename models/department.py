from sqlalchemy import Column, BIGINT, String, DateTime, SmallInteger, func
from db.database import Base

class Department(Base):
    __tablename__ = "department"

    id = Column(BIGINT, primary_key=True, autoincrement=True, comment="部门ID")
    name = Column(String(100), nullable=False, unique=True, comment="部门名称")
    description = Column(String(500), comment="部门描述")
    status = Column(SmallInteger, default=1, comment="状态（1=启用，0=禁用）")
    created_at = Column(DateTime, default=func.now(), comment="创建时间")
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now(), comment="更新时间")