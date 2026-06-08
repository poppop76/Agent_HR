from langchain.agents import create_agent
from agent.model.factory import chat_model
from agent.utils.prompt_loader import load_system_prompts
from agent.tools.agent_tools import (rag_summarize, read_resume_text, query_job_info, query_candidate_info, query_matching_weights,
                                     get_all_jobs, get_all_candidates, search_candidates_by_skill, search_candidates_by_education,
                                     search_candidates_by_work_years, get_all_job_categories,
                                     get_recruitment_statistics, get_resume_parse_stats, get_job_distribution_stats)
from agent.tools.middleware import monitor_tool, log_before_model, report_prompt_switch


# 报告生成专用的系统提示词
REPORT_SYSTEM_PROMPT = """你是一个专业的HR数据分析专家，擅长生成结构清晰、数据翔实的招聘分析报告。

你的职责：
1. 根据用户需求生成专业的招聘报告
2. 必须使用提供的工具获取真实数据
3. 报告内容必须基于真实数据，不得虚构
4. 输出格式必须严格符合要求的JSON结构

重要：每次生成报告前，必须先调用相关工具获取统计数据！
"""

# 报告生成专用的工具列表
REPORT_TOOLS = [
    get_recruitment_statistics,
    get_resume_parse_stats,
    get_job_distribution_stats,
    get_all_jobs,
    get_all_candidates,
    get_all_job_categories,
]


class ReportAgent:
    """报告生成专用Agent"""
    
    def __init__(self):
        self.agent = create_agent(
            model=chat_model,
            system_prompt=REPORT_SYSTEM_PROMPT,
            tools=REPORT_TOOLS,
            middleware=[monitor_tool, log_before_model],
        )
    
    def _extract_content_from_response(self, response):
        """
        从响应中提取内容，处理多种响应格式
        """
        import json
        
        # 处理字典格式 {'messages': [...]}
        if isinstance(response, dict) and 'messages' in response:
            messages = response['messages']
            print(f"[ReportAgent] 消息数量: {len(messages)}", flush=True)
            
            if messages:
                last_msg = messages[-1]
                return self._extract_content_from_message(last_msg)
        
        # 处理对象格式 response.messages
        if hasattr(response, 'messages'):
            messages = response.messages
            print(f"[ReportAgent] 消息数量: {len(messages)}", flush=True)
            
            if messages:
                last_msg = messages[-1]
                return self._extract_content_from_message(last_msg)
        
        # 处理工具调用响应（可能在thought中）
        if isinstance(response, dict) and 'thought' in response:
            thought = response['thought']
            print(f"[ReportAgent] 发现thought字段", flush=True)
            if isinstance(thought, dict) and 'content' in thought:
                return self._clean_json_content(thought['content'])
            elif isinstance(thought, str):
                return self._clean_json_content(thought)
        
        # 处理工具调用格式 {'tool_calls': [...]}
        if isinstance(response, dict) and 'tool_calls' in response:
            print(f"[ReportAgent] 发现tool_calls字段，跳过工具调用", flush=True)
            # 如果只有工具调用，返回空结果让Agent继续
            return None
        
        # 如果响应本身是字符串
        if isinstance(response, str):
            print(f"[ReportAgent] 响应本身是字符串，长度: {len(response)}", flush=True)
            return self._clean_json_content(response)
        
        # 如果响应是字典，检查是否有content字段
        if isinstance(response, dict):
            if 'content' in response:
                return self._clean_json_content(response['content'])
            # 返回整个字典的JSON
            result = json.dumps(response, ensure_ascii=False)
            print(f"[ReportAgent] 响应是字典，转换为JSON，长度: {len(result)}", flush=True)
            return result
        
        # 最后尝试转换为字符串
        result = str(response)
        print(f"[ReportAgent] 最终结果长度: {len(result)}", flush=True)
        return self._clean_json_content(result)
    
    def _extract_content_from_message(self, message):
        """
        从消息对象中提取内容
        """
        msg_type = type(message).__name__
        print(f"[ReportAgent] 消息类型: {msg_type}", flush=True)
        
        # 检查是否有content属性
        if hasattr(message, 'content'):
            content = message.content
            print(f"[ReportAgent] 内容长度: {len(str(content))}", flush=True)
            
            # 如果是字典，转换为JSON字符串
            if isinstance(content, dict):
                import json
                result = json.dumps(content, ensure_ascii=False)
                print(f"[ReportAgent] 返回JSON字符串，长度: {len(result)}", flush=True)
                return result
            # 如果是字符串，清理后返回
            if isinstance(content, str):
                return self._clean_json_content(content)
        
        # 尝试直接访问content属性（不同的消息类型）
        try:
            if hasattr(message, 'content'):
                content = str(message.content)
                return self._clean_json_content(content)
        except:
            pass
        
        # 尝试字典方式访问
        if isinstance(message, dict) and 'content' in message:
            return self._clean_json_content(message['content'])
        
        return str(message)
    
    def _clean_json_content(self, content):
        """
        清理JSON内容，去除Markdown代码块包装，处理截断问题
        """
        if not isinstance(content, str):
            content = str(content)
        
        print(f"[ReportAgent] 原始内容长度: {len(content)}", flush=True)
        print(f"[ReportAgent] 原始内容前200字符: {content[:200]}", flush=True)
        
        # 去除可能的markdown代码块包装
        clean_content = content.strip()
        
        # 处理各种代码块格式
        if clean_content.startswith('```json'):
            clean_content = clean_content[7:]
        elif clean_content.startswith('```'):
            clean_content = clean_content[3:]
        
        if clean_content.endswith('```'):
            clean_content = clean_content[:-3]
        
        clean_content = clean_content.strip()
        
        # 处理可能的截断问题 - 尝试修复不完整的JSON
        clean_content = self._fix_truncated_json(clean_content)
        
        print(f"[ReportAgent] 清理后内容长度: {len(clean_content)}", flush=True)
        print(f"[ReportAgent] 清理后内容前200字符: {clean_content[:200]}", flush=True)
        
        return clean_content
    
    def _fix_truncated_json(self, json_str):
        """
        尝试修复被截断的JSON字符串
        """
        if not json_str:
            return json_str
        
        import re
        
        # 移除多余的逗号
        json_str = re.sub(r',\s*([}\]])', r'\1', json_str)
        
        # 检查是否需要闭合括号
        open_braces = json_str.count('{')
        close_braces = json_str.count('}')
        open_brackets = json_str.count('[')
        close_brackets = json_str.count(']')
        
        # 添加缺失的闭合括号
        while close_braces < open_braces:
            json_str += '}'
            close_braces += 1
        
        while close_brackets < open_brackets:
            json_str += ']'
            close_brackets += 1
        
        # 处理单引号问题（JSON要求双引号）
        # 注意：这可能会破坏包含单引号的字符串，需要谨慎
        # json_str = json_str.replace("'", '"')
        
        return json_str
    
    def generate(self, query: str, report_type: str, period: str):
        """
        生成招聘报告
        :param query: 用户的查询/需求
        :param report_type: 报告类型（周报/月报/季度报告等）
        :param period: 统计周期
        """
        prompt = f"""请生成一份{report_type}，统计周期为：{period}

{query}

请严格按照以下JSON格式返回报告数据：
{{
  "title": "报告标题",
  "period": "报告周期",
  "summary": "核心结论概述（2-3句话）",
  "keyMetrics": {{
    "newResumes": 数字,
    "totalCandidates": 数字,
    "matchCount": 数字,
    "avgScore": 数字,
    "interviewCount": 数字,
    "offerCount": 数字
  }},
  "trends": [
    {{"period": "时间段", "value": 数字, "change": "变化百分比"}}
  ],
  "insights": [
    {{"title": "洞察标题", "content": "详细说明"}}
  ],
  "highlights": ["亮点1", "亮点2"],
  "issues": [
    {{"issue": "问题描述", "suggestion": "改进建议"}}
  ],
  "nextPlan": "下期工作计划",
  "content": "报告正文（使用列表格式，不要使用Markdown表格，用分隔符和缩进展示数据）"
}}

重要提醒：
1. 必须先调用get_recruitment_statistics获取真实统计数据
2. 数据必须来自系统查询，不得虚构
3. content字段不要使用表格，用列表和分隔符展示数据
4. 确保JSON格式正确，可以被Python的json.loads解析
5. 返回结果只能是JSON格式，不要包含任何额外文字"""
        
        input_dict = {
            "messages": [
                {"role": "user", "content": prompt},
            ]
        }
        
        try:
            print(f"[ReportAgent] 开始调用Agent生成报告...", flush=True)
            response = self.agent.invoke(input_dict)
            
            print(f"[ReportAgent] 响应类型: {type(response).__name__}", flush=True)
            print(f"[ReportAgent] 响应: {str(response)[:500]}", flush=True)
            
            # 提取内容
            result = self._extract_content_from_response(response)
            
            if result is None:
                print(f"[ReportAgent] 未提取到有效内容，返回默认响应", flush=True)
                import json
                return json.dumps({
                    "title": f"{report_type} - {period}",
                    "period": period,
                    "summary": "正在获取数据...",
                    "keyMetrics": {"newResumes": 0, "totalCandidates": 0, "matchCount": 0, "avgScore": 0, "interviewCount": 0, "offerCount": 0},
                    "trends": [],
                    "insights": [],
                    "highlights": [],
                    "issues": [],
                    "nextPlan": "",
                    "content": "数据获取中..."
                }, ensure_ascii=False)
            
            return result
            
        except Exception as e:
            import traceback
            print(f"[ReportAgent] 生成失败: {str(e)}", flush=True)
            print(traceback.format_exc(), flush=True)
            # 返回一个默认的错误响应
            import json
            return json.dumps({
                "title": "报告生成失败",
                "period": period,
                "summary": "报告生成过程中遇到问题，请稍后重试",
                "keyMetrics": {"newResumes": 0, "totalCandidates": 0, "matchCount": 0, "avgScore": 0, "interviewCount": 0, "offerCount": 0},
                "trends": [],
                "insights": [],
                "highlights": [],
                "issues": [],
                "nextPlan": "",
                "content": f"报告生成失败: {str(e)}"
            }, ensure_ascii=False)


class ReactAgent:
    def __init__(self, load_tools: bool = True):
        """
        初始化ReactAgent
        :param load_tools: 是否加载工具（用于流式对话），默认True。人岗匹配等简单任务可设为False
        """
        self.agent = None
        if load_tools:
            # 只有在需要工具时才初始化 agent
            self.agent = create_agent(
                model=chat_model,
                system_prompt=load_system_prompts(),
                tools=[rag_summarize, read_resume_text, query_job_info, query_candidate_info, query_matching_weights,
                       get_all_jobs, get_all_candidates, search_candidates_by_skill, search_candidates_by_education,
                       search_candidates_by_work_years, get_all_job_categories],
                middleware=[monitor_tool, log_before_model, report_prompt_switch],
            )

    def execute_stream(self, query: str, system_prompt: str = None):
        """
        流式对话，适用于：
        - chat-query（对话式查询）
        - 需要多轮交互的场景
        """
        # 如果 agent 未初始化，先初始化
        if self.agent is None:
            self.agent = create_agent(
                model=chat_model,
                system_prompt=load_system_prompts(),
                tools=[rag_summarize, read_resume_text, query_job_info, query_candidate_info, query_matching_weights,
                       get_all_jobs, get_all_candidates, search_candidates_by_skill, search_candidates_by_education,
                       search_candidates_by_work_years, get_all_job_categories],
                middleware=[monitor_tool, log_before_model, report_prompt_switch],
            )
        
        prompt = system_prompt or load_system_prompts()

        input_dict = {
            "messages": [
                {"role": "system", "content": prompt},
                {"role": "user", "content": query},
            ]
        }

        previous_content = ""
        try:
            print(f"[Agent] 开始执行流式查询: {query[:30]}...", flush=True)
            for chunk in self.agent.stream(input_dict, stream_mode="values", context={"report": False}):
                try:
                    print(f"[Agent] 收到chunk: {type(chunk).__name__}", flush=True)
                    
                    # 处理不同格式的消息
                    if hasattr(chunk, 'messages'):
                        messages = chunk.messages
                    elif isinstance(chunk, dict) and 'messages' in chunk:
                        messages = chunk['messages']
                    else:
                        print(f"[Agent] chunk无messages字段，跳过", flush=True)
                        continue
                    
                    print(f"[Agent] 消息数量: {len(messages)}", flush=True)
                    
                    if not messages:
                        continue
                    
                    # 找到最后一条 AI 消息（根据类型判断）
                    latest_message = None
                    for msg in reversed(messages):
                        msg_type = type(msg).__name__
                        print(f"[Agent] 消息类型: {msg_type}", flush=True)
                        
                        # 根据消息类型判断，AIMessage 就是 AI 的回复
                        if msg_type == 'AIMessage':
                            latest_message = msg
                            print(f"[Agent] 找到AIMessage", flush=True)
                            break
                    
                    if not latest_message:
                        print(f"[Agent] 未找到assistant消息", flush=True)
                        continue
                        
                    # 获取消息内容
                    if hasattr(latest_message, 'content'):
                        content = str(latest_message.content) if latest_message.content else ""
                    elif isinstance(latest_message, dict):
                        content = str(latest_message.get('content', ''))
                    else:
                        content = ""
                    
                    print(f"[Agent] 内容长度: {len(content)}", flush=True)
                    
                    if content:
                        current_content = content.strip()
                        # 只返回新增的部分（增量），实现打字机效果
                        delta = current_content[len(previous_content):]
                        print(f"[Agent] delta长度: {len(delta)}", flush=True)
                        if delta:
                            yield delta
                        previous_content = current_content
                except Exception as e:
                    print(f"[Agent] 单条chunk处理失败: {str(e)}", flush=True)
                    continue
            print(f"[Agent] 流式查询结束", flush=True)
        except Exception as e:
            print(f"[Agent] 整体流处理失败: {str(e)}", flush=True)
            # 整体流处理失败，返回友好提示
            yield f"处理过程中遇到问题: {str(e)}"




    def execute_once(self, query: str, system_prompt: str = None, response_format: dict = None):
        """
        非流式调用，适用于：
        - 简历解析（要求返回 JSON）
        - 人岗匹配打分（要求返回 JSON）
        - 面试问题生成
        - 薪资建议
        等一次性任务
        """
        messages = []

        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})

        messages.append({"role": "user", "content": query})

        # 调用模型
        if response_format:
            # 强制 JSON 输出
            response = chat_model.invoke(
                messages,
                response_format=response_format
            )
        else:
            response = chat_model.invoke(messages)

        return response.content


if __name__ == '__main__':
    agent = ReactAgent()

    for chunk in agent.execute_stream("给我生成我的使用报告"):
        print(chunk, end="", flush=True)
