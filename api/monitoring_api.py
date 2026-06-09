"""
监控指标API路由
提供指标查询、统计、趋势分析等接口
"""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime, timedelta
import json

from core.config import settings
from db.database import get_db, SessionLocal
from agent.monitoring.metrics_collector import get_metrics_collector, MetricsCollector

router = APIRouter(prefix=settings.API_PREFIX)


class MetricsSummaryRequest(BaseModel):
    """指标汇总请求"""
    start_date: Optional[str] = None
    end_date: Optional[str] = None
    session_id: Optional[str] = None


class MetricsTrendRequest(BaseModel):
    """指标趋势请求"""
    days: int = 7
    metric_type: str = 'all'  # recall/hallucination/accuracy/token_hit_rate/all


class UserFeedbackRequest(BaseModel):
    """用户反馈请求"""
    conversation_id: str
    session_id: str
    rating: int  # 1-5
    feedback_text: Optional[str] = None
    feedback_type: Optional[str] = None
    user_id: Optional[int] = None


@router.get("/monitoring/summary")
def get_metrics_summary(
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
    session_id: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """
    获取指标汇总
    
    参数:
        start_date: 开始日期 (YYYY-MM-DD)
        end_date: 结束日期 (YYYY-MM-DD)
        session_id: 会话ID（可选）
    """
    try:
        # 默认查询最近7天
        if not end_date:
            end_date = datetime.now().strftime('%Y-%m-%d')
        if not start_date:
            start_date = (datetime.now() - timedelta(days=7)).strftime('%Y-%m-%d')
        
        collector = MetricsCollector(SessionLocal)
        summary = collector.get_metrics_summary(start_date, end_date, session_id)
        
        return {
            "code": settings.RES_CODE["200"],
            "msg": "获取成功",
            "data": summary
        }
    except Exception as e:
        import traceback
        error_detail = str(e)
        print(f"[监控] 获取指标汇总失败: {error_detail}")
        print(traceback.format_exc())
        
        # 检查是否是表不存在的错误
        if "doesn't exist" in error_detail or "Table" in error_detail:
            raise HTTPException(
                status_code=500, 
                detail="监控表未初始化，请先执行 database/init.sql 脚本创建监控表"
            )
        raise HTTPException(status_code=500, detail=f"获取指标汇总失败: {error_detail}")


@router.get("/monitoring/trend")
def get_metrics_trend(
    days: int = 7,
    metric_type: str = 'all',
    db: Session = Depends(get_db)
):
    """
    获取指标趋势
    
    参数:
        days: 天数
        metric_type: 指标类型 (recall/hallucination/accuracy/token_hit_rate/all)
    """
    try:
        collector = MetricsCollector(SessionLocal)
        trends = collector.get_metrics_trend(days, metric_type)
        
        return {
            "code": settings.RES_CODE["200"],
            "msg": "获取成功",
            "data": trends
        }
    except Exception as e:
        import traceback
        print(f"[监控] 获取指标趋势失败: {e}")
        print(traceback.format_exc())
        raise HTTPException(status_code=500, detail=f"获取指标趋势失败: {str(e)}")


@router.post("/monitoring/feedback")
def submit_user_feedback(req: UserFeedbackRequest, db: Session = Depends(get_db)):
    """
    提交用户反馈
    """
    try:
        # 验证评分范围
        if req.rating < 1 or req.rating > 5:
            raise HTTPException(status_code=400, detail="评分必须在1-5之间")
        
        collector = MetricsCollector(SessionLocal)
        collector.collect_user_feedback(
            conversation_id=req.conversation_id,
            session_id=req.session_id,
            rating=req.rating,
            feedback_text=req.feedback_text,
            feedback_type=req.feedback_type,
            user_id=req.user_id
        )
        
        return {
            "code": settings.RES_CODE["200"],
            "msg": "反馈提交成功",
            "data": None
        }
    except HTTPException:
        raise
    except Exception as e:
        import traceback
        print(f"[监控] 提交用户反馈失败: {e}")
        print(traceback.format_exc())
        raise HTTPException(status_code=500, detail=f"提交用户反馈失败: {str(e)}")


@router.get("/monitoring/token-usage")
def get_token_usage(
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """
    获取Token使用统计
    """
    try:
        from agent.monitoring.metrics_models import TokenUsageSummary
        
        # 默认查询本月
        if not end_date:
            end_date = datetime.now().strftime('%Y-%m-%d')
        if not start_date:
            start_date = datetime.now().replace(day=1).strftime('%Y-%m-%d')
        
        summaries = db.query(TokenUsageSummary).filter(
            TokenUsageSummary.date >= start_date,
            TokenUsageSummary.date <= end_date
        ).order_by(TokenUsageSummary.date).all()
        
        data = []
        for summary in summaries:
            data.append({
                'date': summary.date,
                'total_input_tokens': summary.total_input_tokens,
                'total_output_tokens': summary.total_output_tokens,
                'total_cached_tokens': summary.total_cached_tokens,
                'total_tokens': summary.total_tokens,
                'total_conversations': summary.total_conversations,
                'estimated_cost': summary.estimated_cost
            })
        
        # 计算总计
        total_input = sum(s.total_input_tokens for s in summaries)
        total_output = sum(s.total_output_tokens for s in summaries)
        total_cached = sum(s.total_cached_tokens for s in summaries)
        total_cost = sum(s.estimated_cost or 0 for s in summaries)
        
        return {
            "code": settings.RES_CODE["200"],
            "msg": "获取成功",
            "data": {
                "daily_data": data,
                "summary": {
                    "total_input_tokens": total_input,
                    "total_output_tokens": total_output,
                    "total_cached_tokens": total_cached,
                    "total_tokens": total_input + total_output,
                    "estimated_cost": total_cost,
                    "date_range": {
                        "start": start_date,
                        "end": end_date
                    }
                }
            }
        }
    except Exception as e:
        import traceback
        error_detail = str(e)
        print(f"[监控] 获取Token使用统计失败: {error_detail}")
        print(traceback.format_exc())
        
        if "doesn't exist" in error_detail or "Table" in error_detail:
            raise HTTPException(
                status_code=500, 
                detail="监控表未初始化，请先执行 database/init.sql 脚本创建监控表"
            )
        raise HTTPException(status_code=500, detail=f"获取Token使用统计失败: {error_detail}")


@router.get("/monitoring/conversation-details")
def get_conversation_details(
    session_id: str,
    limit: int = 50,
    db: Session = Depends(get_db)
):
    """
    获取对话详情
    """
    try:
        from agent.monitoring.metrics_models import ConversationMetrics
        
        conversations = db.query(ConversationMetrics).filter(
            ConversationMetrics.session_id == session_id
        ).order_by(
            ConversationMetrics.created_at.desc()
        ).limit(limit).all()
        
        data = []
        for conv in conversations:
            data.append({
                'conversation_id': conv.conversation_id,
                'query_text': conv.query_text,
                'response_text': conv.response_text,
                'recall_rate': conv.recall_rate,
                'hallucination_rate': conv.hallucination_rate,
                'accuracy': conv.accuracy,
                'user_rating': conv.user_rating,
                'token_hit_rate': conv.token_hit_rate,
                'total_tokens': conv.total_tokens,
                'created_at': conv.created_at.isoformat() if conv.created_at else None,
                'retrieval_method': conv.retrieval_method
            })
        
        return {
            "code": settings.RES_CODE["200"],
            "msg": "获取成功",
            "data": data
        }
    except Exception as e:
        import traceback
        print(f"[监控] 获取对话详情失败: {e}")
        print(traceback.format_exc())
        raise HTTPException(status_code=500, detail=f"获取对话详情失败: {str(e)}")