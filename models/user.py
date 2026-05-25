from sqlalchemy import Column, BIGINT, String, DateTime, func
from db.database import Base

class SysUser(Base):
    __tablename__ = "sys_user"

    id = Column(BIGINT, primary_key=True, autoincrement=True, comment="用户ID")
    username = Column(String(50), nullable=False, unique=True, comment="用户名")
    password = Column(String(255), nullable=False, comment="加密密码")
    name = Column(String(50), comment="姓名")
    role = Column(String(20), default="hr", comment="角色 admin/hr")
    status = Column(String(20), default="1", comment="状态")
    created_at = Column(DateTime, default=func.now(), comment="创建时间")
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now(), comment="更新时间")