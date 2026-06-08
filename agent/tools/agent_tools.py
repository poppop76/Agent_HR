import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent.parent.parent))

import os
from agent.utils.logger_handler import logger
from langchain_core.tools import tool
import random
from agent.utils.config_handler import agent_conf
from agent.utils.path_tool import get_abs_path

from db.database import SessionLocal
from models.job import Job
from models.candidate import Candidate
from models.job_category import JobCategory

# 延迟初始化 RAG 服务
_rag_service = None

def get_rag_service():
    """延迟获取 RAG 服务实例"""
    global _rag_service
    if _rag_service is None:
        try:
            from agent.rag.rag_service import RagSummarizeService
            _rag_service = RagSummarizeService()
            logger.info("RAG服务初始化成功")
        except Exception as e:
            logger.error(f"RAG服务初始化失败: {str(e)}")
            _rag_service = None
    return _rag_service

user_ids = ["1001", "1002", "1003", "1004", "1005", "1006", "1007", "1008", "1009", "1010",]
month_arr = ["2025-01", "2025-02", "2025-03", "2025-04", "2025-05", "2025-06",
             "2025-07", "2025-08", "2025-09", "2025-10", "2025-11", "2025-12", ]

external_data = {}


@tool(description="从向量存储中检索参考资料")
def rag_summarize(query: str) -> str:
    rag = get_rag_service()
    if rag:
        return rag.rag_summarize(query)
    else:
        return "RAG服务暂不可用"



@tool(description="根据简历ID读取简历文件内容并返回文本")
def read_resume_text(resume_id: int) -> str:
    """从数据库获取简历文件路径，读取并返回文本内容"""
    db = SessionLocal()
    try:
        candidate = db.query(Candidate).filter(Candidate.resume_id == resume_id).first()
        if candidate:
            return f"找到候选人: {candidate.name}，求职意向: {candidate.target_position}"
        return "未找到该简历对应的候选人信息"
    finally:
        db.close()


@tool(description="根据岗位ID获取岗位详细信息（任职要求、职责、类别等）")
def query_job_info(job_id: int) -> str:
    """从数据库查询岗位信息并返回结构化文本"""
    db = SessionLocal()
    try:
        job = db.query(Job).filter(Job.id == job_id).first()
        if job:
            return f"【岗位信息】\n名称：{job.name}\n类别：{job.job_type}\n部门：{job.department}\n薪资：{job.salary}\n地点：{job.location}\n状态：{job.status}\n\n【任职要求】\n{job.requirements}\n\n【岗位职责】\n{job.responsibilities}"
        return f"未找到ID为 {job_id} 的岗位"
    finally:
        db.close()


@tool(description="根据候选人ID获取候选人详细信息（技能、经历、教育等）")
def query_candidate_info(candidate_id: int) -> str:
    """从数据库查询候选人信息并返回结构化文本"""
    db = SessionLocal()
    try:
        candidate = db.query(Candidate).filter(Candidate.id == candidate_id).first()
        if candidate:
            return f"【候选人信息】\n姓名：{candidate.name}\n性别：{candidate.gender}\n年龄：{candidate.age}\n学历：{candidate.education}\n工作年限：{candidate.work_years}年\n求职意向：{candidate.target_position}\n技能：{str(candidate.skills or [])}"
        return f"未找到ID为 {candidate_id} 的候选人"
    finally:
        db.close()


@tool(description="根据岗位类别获取匹配权重配置")
def query_matching_weights(category_code: str) -> str:
    """从数据库查询权重配置并返回JSON"""
    db = SessionLocal()
    try:
        category = db.query(JobCategory).filter(JobCategory.code == category_code).first()
        if category:
            return f"岗位类别: {category.name}\n编码: {category.code}\n描述: {category.description or '无'}"
        return f"未找到类别编码为 {category_code} 的岗位类别"
    finally:
        db.close()


@tool(description="获取所有岗位列表，返回岗位ID、名称、类别、状态等基本信息")
def get_all_jobs() -> str:
    """获取系统中所有岗位的列表"""
    db = SessionLocal()
    try:
        jobs = db.query(Job).all()
        if not jobs:
            return "系统中暂无岗位"
        
        result = "【岗位列表】\n"
        for i, job in enumerate(jobs, 1):
            result += f"{i}. ID: {job.id} | 名称: {job.name} | 类别: {job.job_type} | 部门: {job.department} | 状态: {job.status}\n"
        return result
    finally:
        db.close()


@tool(description="获取所有候选人列表，返回候选人ID、姓名、求职意向等基本信息")
def get_all_candidates() -> str:
    """获取系统中所有候选人的列表"""
    db = SessionLocal()
    try:
        candidates = db.query(Candidate).all()
        if not candidates:
            return "系统中暂无候选人"
        
        result = "【候选人列表】\n"
        for i, candidate in enumerate(candidates, 1):
            result += f"{i}. ID: {candidate.id} | 姓名: {candidate.name} | 年龄: {candidate.age} | 学历: {candidate.education} | 求职意向: {candidate.target_position}\n"
        return result
    finally:
        db.close()


@tool(description="根据技能关键词搜索候选人，返回拥有该技能的候选人列表")
def search_candidates_by_skill(skill: str) -> str:
    """搜索拥有指定技能的候选人"""
    db = SessionLocal()
    try:
        candidates = db.query(Candidate).all()
        matched = []
        
        for candidate in candidates:
            skills = candidate.skills or []
            # 检查技能列表中是否包含关键词（支持模糊匹配）
            if any(skill.lower() in str(s).lower() for s in skills):
                matched.append(candidate)
        
        if not matched:
            return f"未找到拥有 '{skill}' 技能的候选人"
        
        result = f"【拥有 '{skill}' 技能的候选人】\n"
        for i, candidate in enumerate(matched, 1):
            result += f"{i}. ID: {candidate.id} | 姓名: {candidate.name} | 年龄: {candidate.age} | 学历: {candidate.education} | 求职意向: {candidate.target_position}\n"
        return result
    finally:
        db.close()


@tool(description="根据学历筛选候选人，支持大专、本科、硕士、博士等")
def search_candidates_by_education(education: str) -> str:
    """根据学历筛选候选人"""
    db = SessionLocal()
    try:
        candidates = db.query(Candidate).filter(
            Candidate.education.like(f"%{education}%")
        ).all()
        
        if not candidates:
            return f"未找到学历为 '{education}' 的候选人"
        
        result = f"【学历为 '{education}' 的候选人】\n"
        for i, candidate in enumerate(candidates, 1):
            result += f"{i}. ID: {candidate.id} | 姓名: {candidate.name} | 年龄: {candidate.age} | 工作年限: {candidate.work_years}年 | 求职意向: {candidate.target_position}\n"
        return result
    finally:
        db.close()


@tool(description="根据工作年限范围筛选候选人，参数格式如：2-5 表示2到5年经验")
def search_candidates_by_work_years(range_str: str) -> str:
    """根据工作年限范围筛选候选人，参数格式如：2-5"""
    db = SessionLocal()
    try:
        parts = range_str.split('-')
        if len(parts) != 2:
            return "参数格式错误，请使用如：2-5 表示2到5年经验"
        
        min_years = int(parts[0].strip())
        max_years = int(parts[1].strip())
        
        candidates = db.query(Candidate).filter(
            Candidate.work_years >= min_years,
            Candidate.work_years <= max_years
        ).all()
        
        if not candidates:
            return f"未找到工作年限在 {min_years}-{max_years} 年的候选人"
        
        result = f"【工作年限在 {min_years}-{max_years} 年的候选人】\n"
        for i, candidate in enumerate(candidates, 1):
            result += f"{i}. ID: {candidate.id} | 姓名: {candidate.name} | 年龄: {candidate.age} | 工作年限: {candidate.work_years}年 | 求职意向: {candidate.target_position}\n"
        return result
    finally:
        db.close()


@tool(description="获取所有岗位类别列表")
def get_all_job_categories() -> str:
    """获取系统中所有岗位类别的列表"""
    db = SessionLocal()
    try:
        categories = db.query(JobCategory).all()
        if not categories:
            return "系统中暂无岗位类别"
        
        result = "【岗位类别列表】\n"
        for i, cat in enumerate(categories, 1):
            result += f"{i}. 编码: {cat.code} | 名称: {cat.name}\n"
        return result
    finally:
        db.close()


# ==================== 报告统计专用工具 ====================

@tool(description="获取招聘统计数据，包括简历数量、候选人数量、岗位数量、匹配次数等")
def get_recruitment_statistics(start_date: str = "", end_date: str = "") -> str:
    """获取招聘统计数据"""
    from datetime import datetime, timedelta
    db = SessionLocal()
    try:
        # 查询统计数据
        total_jobs = db.query(Job).count()
        active_jobs = db.query(Job).filter(Job.status == 1).count()
        total_candidates = db.query(Candidate).count()
        
        # 根据日期范围筛选（如果有）
        candidates_query = db.query(Candidate)
        if start_date:
            try:
                start = datetime.strptime(start_date, "%Y-%m-%d")
                candidates_query = candidates_query.filter(Candidate.created_at >= start)
            except:
                pass
        if end_date:
            try:
                end = datetime.strptime(end_date, "%Y-%m-%d")
                end = end + timedelta(days=1)  # 包含结束日期
                candidates_query = candidates_query.filter(Candidate.created_at < end)
            except:
                pass
        
        period_candidates = candidates_query.count()
        
        # 统计各学历分布
        education_dist = {}
        all_candidates = db.query(Candidate).all()
        for c in all_candidates:
            edu = c.education or "未知"
            education_dist[edu] = education_dist.get(edu, 0) + 1
        
        # 统计各岗位类别分布
        job_type_dist = {}
        for job in db.query(Job).all():
            jtype = job.job_type or "未知"
            job_type_dist[jtype] = job_type_dist.get(jtype, 0) + 1
        
        # 估算匹配次数（基于候选人数量）
        estimated_matches = total_candidates * 2  # 假设每个候选人平均匹配2个岗位
        
        result = f"""【招聘统计数据】
统计周期: {start_date or '全部时间'} 至 {end_date or '当前'}

岗位统计:
- 总岗位数: {total_jobs}
- 在招岗位数: {active_jobs}

候选人统计:
- 总候选人数: {total_candidates}
- 本期新增候选人: {period_candidates}

学历分布:
{chr(10).join([f"- {edu}: {count}人" for edu, count in education_dist.items()])}

岗位类别分布:
{chr(10).join([f"- {jtype}: {count}个" for jtype, count in job_type_dist.items()])}

匹配统计:
- 预估匹配次数: {estimated_matches}
- 平均匹配分: 待匹配后统计
"""
        return result
    finally:
        db.close()


@tool(description="获取简历解析状态统计")
def get_resume_parse_stats(start_date: str = "", end_date: str = "") -> str:
    """获取简历解析状态统计"""
    from datetime import datetime, timedelta
    db = SessionLocal()
    try:
        # 查询已解析和未解析的简历
        parsed_candidates = db.query(Candidate).filter(Candidate.name.isnot(None)).count()
        total_candidates = db.query(Candidate).count()
        
        # 统计解析率
        parse_rate = (parsed_candidates / total_candidates * 100) if total_candidates > 0 else 0
        
        result = f"""【简历解析统计】
- 总候选人: {total_candidates}
- 已解析简历: {parsed_candidates}
- 未解析简历: {total_candidates - parsed_candidates}
- 解析率: {parse_rate:.1f}%
"""
        return result
    finally:
        db.close()


@tool(description="获取岗位分布统计")
def get_job_distribution_stats() -> str:
    """获取岗位分布统计"""
    db = SessionLocal()
    try:
        jobs = db.query(Job).all()
        
        if not jobs:
            return "系统中暂无岗位"
        
        # 按类别分组
        by_type = {}
        by_department = {}
        by_status = {"招聘中": 0, "已下架": 0}
        
        for job in jobs:
            # 按类别
            jtype = job.job_type or "未分类"
            by_type[jtype] = by_type.get(jtype, 0) + 1
            
            # 按部门
            dept = job.department or "未指定"
            by_department[dept] = by_department.get(dept, 0) + 1
            
            # 按状态
            if job.status == 1:
                by_status["招聘中"] += 1
            else:
                by_status["已下架"] += 1
        
        result = f"""【岗位分布统计】
总岗位数: {len(jobs)}

按类别:
{chr(10).join([f"- {jtype}: {count}个" for jtype, count in by_type.items()])}

按部门:
{chr(10).join([f"- {dept}: {count}个" for dept, count in by_department.items()])}

按状态:
{chr(10).join([f"- {status}: {count}个" for status, count in by_status.items()])}
"""
        return result
    finally:
        db.close()
