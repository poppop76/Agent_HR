"""
监控数据收集器
收集和存储AI系统的各种监控指标
"""
import logging
from typing import Dict, List, Optional, Any
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from sqlalchemy import func, and_, desc
import uuid
import json

from agent.monitoring.metrics_calculator import MetricsCalculator, get_metrics_calculator
from agent.monitoring.metrics_models import (
    ConversationMetrics, 
    TokenUsageSummary, 
    SystemMetrics,
    UserFeedback
)

logger = logging.getLogger(__name__)

class MetricsCollector:
    """监控指标收集器"""
    
    def __init__(self, db_session_factory):
        """
        初始化收集器
        
        Args:
            db_session_factory: 数据库会话工厂
        """
        self.db_session_factory = db_session_factory
        self.metrics_calculator = get_metrics_calculator()
    
    def collect_conversation_metrics(
        self,
        session_id: str,
        query_text: str,
        response_text: str,
        retrieval_data: Optional[Dict[str, Any]] = None,
        token_data: Optional[Dict[str, Any]] = None,
        model_name: str = None,
        retrieval_method: str = None
    ) -> str:
        """
        收集对话指标
        
        Args:
            session_id: 会话ID
            query_text: 用户查询文本
            response_text: AI回答文本
            retrieval_data: 检索数据
            token_data: Token数据
            model_name: 模型名称
            retrieval_method: 检索方法
            
        Returns:
            对话指标ID
        """
        try:
            # 生成对话ID
            conversation_id = str(uuid.uuid4())
            
            # 计算综合指标
            metrics = self.metrics_calculator.calculate_comprehensive_metrics(
                retrieval_data=retrieval_data,
                response_data={'ai_response': response_text},
                token_data=token_data
            )
            
            # 提取指标值
            metric_values = metrics.get('metrics', {})
            
            # 创建对话指标记录
            db: Session = self.db_session_factory()
            try:
                conversation_metric = ConversationMetrics(
                    conversation_id=conversation_id,
                    session_id=session_id,
                    query_text=query_text,
                    response_text=response_text,
                    model_name=model_name,
                    retrieval_method=retrieval_method,
                    
                    # 检索指标
                    recall_rate=metric_values.get('recall'),
                    retrieved_count=len(retrieval_data.get('retrieved_docs', [])) if retrieval_data else 0,
                    relevant_count=len(retrieval_data.get('relevant_docs', [])) if retrieval_data else 0,
                    
                    # 回答质量指标
                    hallucination_rate=metric_values.get('hallucination_rate'),
                    accuracy=metric_values.get('accuracy'),
                    
                    # Token指标
                    input_tokens=token_data.get('input_tokens', 0) if token_data else 0,
                    output_tokens=token_data.get('output_tokens', 0) if token_data else 0,
                    cached_tokens=token_data.get('cached_tokens', 0) if token_data else 0,
                    total_tokens=token_data.get('total_tokens', 0) if token_data else 0,
                    token_hit_rate=metric_values.get('token_hit_rate'),
                    
                    # 详细数据
                    retrieval_details=retrieval_data,
                    response_details={'ai_response': response_text},
                    token_details=token_data
                )
                
                db.add(conversation_metric)
                db.commit()
                
                # 更新Token使用汇总
                self._update_token_summary(db, token_data)
                
                logger.info(f"[MetricsCollector] 收集对话指标成功: {conversation_id}")
                return conversation_id
                
            except Exception as e:
                db.rollback()
                logger.error(f"[MetricsCollector] 保存对话指标失败: {e}")
                raise
            finally:
                db.close()
                
        except Exception as e:
            logger.error(f"[MetricsCollector] 收集对话指标失败: {e}")
            raise
    
    def collect_user_feedback(
        self,
        conversation_id: str,
        session_id: str,
        rating: int,
        feedback_text: str = None,
        feedback_type: str = None,
        user_id: int = None
    ):
        """
        收集用户反馈
        
        Args:
            conversation_id: 对话ID
            session_id: 会话ID
            rating: 评分（1-5）
            feedback_text: 反馈文本
            feedback_type: 反馈类型
            user_id: 用户ID
        """
        try:
            db: Session = self.db_session_factory()
            try:
                feedback = UserFeedback(
                    conversation_id=conversation_id,
                    session_id=session_id,
                    rating=rating,
                    feedback_text=feedback_text,
                    feedback_type=feedback_type,
                    user_id=user_id
                )
                
                db.add(feedback)
                
                # 更新对话指标的评分
                db.query(ConversationMetrics).filter(
                    ConversationMetrics.conversation_id == conversation_id
                ).update({'user_rating': rating})
                
                db.commit()
                logger.info(f"[MetricsCollector] 收集用户反馈成功: {conversation_id}, rating={rating}")
                
            except Exception as e:
                db.rollback()
                logger.error(f"[MetricsCollector] 保存用户反馈失败: {e}")
                raise
            finally:
                db.close()
                
        except Exception as e:
            logger.error(f"[MetricsCollector] 收集用户反馈失败: {e}")
    
    def _update_token_summary(self, db: Session, token_data: Optional[Dict[str, Any]]):
        """更新Token使用汇总"""
        if not token_data:
            return
        
        today = datetime.now().strftime('%Y-%m-%d')
        
        # 查找或创建今日汇总记录
        summary = db.query(TokenUsageSummary).filter(
            TokenUsageSummary.date == today
        ).first()
        
        if not summary:
            summary = TokenUsageSummary(date=today)
            db.add(summary)
        
        # 更新统计数据
        summary.total_input_tokens += token_data.get('input_tokens', 0)
        summary.total_output_tokens += token_data.get('output_tokens', 0)
        summary.total_cached_tokens += token_data.get('cached_tokens', 0)
        summary.total_tokens += token_data.get('total_tokens', 0)
        summary.total_conversations += 1
        
        # 成本估算（假设：输入Token $0.001/1K，输出Token $0.002/1K）
        input_cost = token_data.get('input_tokens', 0) * 0.001 / 1000
        output_cost = token_data.get('output_tokens', 0) * 0.002 / 1000
        if summary.estimated_cost is None:
            summary.estimated_cost = 0
        summary.estimated_cost += (input_cost + output_cost)
    
    def get_metrics_summary(
        self,
        start_date: Optional[str] = None,
        end_date: Optional[str] = None,
        session_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        获取指标汇总
        
        Args:
            start_date: 开始日期
            end_date: 结束日期
            session_id: 会话ID（可选）
            
        Returns:
            指标汇总数据
        """
        db: Session = self.db_session_factory()
        try:
            # 构建查询条件
            query = db.query(ConversationMetrics)
            
            if start_date:
                start_datetime = datetime.strptime(start_date, '%Y-%m-%d')
                query = query.filter(ConversationMetrics.created_at >= start_datetime)
            
            if end_date:
                end_datetime = datetime.strptime(end_date, '%Y-%m-%d') + timedelta(days=1)
                query = query.filter(ConversationMetrics.created_at < end_datetime)
            
            if session_id:
                query = query.filter(ConversationMetrics.session_id == session_id)
            
            # 计算聚合指标
            metrics = query.with_entities(
                func.avg(ConversationMetrics.recall_rate).label('avg_recall'),
                func.avg(ConversationMetrics.hallucination_rate).label('avg_hallucination'),
                func.avg(ConversationMetrics.accuracy).label('avg_accuracy'),
                func.avg(ConversationMetrics.token_hit_rate).label('avg_token_hit_rate'),
                func.sum(ConversationMetrics.total_tokens).label('total_tokens'),
                func.count(ConversationMetrics.id).label('total_conversations'),
                func.avg(ConversationMetrics.user_rating).label('avg_rating')
            ).first()
            
            # 获取Token使用汇总
            token_summary = db.query(TokenUsageSummary).filter(
                TokenUsageSummary.date >= (start_date or datetime.now().strftime('%Y-%m-%d')),
                TokenUsageSummary.date <= (end_date or datetime.now().strftime('%Y-%m-%d'))
            ).all()
            
            total_input_tokens = sum(s.total_input_tokens for s in token_summary)
            total_output_tokens = sum(s.total_output_tokens for s in token_summary)
            total_cached_tokens = sum(s.total_cached_tokens for s in token_summary)
            estimated_cost = sum(s.estimated_cost or 0 for s in token_summary)
            
            return {
                'quality_metrics': {
                    'avg_recall_rate': float(metrics.avg_recall) if metrics.avg_recall else 0,
                    'avg_hallucination_rate': float(metrics.avg_hallucination) if metrics.avg_hallucination else 0,
                    'avg_accuracy': float(metrics.avg_accuracy) if metrics.avg_accuracy else 0,
                    'avg_user_rating': float(metrics.avg_rating) if metrics.avg_rating else 0
                },
                'token_metrics': {
                    'total_input_tokens': total_input_tokens,
                    'total_output_tokens': total_output_tokens,
                    'total_cached_tokens': total_cached_tokens,
                    'total_tokens': total_input_tokens + total_output_tokens,
                    'avg_token_hit_rate': float(metrics.avg_token_hit_rate) if metrics.avg_token_hit_rate else 0,
                    'estimated_cost': estimated_cost
                },
                'usage_metrics': {
                    'total_conversations': metrics.total_conversations or 0,
                    'date_range': {
                        'start': start_date,
                        'end': end_date
                    }
                }
            }
            
        finally:
            db.close()
    
    def get_metrics_trend(
        self,
        days: int = 7,
        metric_type: str = 'all'
    ) -> List[Dict[str, Any]]:
        """
        获取指标趋势
        
        Args:
            days: 天数
            metric_type: 指标类型（recall/hallucination/accuracy/token_hit_rate/all）
            
        Returns:
            趋势数据列表
        """
        db: Session = self.db_session_factory()
        try:
            end_date = datetime.now()
            start_date = end_date - timedelta(days=days)
            
            # 按日期分组统计
            query = db.query(
                func.date(ConversationMetrics.created_at).label('date'),
                func.avg(ConversationMetrics.recall_rate).label('avg_recall'),
                func.avg(ConversationMetrics.hallucination_rate).label('avg_hallucination'),
                func.avg(ConversationMetrics.accuracy).label('avg_accuracy'),
                func.avg(ConversationMetrics.token_hit_rate).label('avg_token_hit_rate'),
                func.sum(ConversationMetrics.total_tokens).label('total_tokens'),
                func.count(ConversationMetrics.id).label('conversation_count')
            ).filter(
                ConversationMetrics.created_at >= start_date,
                ConversationMetrics.created_at < end_date
            ).group_by(
                func.date(ConversationMetrics.created_at)
            ).order_by(
                func.date(ConversationMetrics.created_at)
            ).all()
            
            trends = []
            for row in query:
                trend = {
                    'date': row.date.strftime('%Y-%m-%d'),
                    'conversation_count': row.conversation_count
                }
                
                if metric_type in ['recall', 'all']:
                    trend['recall_rate'] = float(row.avg_recall) if row.avg_recall else 0
                
                if metric_type in ['hallucination', 'all']:
                    trend['hallucination_rate'] = float(row.avg_hallucination) if row.avg_hallucination else 0
                
                if metric_type in ['accuracy', 'all']:
                    trend['accuracy'] = float(row.avg_accuracy) if row.avg_accuracy else 0
                
                if metric_type in ['token_hit_rate', 'all']:
                    trend['token_hit_rate'] = float(row.avg_token_hit_rate) if row.avg_token_hit_rate else 0
                    trend['total_tokens'] = row.total_tokens or 0
                
                trends.append(trend)
            
            return trends
            
        finally:
            db.close()


# 全局收集器实例
_metrics_collector = None

def get_metrics_collector(db_session_factory) -> MetricsCollector:
    """获取全局收集器实例"""
    global _metrics_collector
    if _metrics_collector is None:
        _metrics_collector = MetricsCollector(db_session_factory)
    return _metrics_collector