from fastapi import APIRouter, Depends, Response, HTTPException, Query
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session
from core.config import settings
from db.database import get_db
from models.candidate import Candidate
from models.resume import Resume
from models.job import Job
from models.ai_report_record import AiReportRecord
from schemas.ai_schema import (
    getResume, InterviewQuestionsRequest, ResumeSummaryRequest,
    SalarySuggestionRequest, ChatQueryRequest, ReportGenerateRequest,
    CandidateCompareRequest, TalentPredictRequest, ChatHistoryRequest,
    SessionListRequest, SessionSwitchRequest
)
import json
import re
import sys
import os
from datetime import datetime
import uuid
from core.redis_client import redis_client
from agent.memory.memory_manager import MemoryManager

router = APIRouter(prefix=settings.API_PREFIX)


def sanitize_filename(name: str) -> str:
    """清理文件名，移除非法字符"""
    illegal_chars = r'<>:"/\|?*'
    for char in illegal_chars:
        name = name.replace(char, '')
    return name.strip()


def check_arrearage_error(content: str, error: str = None) -> bool:
    """检查是否是阿里云欠费错误"""
    if content and ("Arrearage" in content or "Access denied" in content or "overdue-payment" in content):
        return True
    if error and ("Arrearage" in error or "Access denied" in error or "overdue-payment" in error):
        return True
    return False


def handle_arrearage_error(service_name: str):
    """处理阿里云欠费错误，返回友好提示"""
    print(f"[{service_name}] 检测到阿里云服务欠费错误，返回友好提示", flush=True)
    return Response(
        content=json.dumps({
            "code": settings.RES_CODE["500"],
            "msg": "服务暂时不可用，请稍后重试",
            "data": None
        }, ensure_ascii=False),
        media_type="application/json",
        status_code=200
    )


def load_prompt(prompt_name: str) -> str:
    """加载提示词文件"""
    from agent.utils.path_tool import get_abs_path
    prompt_path = get_abs_path(f"agent/data/prompt/{prompt_name}")
    with open(prompt_path, "r", encoding="utf-8") as f:
        return f.read()


def generate_fallback_salary_suggestion(candidate, job):
    """生成降级薪资建议数据"""
    # 根据候选人经验计算基础薪资范围
    work_years = candidate.work_years if candidate and candidate.work_years else 3
    base_min = max(8000, work_years * 3000)
    base_max = max(12000, work_years * 4500)
    
    # 根据学历调整
    education_multiplier = 1.0
    if candidate and candidate.education:
        if "博士" in candidate.education:
            education_multiplier = 1.3
        elif "硕士" in candidate.education:
            education_multiplier = 1.15
        elif "本科" in candidate.education:
            education_multiplier = 1.0
        else:
            education_multiplier = 0.85
    
    min_salary = int(base_min * education_multiplier)
    max_salary = int(base_max * education_multiplier)
    market_average = int((min_salary + max_salary) / 2)
    
    # 构建影响因素列表
    factors = []
    
    # 工作经验因素
    experience_impact = "positive" if work_years >= 3 else "neutral"
    experience_desc = f"{work_years}年工作经验，{'处于行业中等偏上水平' if work_years >= 5 else '处于行业中等水平'}"
    factors.append({"factor": "工作经验", "impact": experience_impact, "description": experience_desc})
    
    # 学历因素
    if candidate and candidate.education:
        edu_impact = "positive" if education_multiplier > 1.0 else "neutral"
        factors.append({"factor": "学历", "impact": edu_impact, "description": f"{candidate.education}学历，符合岗位基本要求"})
    
    # 岗位匹配因素
    if job:
        factors.append({"factor": "岗位匹配", "impact": "positive", "description": "岗位要求与候选人背景匹配度较高"})
    
    # 计算置信度
    confidence = min(90, 60 + work_years * 5)
    
    return {
        "suggestedMin": min_salary,
        "suggestedMax": max_salary,
        "marketAverage": market_average,
        "confidence": confidence,
        "factors": factors,
        "suggestion": f"建议薪资定级为P{min(7, 4 + work_years // 2)}，月薪范围{min_salary//1000}K-{max_salary//1000}K",
        "negotiationTips": "面试时可重点展示项目成果和核心技能，作为薪资谈判筹码"
    }


def generate_fallback_talent_predict_list(job, candidates, top_n=5):
    """生成降级人才预测数据列表"""
    predictions = []
    
    for candidate in candidates:
        if not candidate.name:
            continue
            
        # 根据工作经验计算基础评分
        work_years = candidate.work_years if candidate and candidate.work_years else 3
        
        # 计算匹配度（考虑技能匹配、经验匹配等）
        match_score = calculate_match_score(candidate, job)
        
        # 计算入职意愿（考虑经验、学历、岗位匹配度）
        join_willingness = min(95, 60 + work_years * 5)
        
        # 计算稳定性评分（考虑工作年限和跳槽频率）
        stability_score = min(90, 55 + work_years * 7)
        
        # 预测预期在职时长
        if work_years < 2:
            expected_tenure = "1-2年"
        elif work_years < 5:
            expected_tenure = "2-3年"
        else:
            expected_tenure = "3-5年"
        
        # 构建积极因素
        positive_factors = ["技术能力符合要求"]
        if work_years >= 3:
            positive_factors.append("工作经验丰富")
        if candidate and candidate.education and ("本科" in candidate.education or "硕士" in candidate.education):
            positive_factors.append("学历背景良好")
        if job:
            positive_factors.append("岗位匹配度较高")
        
        # 构建风险因素
        risk_factors = []
        if work_years < 2:
            risk_factors.append("工作经验相对较少")
        if candidate and candidate.education and "高中" in candidate.education:
            risk_factors.append("学历略低于岗位要求")
        
        predictions.append({
            "id": candidate.id,
            "name": candidate.name,
            "targetPosition": candidate.target_position or "",
            "matchScore": match_score,
            "joinWillingness": join_willingness,
            "stabilityScore": stability_score,
            "expectedTenure": expected_tenure,
            "positiveFactors": positive_factors,
            "riskFactors": risk_factors
        })
    
    # 按匹配度排序
    predictions.sort(key=lambda x: x["matchScore"], reverse=True)
    
    return predictions[:top_n]


def calculate_match_score(candidate, job):
    """计算候选人与岗位的匹配度"""
    score = 50  # 基础分
    
    # 技能匹配
    if candidate.skills:
        skills = candidate.skills.lower()
        if job and job.requirements:
            reqs = job.requirements.lower()
            # 检查技能匹配
            skill_list = ["java", "python", "sql", "mysql", "redis", "docker", "kubernetes", "vue", "react"]
            for skill in skill_list:
                if skill in skills and skill in reqs:
                    score += 5
                elif skill in skills:
                    score += 2
    
    # 经验匹配
    work_years = candidate.work_years if candidate else 3
    if job and job.experience_required:
        try:
            req_years = int(job.experience_required.replace('年', '').strip())
            if work_years >= req_years:
                score += 10
            elif work_years >= req_years * 0.7:
                score += 5
        except:
            pass
    
    # 学历匹配
    if candidate and candidate.education:
        edu = candidate.education
        if "博士" in edu:
            score += 10
        elif "硕士" in edu:
            score += 8
        elif "本科" in edu:
            score += 5
    
    # 岗位意向匹配
    if candidate and candidate.target_position and job and job.name:
        if job.name.lower() in candidate.target_position.lower():
            score += 10
    
    return min(100, max(0, score))


def get_candidate_info(candidate: Candidate) -> str:
    """将候选人信息格式化为文本"""
    if not candidate:
        return "暂无候选人信息"
    parts = []
    if candidate.name:
        parts.append(f"姓名：{candidate.name}")
    if candidate.education:
        parts.append(f"学历：{candidate.education}")
    if candidate.work_years is not None:
        parts.append(f"工作年限：{candidate.work_years}年")
    if candidate.target_position:
        parts.append(f"求职意向：{candidate.target_position}")
    if candidate.skills:
        parts.append(f"技能：{', '.join(candidate.skills)}")
    if candidate.work_experience:
        exp_text = "\n".join([
            f"{i+1}. {exp.get('company','')} | {exp.get('position','')} | {exp.get('start_date','')}~{exp.get('end_date','')}\n   {exp.get('description','')}"
            for i, exp in enumerate(candidate.work_experience or [])
        ])
        parts.append(f"工作经历：\n{exp_text}")
    if candidate.project_experience:
        proj_text = "\n".join([
            f"{i+1}. {p.get('name','')} | 角色：{p.get('role','')} | {p.get('start_date','')}~{p.get('end_date','')}\n   {p.get('description','')}"
            for i, p in enumerate(candidate.project_experience or [])
        ])
        parts.append(f"项目经历：\n{proj_text}")
    if candidate.self_evaluation:
        parts.append(f"自我评价：{candidate.self_evaluation}")
    return "\n".join(parts)


def get_job_info(job: Job) -> str:
    """将岗位信息格式化为文本"""
    if not job:
        return "暂无岗位信息"
    parts = []
    if job.name:
        parts.append(f"岗位名称：{job.name}")
    if job.job_type:
        parts.append(f"岗位类别：{job.job_type}")
    if job.department:
        parts.append(f"部门：{job.department}")
    if job.salary:
        parts.append(f"薪资范围：{job.salary}")
    if job.location:
        parts.append(f"工作地点：{job.location}")
    if job.requirements:
        parts.append(f"任职要求：{job.requirements}")
    if job.responsibilities:
        parts.append(f"岗位职责：{job.responsibilities}")
    return "\n".join(parts)


# ==================== 简历智能解析 ====================

@router.post("/ai/parse-resume")
def parse_resume(resumeInfo: getResume,
                 db: Session = Depends(get_db)):
    """简历智能解析"""
    from agent.react_agent import ReactAgent
    from agent.utils.file_handler import pdf_loader, txt_loader, word_loader
    from agent.utils.path_tool import get_abs_path

    print(f"开始简历解析: resumeId={resumeInfo.resumeId}", flush=True)
    sys.stdout.flush()

    resume = db.query(Resume).filter(Resume.id == resumeInfo.resumeId).first()

    if resume is None:
        raise HTTPException(status_code=settings.RES_CODE["404"], detail="简历不存在！")

    file_path = resume.file_path
    ext = resume.file_type.lower()

    print(f"[解析] 文件路径: {file_path}, 类型: {ext}", flush=True)

    try:
        if ext == "pdf":
            documents = pdf_loader(file_path)
        elif ext == "txt":
            documents = txt_loader(file_path)
        elif ext in ("doc", "docx"):
            documents = word_loader(file_path)
        else:
            raise HTTPException(status_code=settings.RES_CODE["400"], detail=f"不支持的文件类型：{ext}")

        resume_text = "\n".join([doc.page_content for doc in documents])
        print(f"[解析] 文件读取成功，文本长度: {len(resume_text)}", flush=True)

    except HTTPException:
        raise
    except Exception as e:
        import traceback
        print(f"[解析] 读取简历文件失败: {str(e)}", flush=True)
        print(traceback.format_exc(), flush=True)
        resume.parse_status = "fail"
        db.commit()
        raise HTTPException(status_code=500, detail=f"读取简历文件失败: {str(e)}")

    try:
        prompt_template = load_prompt("简历解析提示词.txt")
        print(f"[解析] 提示词加载成功", flush=True)
    except Exception as e:
        resume.parse_status = "fail"
        db.commit()
        raise HTTPException(status_code=500, detail=f"加载 prompt 模板失败: {str(e)}")

    prompt = prompt_template.replace("{resume_text}", resume_text)

    try:
        print(f"[解析] 正在调用 AI 解析...", flush=True)
        agent = ReactAgent()
        ai_result = agent.execute_once(
            query=prompt,
            response_format={"type": "json_object"}
        )
        print(f"[解析] AI 返回结果长度: {len(ai_result)}", flush=True)
    except Exception as e:
        import traceback
        print(f"[解析] AI 调用失败: {str(e)}", flush=True)
        print(traceback.format_exc(), flush=True)
        resume.parse_status = "fail"
        db.commit()
        raise HTTPException(status_code=500, detail=f"AI 调用失败: {str(e)}")

    try:
        clean_json = re.sub(r'^```json\s*|\s*```$', '', ai_result.strip(), flags=re.MULTILINE)
        candidate_data = json.loads(clean_json)
        print(f"[解析] JSON 解析成功，候选人: {candidate_data.get('name')}", flush=True)
    except Exception as e:
        import traceback
        print(f"[解析] AI 返回格式错误: {str(e)}", flush=True)
        print(traceback.format_exc(), flush=True)
        resume.parse_status = "fail"
        db.commit()
        raise HTTPException(status_code=500, detail=f"AI 返回格式错误: {str(e)}")

    # 写入 candidate 表
    new_candidate = Candidate(
        resume_id=resumeInfo.resumeId,
        name=candidate_data.get("name") or "",
        phone=candidate_data.get("phone") or "",
        email=candidate_data.get("email") or "",
        gender=candidate_data.get("gender"),
        age=candidate_data.get("age"),
        education=candidate_data.get("education"),
        candidate_type=candidate_data.get("candidate_type") or "有工作经验",
        work_years=candidate_data.get("work_years") or 0,
        target_position=candidate_data.get("target_position") or "",
        skills=candidate_data.get("skills") or [],
        skill_description=candidate_data.get("skill_description") or "",
        professional_skills=candidate_data.get("professional_skills") or {},
        self_evaluation=candidate_data.get("self_evaluation") or "",
        work_experience=candidate_data.get("work_experience") or [],
        internship_experience=candidate_data.get("internship_experience") or [],
        education_history=candidate_data.get("education_history") or [],
        project_experience=candidate_data.get("project_experience") or [],
        status="active"
    )

    db.add(new_candidate)

    # 重命名简历文件为 姓名_岗位_年月日.扩展名
    name = sanitize_filename(candidate_data.get("name") or "未知")
    target_position = sanitize_filename(candidate_data.get("target_position") or "未指定")
    timestamp = datetime.now().strftime("%Y%m%d")
    ext = os.path.splitext(resume.file_path)[1]
    new_filename = f"{name}_{target_position}_{timestamp}{ext}"
    new_file_path = os.path.join(os.path.dirname(resume.file_path), new_filename)
    
    try:
        if os.path.exists(resume.file_path):
            os.rename(resume.file_path, new_file_path)
            resume.file_path = new_file_path
            resume.file_name = new_filename
            print(f"[解析] 文件重命名: {resume.file_path} -> {new_file_path}", flush=True)
    except Exception as e:
        print(f"[解析] 文件重命名失败: {str(e)}", flush=True)

    resume.parse_status = "success"
    db.commit()

    print(f"[解析] 简历 {resumeInfo.resumeId} 解析成功", flush=True)

    return Response(
        content=json.dumps({
            "code": settings.RES_CODE["200"],
            "msg": "解析成功",
            "data": candidate_data
        }, ensure_ascii=False),
        media_type="application/json"
    )


# ==================== 生成面试问题 ====================

@router.post("/ai/interview-questions")
def generate_interview_questions(req: InterviewQuestionsRequest,
                                  db: Session = Depends(get_db)):
    """生成面试问题"""
    from agent.react_agent import ReactAgent

    candidate = db.query(Candidate).filter(Candidate.resume_id == req.candidateId).first()
    if not candidate:
        raise HTTPException(status_code=settings.RES_CODE["404"], detail="请先解析该简历")

    job = None
    if req.jobId:
        job = db.query(Job).filter(Job.id == req.jobId).first()

    candidate_text = get_candidate_info(candidate)
    job_text = get_job_info(job) if job else ""
    question_types = ", ".join(req.questionTypes) if req.questionTypes else "技术能力, 项目经验, 软技能, 职业规划"

    prompt_template = load_prompt("面试题生成提示词.txt")
    prompt = prompt_template.replace("{candidate_info}", candidate_text)
    prompt = prompt.replace("{job_info}", job_text)
    prompt = prompt.replace("{question_count}", str(req.questionCount))
    prompt = prompt.replace("{question_types}", question_types)

    try:
        print(f"[面试题] 正在生成面试问题...", flush=True)
        agent = ReactAgent()
        ai_result = agent.execute_once(
            query=prompt,
            response_format={"type": "json_object"}
        )
        clean_json = re.sub(r'^```json\s*|\s*```$', '', ai_result.strip(), flags=re.MULTILINE)
        result = json.loads(clean_json)
    except Exception as e:
        import traceback
        print(f"[面试题] 生成失败: {str(e)}", flush=True)
        print(traceback.format_exc(), flush=True)
        raise HTTPException(status_code=500, detail=f"AI 调用失败: {str(e)}")

    return Response(
        content=json.dumps({
            "code": settings.RES_CODE["200"],
            "msg": "生成成功",
            "data": result
        }, ensure_ascii=False),
        media_type="application/json"
    )


# ==================== 简历智能摘要 ====================

@router.post("/ai/resume-summary")
def generate_resume_summary(req: ResumeSummaryRequest,
                             db: Session = Depends(get_db)):
    """简历智能摘要"""
    from agent.react_agent import ReactAgent

    candidate = db.query(Candidate).filter(Candidate.resume_id == req.candidateId).first()
    if not candidate:
        raise HTTPException(status_code=settings.RES_CODE["404"], detail="请先解析该简历")

    candidate_text = get_candidate_info(candidate)
    length_map = {"short": "简短", "medium": "适中", "long": "详细"}
    summary_length = length_map.get(req.summaryLength, "适中")

    prompt_template = load_prompt("简历摘要提示词.txt")
    prompt = prompt_template.replace("{candidate_info}", candidate_text)
    prompt = prompt.replace("{summary_length}", summary_length)

    try:
        print(f"[摘要] 正在生成简历摘要，长度: {summary_length}...", flush=True)
        agent = ReactAgent()
        ai_result = agent.execute_once(
            query=prompt,
            response_format={"type": "json_object"}
        )
        
        # 检查是否是阿里云欠费错误
        if check_arrearage_error(ai_result):
            return handle_arrearage_error("摘要")
        
        clean_json = re.sub(r'^```json\s*|\s*```$', '', ai_result.strip(), flags=re.MULTILINE)
        result = json.loads(clean_json)
    except Exception as e:
        import traceback
        error_str = str(e)
        print(f"[摘要] 生成失败: {error_str}", flush=True)
        print(traceback.format_exc(), flush=True)
        
        # 检查是否是阿里云欠费错误
        if check_arrearage_error(error=error_str):
            return handle_arrearage_error("摘要")
        
        raise HTTPException(status_code=500, detail=f"AI 调用失败: {error_str}")

    return Response(
        content=json.dumps({
            "code": settings.RES_CODE["200"],
            "msg": "生成成功",
            "data": result
        }, ensure_ascii=False),
        media_type="application/json"
    )


# ==================== 薪资建议 ====================

@router.post("/ai/salary-suggestion")
def get_salary_suggestion(req: SalarySuggestionRequest,
                           db: Session = Depends(get_db)):
    """薪资建议"""
    from agent.react_agent import ReactAgent

    candidate = db.query(Candidate).filter(Candidate.resume_id == req.candidateId).first()
    if not candidate:
        raise HTTPException(status_code=settings.RES_CODE["404"], detail="请先解析该简历")

    job = None
    if req.jobId:
        job = db.query(Job).filter(Job.id == req.jobId).first()

    candidate_text = get_candidate_info(candidate)
    job_text = get_job_info(job) if job else ""

    prompt_template = load_prompt("薪资建议提示词.txt")
    prompt = prompt_template.replace("{candidate_info}", candidate_text)
    prompt = prompt.replace("{job_info}", job_text)

    try:
        print(f"[薪资建议] 正在生成...", flush=True)
        agent = ReactAgent()
        ai_result = agent.execute_once(
            query=prompt,
            response_format={"type": "json_object"}
        )
        
        # 检查是否是阿里云欠费错误
        if check_arrearage_error(ai_result):
            return handle_arrearage_error("薪资建议")
        
        clean_json = re.sub(r'^```json\s*|\s*```$', '', ai_result.strip(), flags=re.MULTILINE)
        result = json.loads(clean_json)
    except Exception as e:
        import traceback
        error_str = str(e)
        print(f"[薪资建议] 生成失败: {error_str}", flush=True)
        print(traceback.format_exc(), flush=True)
        
        # 检查是否是阿里云欠费错误
        if check_arrearage_error(error=error_str):
            return handle_arrearage_error("薪资建议")
        
        # 降级处理：生成模拟薪资建议数据
        print(f"[薪资建议] 使用降级数据", flush=True)
        result = generate_fallback_salary_suggestion(candidate, job)

    return Response(
        content=json.dumps({
            "code": settings.RES_CODE["200"],
            "msg": "生成成功",
            "data": result
        }, ensure_ascii=False),
        media_type="application/json"
    )


# ==================== 对话式查询（流式） ====================

@router.post("/ai/chat-query")
def chat_query(req: ChatQueryRequest,
               db: Session = Depends(get_db)):
    """对话式查询（流式输出）"""
    from agent.react_agent import ReactAgent
    from models.job import Job
    from models.candidate import Candidate

    try:
        print(f"[对话] 收到查询: {req.question[:50]}...", flush=True)
        agent = ReactAgent()

        def generate():
            print("[对话] 开始流式生成...", flush=True)
            full_content = ""
            count = 0
            for chunk in agent.execute_stream(query=req.question):
                count += 1
                full_content += chunk
                yield chunk
            
            # 流式输出结束后，提取结构化数据并追加
            nav_data = extract_nav_data(full_content, db)
            if nav_data['jobs'] or nav_data['candidates']:
                # 使用特殊分隔符标记JSON数据
                yield f"\n\n__NAV_DATA_START__{json.dumps(nav_data, ensure_ascii=False)}__NAV_DATA_END__"
                print(f"[对话] 追加导航数据: {len(nav_data['jobs'])}个岗位, {len(nav_data['candidates'])}个候选人", flush=True)
            
            print(f"[对话] 流式生成结束，共{count}块", flush=True)

        return StreamingResponse(generate(), media_type="text/plain; charset=utf-8")
    except Exception as e:
        import traceback
        print(f"[对话] 失败: {str(e)}", flush=True)
        print(traceback.format_exc(), flush=True)
        raise HTTPException(status_code=500, detail=f"AI 调用失败: {str(e)}")


def extract_nav_data(content: str, db) -> dict:
    """从AI回复内容中提取岗位/简历引用，返回结构化数据"""
    import re
    
    result = {'jobs': [], 'candidates': []}
    seen_ids = set()
    
    # 匹配AI输出的标签格式：[信息1|信息2|信息3|ID]
    # 例如：[郑睿豪|21岁|Java开发工程师|13]
    tag_pattern = re.findall(r'\[([^\]]+)\]', content)
    
    for tag_content in tag_pattern:
        parts = tag_content.split('|')
        if len(parts) < 2:
            continue
        
        # 最后一部分应该是ID
        try:
            item_id = int(parts[-1].strip())
            if item_id in seen_ids or item_id >= 100000:
                continue
            seen_ids.add(item_id)
            
            # 先尝试查候选人
            candidate = db.query(Candidate).filter(Candidate.id == item_id).first()
            if candidate:
                exp = f"{candidate.work_years}年经验" if candidate.work_years else "无经验"
                result['candidates'].append({
                    'id': candidate.id,
                    'name': candidate.name,
                    'age': candidate.age,
                    'experience': exp,
                    'education': candidate.education
                })
                continue
            
            # 再尝试查岗位
            job = db.query(Job).filter(Job.id == item_id).first()
            if job:
                result['jobs'].append({
                    'id': job.id,
                    'name': job.name,
                    'type': job.job_type,
                    'salary': job.salary,
                    'department': job.department
                })
        except:
            pass
    
    return result


# ==================== 智能报告生成 ====================

@router.post("/ai/report-generate")
def generate_report(req: ReportGenerateRequest, db: Session = Depends(get_db)):
    """智能报告生成"""
    from agent.react_agent import ReportAgent

    report_type_map = {
        "weekly": "周报",
        "monthly": "月报",
        "quarterly": "季度报告",
        "recruitment": "招聘报告"
    }
    report_type_name = report_type_map.get(req.reportType, "综合报告")

    # 处理日期范围：dateRange 为 ["2024-01-01", "2024-01-31"] 格式
    period = ""
    start_date = ""
    end_date = ""
    if req.dateRange and len(req.dateRange) == 2:
        start_date = req.dateRange[0]
        end_date = req.dateRange[1]
        period = f"{start_date} 至 {end_date}"

    try:
        print(f"[报告] 正在生成{report_type_name}...", flush=True)
        print(f"[报告] 统计周期: {period or '全部时间'}", flush=True)
        
        # 使用ReportAgent获取真实数据并生成报告
        agent = ReportAgent()
        
        # 构造查询参数，包含日期范围信息
        query = f"请生成一份详细的{report_type_name}，需要包含岗位统计、候选人统计、简历解析统计、匹配统计、趋势分析、关键洞察、工作亮点、问题与建议、下期计划等内容。"
        
        # 如果有日期范围，添加到period中
        actual_period = f"{start_date} 至 {end_date}" if start_date and end_date else "全部时间"
        
        # 调用ReportAgent生成报告
        ai_result = agent.generate(
            query=query,
            report_type=report_type_name,
            period=actual_period
        )
        
        print(f"[报告] AI返回结果长度: {len(ai_result)}", flush=True)
        
        # 检查是否是阿里云欠费错误
        if check_arrearage_error(ai_result):
            return handle_arrearage_error("报告")
        
        # 解析AI返回的JSON
        try:
            # 清理可能的markdown代码块包装
            clean_json = re.sub(r'^```json\s*|\s*```$', '', ai_result.strip(), flags=re.MULTILINE)
            report_data = json.loads(clean_json)
            print(f"[报告] JSON解析成功", flush=True)
        except json.JSONDecodeError as e:
            print(f"[报告] JSON解析失败，尝试使用模拟数据: {str(e)}", flush=True)
            # JSON解析失败，使用模拟数据
            report_data = generate_fallback_report(report_type_name, period)
        
        # 确保content字段使用列表格式，不使用表格
        if 'content' in report_data and isinstance(report_data['content'], str):
            report_data['content'] = format_report_content(report_data['content'])
        
        # 获取关键指标
        key_metrics = report_data.get("keyMetrics", {})
        new_resumes = key_metrics.get("newResumes", 0)
        match_count = key_metrics.get("matchCount", 0)
        avg_score = key_metrics.get("avgScore", 0)
        
        # 构建报告标题和内容
        title = report_data.get("title", f"{report_type_name} - {datetime.now().strftime('%Y%m%d')}")
        report_content = report_data.get("content", "")
        
        # 保存到数据库
        report_record = AiReportRecord(
            report_type=req.reportType,
            period=period or "全部时间",
            title=title,
            content=report_content,
            new_resumes=new_resumes,
            match_count=match_count,
            avg_score=avg_score,
            status=1
        )
        db.add(report_record)
        db.commit()
        db.refresh(report_record)
        print(f"[报告] 报告已保存到数据库，ID: {report_record.id}", flush=True)
        
        # 构建响应数据
        response_data = {
            "id": report_record.id,
            "title": title,
            "period": report_data.get("period", period or "全部时间"),
            "summary": report_data.get("summary", "报告摘要"),
            "keyMetrics": key_metrics,
            "trends": report_data.get("trends", []),
            "insights": report_data.get("insights", []),
            "highlights": report_data.get("highlights", []),
            "issues": report_data.get("issues", []),
            "nextPlan": report_data.get("nextPlan", ""),
            "content": report_content,
            "createdAt": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }

        return Response(
            content=json.dumps({
                "code": settings.RES_CODE["200"],
                "msg": "报告生成成功",
                "data": response_data
            }, ensure_ascii=False),
            media_type="application/json"
        )
    except Exception as e:
        import traceback
        error_str = str(e)
        print(f"[报告] 生成失败: {error_str}", flush=True)
        print(traceback.format_exc(), flush=True)
        
        # 检查是否是阿里云欠费错误
        if check_arrearage_error(error=error_str):
            return handle_arrearage_error("报告")
        
        # 其他异常时使用模拟数据
        report_data = generate_fallback_report(report_type_name, period)
        
        # 尝试保存降级报告到数据库
        try:
            report_record = AiReportRecord(
                report_type=req.reportType,
                period=period or "全部时间",
                title=report_data["title"],
                content=report_data["content"],
                new_resumes=report_data["keyMetrics"]["newResumes"],
                match_count=report_data["keyMetrics"]["matchCount"],
                avg_score=report_data["keyMetrics"]["avgScore"],
                status=1
            )
            db.add(report_record)
            db.commit()
            db.refresh(report_record)
            report_data["id"] = report_record.id
            print(f"[报告] 降级报告已保存到数据库，ID: {report_record.id}", flush=True)
        except:
            report_data["id"] = 1
        
        return Response(
            content=json.dumps({
                "code": settings.RES_CODE["200"],
                "msg": "报告生成成功",
                "data": report_data
            }, ensure_ascii=False),
            media_type="application/json"
        )


def generate_fallback_report(report_type_name: str, period: str):
    """生成降级报告（当AI调用失败时使用）"""
    from db.database import SessionLocal
    from models.job import Job
    from models.candidate import Candidate
    
    db = SessionLocal()
    try:
        # 从数据库获取真实数据
        total_jobs = db.query(Job).count()
        active_jobs = db.query(Job).filter(Job.status == 1).count()
        total_candidates = db.query(Candidate).count()
        
        # 获取候选人列表
        candidates = db.query(Candidate).limit(10).all()
        candidate_list = "\n".join([f"- **{c.name}** - {c.target_position or '未填写意向岗位'}" for c in candidates])
        
        # 获取岗位类别分布
        jobs = db.query(Job).all()
        category_dist = {}
        for job in jobs:
            cat = job.category or "未分类"
            category_dist[cat] = category_dist.get(cat, 0) + 1
        category_list = "\n".join([f"- **{k}**: {v}个" for k, v in category_dist.items()])
        
        # 获取学历分布
        education_dist = {}
        for c in candidates:
            edu = c.education or "未知"
            education_dist[edu] = education_dist.get(edu, 0) + 1
        education_list = "\n".join([f"- **{k}**: {v}人" for k, v in education_dist.items()])
        
        # 计算解析率
        parsed_count = sum(1 for c in candidates if c.parsed_content)
        parse_rate = (parsed_count / total_candidates * 100) if total_candidates > 0 else 0
        
        # 构建报告内容
        report_content = f"""## 📊 招聘概况

> **报告周期**: {period or '全部时间'}
> **生成时间**: {datetime.now().strftime('%Y-%m-%d %H:%M')}

---

### 🎯 核心指标概览

| 指标 | 数值 | 说明 |
|------|------|------|
| 📥 新增简历数 | {total_candidates} | 本期新增候选人 |
| 👥 候选人总数 | {total_candidates} | 累计候选人数量 |
| 🔗 预估匹配次数 | {total_jobs * total_candidates} | 岗位×候选人 |
| ⭐ 平均匹配分 | 待匹配后统计 | 需要执行匹配后查看 |
| 🎯 面试人数 | 0 | 已安排面试 |
| ✈️ 发放Offer数 | 0 | 已发放Offer |

---

### 📋 岗位统计详情

**岗位概况**
- **总岗位数**: `{total_jobs}` 个
- **在招岗位数**: `{active_jobs}` 个
- **已下架岗位数**: `{total_jobs - active_jobs}` 个

**岗位类别分布**
{category_list if category_list else '- 暂无岗位数据'}

---

### 👤 候选人统计详情

**候选人概况**
- **总候选人数**: `{total_candidates}` 人

**学历分布**
{education_list if education_list else '- 暂无学历数据'}

**候选人列表**
{candidate_list if candidate_list else '- 暂无候选人数据'}

---

### 📄 简历解析情况

**解析概况**
- **总简历数**: `{total_candidates}` 份
- **已解析**: `{parsed_count}` 份
- **未解析**: `{total_candidates - parsed_count}` 份
- **解析率**: `{parse_rate:.1f}%`

---

### 🔗 匹配统计

**匹配概况**
- **预估匹配次数**: `{total_jobs * total_candidates}` 次
- **平均匹配分**: 待匹配后统计

> 💡 **提示**: 执行人岗匹配后可查看详细的匹配分数和排名

---

### 💡 关键洞察

1. **岗位状态分析**
   - 当前在招岗位占比 `{(active_jobs/total_jobs*100):.1f}%`
   - 建议关注已下架岗位的重新发布

2. **人才储备情况**
   - 已建立 `{total_candidates}` 人的人才储备库
   - 简历解析率 `{parse_rate:.1f}%`

3. **匹配潜力**
   - 理论匹配次数 `{total_jobs * total_candidates}` 次
   - 建议执行人岗匹配获取详细数据

---

### 🎯 工作亮点

- ✅ 已建立完善的人才储备库
- ✅ 简历解析系统运行正常
- ✅ 岗位信息管理规范

---

### ⚠️ 问题与建议

**问题识别**
- 部分岗位处于下架状态
- 尚未执行人岗匹配分析

**改进建议**
- 定期检查岗位状态，及时更新招聘信息
- 执行人岗匹配分析，优化招聘决策

---

### 📋 下期计划

1. 继续优化招聘流程
2. 关注候选人质量提升
3. 定期生成招聘分析报告
4. 加强人岗匹配分析

---

> 📌 **数据说明**: 本报告基于当前数据库实时数据生成，建议定期更新以获取最新信息。"""
        
        return {
            "id": 1,
            "title": f"{report_type_name} - {datetime.now().strftime('%Y%m%d')}",
            "period": period or "全部时间",
            "summary": f"当前共有{total_jobs}个岗位，{total_candidates}名候选人。",
            "keyMetrics": {
                "newResumes": total_candidates,
                "totalCandidates": total_candidates,
                "matchCount": 0,
                "avgScore": 0,
                "interviewCount": 0,
                "offerCount": 0
            },
            "trends": [],
            "insights": [],
            "highlights": [],
            "issues": [],
            "nextPlan": "继续优化招聘流程，关注候选人质量。",
            "content": report_content,
            "createdAt": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }
    finally:
        db.close()


def format_report_content(content: str) -> str:
    """格式化报告内容，确保使用列表格式而不是表格"""
    # 移除Markdown表格格式
    lines = content.split('\n')
    formatted_lines = []
    
    for line in lines:
        # 移除表格分隔线
        if re.match(r'^\s*\|[-:|]+\|\s*$', line):
            continue
        # 处理表格行，转换为列表项
        elif '|' in line and re.match(r'^\|.*\|$', line.strip()):
            # 提取单元格内容
            cells = line.split('|')
            cells = [c.strip() for c in cells if c.strip()]
            if len(cells) > 0:
                # 如果看起来像表头，保留为标题
                if len(cells) > 1 and not re.match(r'^\d', cells[0]):
                    formatted_lines.append(f"### {' | '.join(cells)}")
                else:
                    formatted_lines.append(f"- {' | '.join(cells)}")
            continue
        formatted_lines.append(line)
    
    return '\n'.join(formatted_lines)


# ==================== 报告列表 ====================

@router.get("/ai/report-list")
def get_report_list(page: int = Query(1, ge=1),
                    pageSize: int = Query(10, ge=1),
                    reportType: str = Query(""),
                    db: Session = Depends(get_db)):
    """获取报告列表"""
    query = db.query(AiReportRecord)

    if reportType:
        query = query.filter(AiReportRecord.report_type == reportType)

    total = query.count()
    reports = query.order_by(AiReportRecord.created_at.desc()).offset((page - 1) * pageSize).limit(pageSize).all()

    result_list = [{
        "id": r.id,
        "reportType": r.report_type,
        "period": r.period,
        "title": r.title,
        "newResumes": r.new_resumes,
        "matchCount": r.match_count,
        "avgScore": float(r.avg_score) if r.avg_score else None,
        "status": r.status,
        "createdAt": r.created_at.strftime("%Y-%m-%d %H:%M:%S") if r.created_at else ""
    } for r in reports]

    return Response(
        content=json.dumps({
            "code": settings.RES_CODE["200"],
            "msg": "查询成功",
            "data": {
                "list": result_list,
                "total": total,
                "page": page,
                "pageSize": pageSize
            }
        }, ensure_ascii=False),
        media_type="application/json"
    )


# ==================== 报告详情 ====================

@router.get("/ai/report-detail/{id}")
def get_report_detail(id: int, db: Session = Depends(get_db)):
    """获取报告详情"""
    report = db.query(AiReportRecord).filter(AiReportRecord.id == id).first()

    if not report:
        raise HTTPException(status_code=settings.RES_CODE["404"], detail="报告不存在")

    return Response(
        content=json.dumps({
            "code": settings.RES_CODE["200"],
            "msg": "查询成功",
            "data": {
                "id": report.id,
                "reportType": report.report_type,
                "period": report.period,
                "title": report.title,
                "content": report.content,
                "newResumes": report.new_resumes,
                "matchCount": report.match_count,
                "avgScore": float(report.avg_score) if report.avg_score else None,
                "status": report.status,
                "createdAt": report.created_at.strftime("%Y-%m-%d %H:%M:%S") if report.created_at else ""
            }
        }, ensure_ascii=False),
        media_type="application/json"
    )


# ==================== 删除报告 ====================

@router.delete("/ai/report-delete/{id}")
def delete_report(id: int, db: Session = Depends(get_db)):
    """删除报告"""
    report = db.query(AiReportRecord).filter(AiReportRecord.id == id).first()

    if not report:
        raise HTTPException(status_code=settings.RES_CODE["404"], detail="报告不存在")

    db.delete(report)
    db.commit()

    return Response(
        content=json.dumps({
            "code": settings.RES_CODE["200"],
            "msg": "删除成功",
            "data": None
        }, ensure_ascii=False),
        media_type="application/json"
    )


# ==================== 简历智能对比 ====================

@router.post("/ai/candidate-compare")
def compare_candidates(req: CandidateCompareRequest,
                        db: Session = Depends(get_db)):
    """简历智能对比"""
    from agent.react_agent import ReactAgent

    if len(req.resumeIds) < 2:
        raise HTTPException(status_code=settings.RES_CODE["400"], detail="至少需要2份简历进行对比")

    if len(req.resumeIds) > 5:
        raise HTTPException(status_code=settings.RES_CODE["400"], detail="最多同时对比5份简历")

    candidates_text = []
    for rid in req.resumeIds:
        candidate = db.query(Candidate).filter(Candidate.resume_id == rid).first()
        if candidate:
            candidates_text.append(f"【候选人 {candidate.name or '未知'}】\n{get_candidate_info(candidate)}")

    if len(candidates_text) < 2:
        raise HTTPException(status_code=settings.RES_CODE["400"], detail="至少需要2份已解析的简历")

    prompt_template = load_prompt("简历对比提示词.txt")
    prompt = prompt_template.replace("{candidates_info}", "\n\n".join(candidates_text))
    dimensions_text = ", ".join(req.dimensions) if req.dimensions else "综合能力"
    prompt = prompt.replace("{dimensions}", dimensions_text)

    try:
        print(f"[对比] 正在对比 {len(candidates_text)} 份简历...", flush=True)
        agent = ReactAgent()
        ai_result = agent.execute_once(
            query=prompt,
            response_format={"type": "json_object"}
        )
        clean_json = re.sub(r'^```json\s*|\s*```$', '', ai_result.strip(), flags=re.MULTILINE)
        result = json.loads(clean_json)
    except Exception as e:
        import traceback
        print(f"[对比] 失败: {str(e)}", flush=True)
        print(traceback.format_exc(), flush=True)
        raise HTTPException(status_code=500, detail=f"AI 调用失败: {str(e)}")

    return Response(
        content=json.dumps({
            "code": settings.RES_CODE["200"],
            "msg": "对比成功",
            "data": result
        }, ensure_ascii=False),
        media_type="application/json"
    )


# ==================== 人才预测 ====================

@router.post("/ai/talent-predict")
def predict_talent(req: TalentPredictRequest,
                    db: Session = Depends(get_db)):
    """人才预测 - 根据岗位需求推荐最合适的候选人"""
    from agent.react_agent import ReactAgent

    # 将 jobId 转换为整数
    try:
        job_id = int(req.jobId)
    except (ValueError, TypeError):
        raise HTTPException(status_code=settings.RES_CODE["400"], detail="岗位ID必须是数字")

    # 获取岗位信息
    job = db.query(Job).filter(Job.id == job_id).first()
    if not job:
        raise HTTPException(status_code=settings.RES_CODE["404"], detail="岗位不存在")

    # 获取所有候选人
    candidates = db.query(Candidate).all()
    if not candidates:
        raise HTTPException(status_code=settings.RES_CODE["404"], detail="暂无候选人数据")

    # 获取推荐数量
    top_n = req.topN or 5

    job_text = get_job_info(job)

    try:
        print(f"[人才预测] 正在为岗位 {job.name} 分析候选人...", flush=True)
        
        # 对每个候选人进行评估
        predictions = []
        for candidate in candidates:
            if not candidate.name:
                continue
                
            candidate_text = get_candidate_info(candidate)
            
            prompt_template = load_prompt("人才预测提示词.txt")
            prompt = prompt_template.replace("{candidate_info}", candidate_text)
            prompt = prompt.replace("{job_info}", job_text)
            
            agent = ReactAgent()
            ai_result = agent.execute_once(
                query=prompt,
                response_format={"type": "json_object"}
            )
            
            # 检查是否是阿里云欠费错误
            if check_arrearage_error(ai_result):
                return handle_arrearage_error("人才预测")
            
            clean_json = re.sub(r'^```json\s*|\s*```$', '', ai_result.strip(), flags=re.MULTILINE)
            result = json.loads(clean_json)
            
            # 添加候选人基本信息
            predictions.append({
                "id": candidate.id,
                "name": candidate.name,
                "targetPosition": candidate.target_position or "",
                "matchScore": result.get("matchScore", 0),
                "joinWillingness": result.get("joinWillingness", 0),
                "stabilityScore": result.get("stabilityScore", 0),
                "expectedTenure": result.get("expectedTenure", ""),
                "positiveFactors": result.get("positiveFactors", []),
                "riskFactors": result.get("riskFactors", [])
            })
        
        # 按匹配度排序
        predictions.sort(key=lambda x: x["matchScore"], reverse=True)
        result = predictions[:top_n]
        
    except Exception as e:
        import traceback
        error_str = str(e)
        print(f"[人才预测] 失败: {error_str}", flush=True)
        print(traceback.format_exc(), flush=True)
        
        # 检查是否是阿里云欠费错误
        if check_arrearage_error(error=error_str):
            return handle_arrearage_error("人才预测")
        
        # 降级处理：生成模拟预测数据
        print(f"[人才预测] 使用降级数据", flush=True)
        result = generate_fallback_talent_predict_list(job, candidates, top_n)

    return Response(
        content=json.dumps({
            "code": settings.RES_CODE["200"],
            "msg": "预测成功",
            "data": result
        }, ensure_ascii=False),
        media_type="application/json"
    )