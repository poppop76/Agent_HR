"""
Query改写模块
将用户的自然语言问题改写成更精准、更专业的查询语句
"""
import os
import logging
from typing import List, Optional

# 尝试从正确的模块导入ChatOpenAI
try:
    from langchain_openai import ChatOpenAI
except ImportError:
    try:
        from langchain_community.chat_models import ChatOpenAI
    except ImportError:
        ChatOpenAI = None

from langchain.prompts import PromptTemplate

logger = logging.getLogger(__name__)

class QueryRewriter:
    """Query改写器，将用户问题改写成更精准的查询"""
    
    def __init__(self):
        """初始化Query改写器"""
        self.prompt_template = self._load_prompt_template()
        self.llm = self._init_llm()
        
    def _load_prompt_template(self) -> str:
        """加载Query改写提示词模板"""
        prompt_path = os.path.join(
            os.path.dirname(__file__), 
            'data', 'prompt', 'Query改写提示词.txt'
        )
        
        try:
            with open(prompt_path, 'r', encoding='utf-8') as f:
                return f.read()
        except FileNotFoundError:
            logger.warning(f"[QueryRewriter] 提示词文件不存在: {prompt_path}")
            return self._get_default_prompt()
    
    def _get_default_prompt(self) -> str:
        """获取默认提示词"""
        return """你是一个专业的查询改写助手，负责将用户的自然语言问题改写成更精准的查询语句。

改写规则：
1. 理解用户意图，分析核心需求
2. 结合历史对话上下文，补充缺失信息
3. 使用专业术语和标准表达
4. 明确查询的对象、条件、范围
5. 保持简洁，避免冗余

直接输出改写后的查询语句，不需要解释。"""
    
    def _init_llm(self):
        """初始化LLM"""
        if ChatOpenAI is None:
            logger.warning("[QueryRewriter] ChatOpenAI 未安装，跳过LLM初始化")
            return None
            
        try:
            from core.config import settings
            
            # 使用较小的模型进行改写，节省资源
            llm = ChatOpenAI(
                model_name=settings.OPENAI_MODEL_NAME,
                openai_api_key=settings.OPENAI_API_KEY,
                openai_api_base=settings.OPENAI_API_BASE,
                temperature=0.3,  # 较低温度，保证改写稳定性
                max_tokens=200,   # 改写结果通常较短
                request_timeout=10
            )
            return llm
        except Exception as e:
            logger.error(f"[QueryRewriter] LLM初始化失败: {e}")
            return None
    
    def rewrite(
        self, 
        original_query: str, 
        context: Optional[str] = None,
        history_keywords: Optional[List[str]] = None
    ) -> str:
        """
        改写用户查询
        
        Args:
            original_query: 用户原始问题
            context: 当前上下文信息（如当前查看的岗位、候选人等）
            history_keywords: 历史对话关键词
            
        Returns:
            改写后的查询语句
        """
        if not self.llm:
            logger.warning("[QueryRewriter] LLM未初始化，返回原始查询")
            return original_query
        
        # 构建改写提示
        prompt = self._build_rewrite_prompt(original_query, context, history_keywords)
        
        try:
            # 调用LLM进行改写
            rewritten_query = self.llm.invoke(prompt)
            
            # 清理结果
            rewritten_query = rewritten_query.strip()
            
            # 如果改写结果为空或过长，返回原始查询
            if not rewritten_query or len(rewritten_query) > len(original_query) * 3:
                logger.warning("[QueryRewriter] 改写结果异常，使用原始查询")
                return original_query
            
            logger.info(f"[QueryRewriter] 改写成功: '{original_query}' -> '{rewritten_query}'")
            return rewritten_query
            
        except Exception as e:
            logger.error(f"[QueryRewriter] 改写失败: {e}")
            return original_query
    
    def _build_rewrite_prompt(
        self, 
        original_query: str, 
        context: Optional[str] = None,
        history_keywords: Optional[List[str]] = None
    ) -> str:
        """构建改写提示"""
        
        # 基础提示
        prompt_parts = [self.prompt_template]
        
        # 添加上下文信息
        if context:
            prompt_parts.append(f"\n\n## 当前上下文\n{context}")
        
        # 添加历史关键词
        if history_keywords and len(history_keywords) > 0:
            keywords_str = ", ".join(history_keywords[:10])  # 最多10个关键词
            prompt_parts.append(f"\n\n## 相关关键词\n{keywords_str}")
        
        # 添加原始问题和改写要求
        prompt_parts.append(f"\n\n## 原始问题\n{original_query}")
        prompt_parts.append("\n\n## 改写结果\n（直接输出改写后的查询语句）")
        
        return "\n".join(prompt_parts)
    
    def rewrite_with_context_detection(
        self, 
        original_query: str,
        session_context: Optional[dict] = None
    ) -> str:
        """
        带上下文检测的Query改写
        
        Args:
            original_query: 用户原始问题
            session_context: 会话上下文信息
            
        Returns:
            改写后的查询语句
        """
        # 提取上下文信息
        context_str = None
        history_keywords = None
        
        if session_context:
            # 提取当前关注的对象（如岗位、候选人）
            if 'current_position' in session_context:
                context_str = f"当前关注岗位: {session_context['current_position']}"
            elif 'current_candidate' in session_context:
                context_str = f"当前关注候选人: {session_context['current_candidate']}"
            
            # 提取历史关键词
            history_keywords = session_context.get('history_keywords', [])
        
        return self.rewrite(original_query, context_str, history_keywords)


# 全局Query改写器实例
_query_rewriter = None

def get_query_rewriter() -> QueryRewriter:
    """获取全局Query改写器实例"""
    global _query_rewriter
    if _query_rewriter is None:
        _query_rewriter = QueryRewriter()
    return _query_rewriter