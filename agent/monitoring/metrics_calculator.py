"""
AI系统监控指标计算模块
计算召回率、幻觉情况、准确率、Token命中率等指标
"""
import logging
from typing import Dict, List, Optional, Any
from datetime import datetime
from enum import Enum

logger = logging.getLogger(__name__)

class MetricType(Enum):
    """指标类型"""
    RECALL = "recall"  # 召回率
    HALLUCINATION = "hallucination"  # 幻觉率
    ACCURACY = "accuracy"  # 准确率
    TOKEN_HIT_RATE = "token_hit_rate"  # Token命中率
    TOKEN_USAGE = "token_usage"  # Token使用量

class MetricsCalculator:
    """监控指标计算器"""
    
    def __init__(self):
        """初始化指标计算器"""
        self.metrics_history = []
    
    def calculate_recall(
        self,
        retrieved_docs: List[Dict[str, Any]],
        relevant_docs: List[Dict[str, Any]]
    ) -> float:
        """
        计算召回率
        
        Args:
            retrieved_docs: 检索到的文档列表
            relevant_docs: 真正相关的文档列表
            
        Returns:
            召回率 (0-1)
        """
        if not relevant_docs:
            return 1.0  # 没有相关文档，召回率为1
        
        if not retrieved_docs:
            return 0.0  # 没有检索到文档，召回率为0
        
        # 获取相关文档的ID集合
        relevant_ids = set(doc.get('id', doc.get('memory_id', '')) for doc in relevant_docs)
        retrieved_ids = set(doc.get('id', doc.get('memory_id', '')) for doc in retrieved_docs)
        
        # 计算检索到的相关文档数
        hit_count = len(relevant_ids & retrieved_ids)
        
        # 召回率 = 检索到的相关文档数 / 总相关文档数
        recall = hit_count / len(relevant_ids)
        
        logger.info(f"[Metrics] 召回率计算: {hit_count}/{len(relevant_ids)} = {recall:.4f}")
        return recall
    
    def calculate_hallucination_rate(
        self,
        ai_response: str,
        ground_truth: Optional[str] = None,
        fact_check_results: Optional[Dict[str, Any]] = None
    ) -> float:
        """
        计算幻觉率
        
        Args:
            ai_response: AI回答内容
            ground_truth: 标准答案（如果有）
            fact_check_results: 事实核查结果
            
        Returns:
            幻觉率 (0-1)
        """
        if not ai_response:
            return 0.0
        
        # 如果有事实核查结果，直接使用
        if fact_check_results:
            hallucinated_count = fact_check_results.get('hallucinated_count', 0)
            total_claims = fact_check_results.get('total_claims', 1)
            return hallucinated_count / total_claims if total_claims > 0 else 0.0
        
        # 如果有标准答案，进行对比
        if ground_truth:
            # 简单的相似度计算（实际可以使用更复杂的NLP方法）
            similarity = self._calculate_similarity(ai_response, ground_truth)
            hallucination_rate = 1.0 - similarity
            logger.info(f"[Metrics] 幻觉率计算: 1-{similarity:.4f} = {hallucination_rate:.4f}")
            return hallucination_rate
        
        # 默认返回0（无法计算）
        return 0.0
    
    def _calculate_similarity(self, text1: str, text2: str) -> float:
        """
        计算两个文本的相似度（简化版）
        
        Args:
            text1: 文本1
            text2: 文本2
            
        Returns:
            相似度 (0-1)
        """
        # 使用简单的词重叠计算相似度
        words1 = set(text1.split())
        words2 = set(text2.split())
        
        if not words1 or not words2:
            return 0.0
        
        intersection = words1 & words2
        union = words1 | words2
        
        return len(intersection) / len(union)
    
    def calculate_accuracy(
        self,
        correct_count: int,
        total_count: int,
        user_feedback: Optional[List[Dict[str, Any]]] = None
    ) -> float:
        """
        计算准确率
        
        Args:
            correct_count: 正确回答数
            total_count: 总回答数
            user_feedback: 用户反馈列表（可选）
            
        Returns:
            准确率 (0-1)
        """
        if total_count == 0:
            return 0.0
        
        # 如果有用户反馈，使用反馈数据计算
        if user_feedback:
            positive_count = sum(1 for f in user_feedback if f.get('rating', 0) >= 4)
            total_feedback = len(user_feedback)
            accuracy = positive_count / total_feedback if total_feedback > 0 else 0.0
            logger.info(f"[Metrics] 准确率计算（用户反馈）: {positive_count}/{total_feedback} = {accuracy:.4f}")
            return accuracy
        
        # 使用传入的计数
        accuracy = correct_count / total_count
        logger.info(f"[Metrics] 准确率计算: {correct_count}/{total_count} = {accuracy:.4f}")
        return accuracy
    
    def calculate_token_hit_rate(
        self,
        total_tokens: int,
        cached_tokens: int
    ) -> float:
        """
        计算Token命中率
        
        Args:
            total_tokens: 总Token数
            cached_tokens: 缓存命中的Token数
            
        Returns:
            Token命中率 (0-1)
        """
        if total_tokens == 0:
            return 0.0
        
        hit_rate = cached_tokens / total_tokens
        logger.info(f"[Metrics] Token命中率计算: {cached_tokens}/{total_tokens} = {hit_rate:.4f}")
        return hit_rate
    
    def calculate_token_usage(
        self,
        input_tokens: int,
        output_tokens: int,
        cached_tokens: int = 0
    ) -> Dict[str, Any]:
        """
        计算Token使用量
        
        Args:
            input_tokens: 输入Token数
            output_tokens: 输出Token数
            cached_tokens: 缓存命中的Token数
            
        Returns:
            Token使用量统计
        """
        total_tokens = input_tokens + output_tokens
        actual_tokens = total_tokens - cached_tokens
        
        usage_stats = {
            'input_tokens': input_tokens,
            'output_tokens': output_tokens,
            'cached_tokens': cached_tokens,
            'total_tokens': total_tokens,
            'actual_tokens': actual_tokens,
            'timestamp': datetime.now().isoformat()
        }
        
        logger.info(f"[Metrics] Token使用量: 输入={input_tokens}, 输出={output_tokens}, 缓存={cached_tokens}, 总计={total_tokens}")
        return usage_stats
    
    def calculate_comprehensive_metrics(
        self,
        retrieval_data: Optional[Dict[str, Any]] = None,
        response_data: Optional[Dict[str, Any]] = None,
        token_data: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        计算综合指标
        
        Args:
            retrieval_data: 检索相关数据
            response_data: 回答相关数据
            token_data: Token相关数据
            
        Returns:
            综合指标统计
        """
        metrics = {
            'timestamp': datetime.now().isoformat(),
            'metrics': {}
        }
        
        # 计算召回率
        if retrieval_data:
            metrics['metrics']['recall'] = self.calculate_recall(
                retrieval_data.get('retrieved_docs', []),
                retrieval_data.get('relevant_docs', [])
            )
        
        # 计算幻觉率
        if response_data:
            metrics['metrics']['hallucination_rate'] = self.calculate_hallucination_rate(
                response_data.get('ai_response', ''),
                response_data.get('ground_truth'),
                response_data.get('fact_check_results')
            )
        
        # 计算准确率
        if response_data:
            metrics['metrics']['accuracy'] = self.calculate_accuracy(
                response_data.get('correct_count', 0),
                response_data.get('total_count', 1),
                response_data.get('user_feedback')
            )
        
        # 计算Token命中率和使用量
        if token_data:
            metrics['metrics']['token_hit_rate'] = self.calculate_token_hit_rate(
                token_data.get('total_tokens', 1),
                token_data.get('cached_tokens', 0)
            )
            metrics['metrics']['token_usage'] = self.calculate_token_usage(
                token_data.get('input_tokens', 0),
                token_data.get('output_tokens', 0),
                token_data.get('cached_tokens', 0)
            )
        
        # 保存到历史记录
        self.metrics_history.append(metrics)
        
        return metrics


# 全局指标计算器实例
_metrics_calculator = None

def get_metrics_calculator() -> MetricsCalculator:
    """获取全局指标计算器实例"""
    global _metrics_calculator
    if _metrics_calculator is None:
        _metrics_calculator = MetricsCalculator()
    return _metrics_calculator