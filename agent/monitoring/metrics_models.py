"""
监控数据存储模型
定义监控指标的数据结构
"""
from sqlalchemy import Column, Integer, String, Text, Float, DateTime, JSON, Index
from sqlalchemy.ext.declarative import declarative_base
from datetime import datetime

Base = declarative_base()

class ConversationMetrics(Base):
    """对话指标表"""
    __tablename__ = "conversation_metrics"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    session_id = Column(String(64), nullable=False, index=True)  # 会话ID
    conversation_id = Column(String(64), nullable=False, unique=True)  # 对话ID
    
    # 检索指标
    recall_rate = Column(Float, nullable=True)  # 召回率
    retrieved_count = Column(Integer, default=0)  # 检索到的文档数
    relevant_count = Column(Integer, default=0)  # 相关文档数
    
    # 回答质量指标
    hallucination_rate = Column(Float, nullable=True)  # 幻觉率
    accuracy = Column(Float, nullable=True)  # 准确率
    user_rating = Column(Integer, nullable=True)  # 用户评分（1-5）
    
    # Token使用指标
    input_tokens = Column(Integer, default=0)  # 输入Token数
    output_tokens = Column(Integer, default=0)  # 输出Token数
    cached_tokens = Column(Integer, default=0)  # 缓存命中的Token数
    total_tokens = Column(Integer, default=0)  # 总Token数
    token_hit_rate = Column(Float, nullable=True)  # Token命中率
    
    # 元数据
    query_text = Column(Text, nullable=True)  # 用户查询文本
    response_text = Column(Text, nullable=True)  # AI回答文本
    model_name = Column(String(100), nullable=True)  # 使用的模型名称
    retrieval_method = Column(String(50), nullable=True)  # 检索方法（关键词/语义/混合）
    
    # 详细数据（JSON格式）
    retrieval_details = Column(JSON, nullable=True)  # 检索详情
    response_details = Column(JSON, nullable=True)  # 回答详情
    token_details = Column(JSON, nullable=True)  # Token详情
    
    created_at = Column(DateTime, default=datetime.now, index=True)  # 创建时间
    
    __table_args__ = (
        Index('idx_session_created', 'session_id', 'created_at'),
        Index('idx_conversation_id', 'conversation_id'),
    )


class TokenUsageSummary(Base):
    """Token使用汇总表"""
    __tablename__ = "token_usage_summary"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    date = Column(String(10), nullable=False, index=True)  # 日期（YYYY-MM-DD）
    
    # Token统计
    total_input_tokens = Column(Integer, default=0)  # 总输入Token
    total_output_tokens = Column(Integer, default=0)  # 总输出Token
    total_cached_tokens = Column(Integer, default=0)  # 总缓存Token
    total_tokens = Column(Integer, default=0)  # 总Token数
    
    # 对话统计
    total_conversations = Column(Integer, default=0)  # 总对话数
    total_sessions = Column(Integer, default=0)  # 总会话数
    
    # 成本估算（可选）
    estimated_cost = Column(Float, nullable=True)  # 估算成本
    
    created_at = Column(DateTime, default=datetime.now)
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now)
    
    __table_args__ = (
        Index('idx_date', 'date'),
    )


class SystemMetrics(Base):
    """系统指标表"""
    __tablename__ = "system_metrics"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    timestamp = Column(DateTime, default=datetime.now, index=True)  # 时间戳
    
    # 性能指标
    avg_response_time = Column(Float, nullable=True)  # 平均响应时间（秒）
    p95_response_time = Column(Float, nullable=True)  # P95响应时间
    p99_response_time = Column(Float, nullable=True)  # P99响应时间
    
    # 质量指标（聚合）
    avg_recall_rate = Column(Float, nullable=True)  # 平均召回率
    avg_hallucination_rate = Column(Float, nullable=True)  # 平均幻觉率
    avg_accuracy = Column(Float, nullable=True)  # 平均准确率
    avg_token_hit_rate = Column(Float, nullable=True)  # 平均Token命中率
    
    # 使用量指标
    total_tokens = Column(Integer, default=0)  # 总Token数
    total_conversations = Column(Integer, default=0)  # 总对话数
    
    # 错误指标
    error_count = Column(Integer, default=0)  # 错误数
    error_rate = Column(Float, nullable=True)  # 错误率
    
    # 元数据
    time_window = Column(String(20), nullable=True)  # 时间窗口（hourly/daily/weekly）
    
    __table_args__ = (
        Index('idx_timestamp_window', 'timestamp', 'time_window'),
    )


class UserFeedback(Base):
    """用户反馈表"""
    __tablename__ = "user_feedback"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    conversation_id = Column(String(64), nullable=False, index=True)  # 对话ID
    session_id = Column(String(64), nullable=False, index=True)  # 会话ID
    
    # 反馈内容
    rating = Column(Integer, nullable=False)  # 评分（1-5）
    feedback_text = Column(Text, nullable=True)  # 反馈文本
    feedback_type = Column(String(50), nullable=True)  # 反馈类型（helpful/not_helpful/needs_improvement）
    
    # 元数据
    user_id = Column(Integer, nullable=True)  # 用户ID
    created_at = Column(DateTime, default=datetime.now, index=True)  # 创建时间
    
    __table_args__ = (
        Index('idx_conversation_rating', 'conversation_id', 'rating'),
    )