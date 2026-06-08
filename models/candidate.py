from sqlalchemy import Column, BIGINT, String, Integer, Text, JSON, DateTime, func
from db.database import Base

class Candidate(Base):
    __tablename__ = "candidate"

    id = Column(BIGINT, primary_key=True, autoincrement=True)
    resume_id = Column(BIGINT, nullable=False, comment="简历ID")
    name = Column(String(50), nullable=False, comment="姓名")
    phone = Column(String(20), comment="手机号")
    email = Column(String(100), comment="邮箱")
    gender = Column(String(10), comment="性别")
    age = Column(Integer, comment="年龄")
    education = Column(String(50), comment="最高学历")
    candidate_type = Column(String(20), comment="候选人类型(在校生/应届生/有工作经验)")
    work_years = Column(Integer, comment="工作年限")
    skills = Column(JSON, comment="技能列表")
    target_position = Column(String(100), comment="求职意向/目标岗位")
    skill_description = Column(Text, comment="专业技能原始描述")
    professional_skills = Column(JSON, comment="专业技能详情(languages/frameworks/tools/certificates)")
    self_evaluation = Column(Text, comment="自我评价")
    work_experience = Column(JSON, comment="工作经历")
    internship_experience = Column(JSON, comment="实习经历")
    education_history = Column(JSON, comment="教育经历")
    project_experience = Column(JSON, comment="项目经历")
    status = Column(String(20), default="active", comment="状态")
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())