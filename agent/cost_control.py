"""
成本控制模块
提供Token使用限制、预算管理和成本优化功能
"""
import logging
import time
from typing import Dict, Any, Optional, Callable
from datetime import datetime, timedelta
from threading import Lock
from dataclasses import dataclass
from enum import Enum

logger = logging.getLogger(__name__)


class CostModel(Enum):
    """成本模型"""
    OPENAI_GPT35 = "openai_gpt35"
    OPENAI_GPT4 = "openai_gpt4"
    ANTHROPIC_CLAUDE = "anthropic_claude"
    CUSTOM = "custom"


@dataclass
class TokenPricing:
    """Token定价"""
    model_name: str
    input_price_per_1k: float   # 每1000输入Token的价格（元）
    output_price_per_1k: float  # 每1000输出Token的价格（元）
    context_window: int         # 上下文窗口大小
    max_tokens: int             # 最大输出Token


# 预定义的定价模型
PRICING_MODELS: Dict[CostModel, TokenPricing] = {
    CostModel.OPENAI_GPT35: TokenPricing(
        model_name="gpt-3.5-turbo",
        input_price_per_1k=0.0015,
        output_price_per_1k=0.002,
        context_window=16384,
        max_tokens=4096
    ),
    CostModel.OPENAI_GPT4: TokenPricing(
        model_name="gpt-4",
        input_price_per_1k=0.03,
        output_price_per_1k=0.06,
        context_window=8192,
        max_tokens=4096
    ),
    CostModel.ANTHROPIC_CLAUDE: TokenPricing(
        model_name="claude-3-sonnet",
        input_price_per_1k=0.008,
        output_price_per_1k=0.024,
        context_window=200000,
        max_tokens=8192
    )
}


@dataclass
class Budget:
    """预算配置"""
    daily_limit: float = 100.0    # 每日预算上限（元）
    monthly_limit: float = 3000.0 # 每月预算上限（元）
    soft_limit_ratio: float = 0.8 # 软限制比例（触发警告）
    hard_limit_ratio: float = 0.95 # 硬限制比例（拒绝请求）


@dataclass
class Consumption:
    """消费记录"""
    date: str                    # 日期 YYYY-MM-DD
    model: str                   # 模型名称
    input_tokens: int = 0        # 输入Token数
    output_tokens: int = 0       # 输出Token数
    cost: float = 0.0            # 消费金额（元）
    requests: int = 0            # 请求次数


@dataclass
class RateLimit:
    """限流配置"""
    requests_per_minute: int = 60    # 每分钟最大请求数
    tokens_per_minute: int = 10000   # 每分钟最大Token数
    requests_per_day: int = 10000    # 每日最大请求数


class CostController:
    """成本控制器"""
    
    def __init__(
        self,
        pricing_model: CostModel = CostModel.OPENAI_GPT35,
        budget: Budget = None,
        rate_limit: RateLimit = None
    ):
        self._pricing = PRICING_MODELS.get(pricing_model, PRICING_MODELS[CostModel.OPENAI_GPT35])
        self._budget = budget or Budget()
        self._rate_limit = rate_limit or RateLimit()
        
        # 实时计数器
        self._daily_consumption: Dict[str, Consumption] = {}
        self._monthly_consumption: Dict[str, float] = {}
        self._current_minute_requests = 0
        self._current_minute_tokens = 0
        self._current_day_requests = 0
        self._last_minute = time.time()
        self._last_day = self._get_today_str()
        
        # 回调函数
        self._budget_warning_callback = None
        self._budget_exhausted_callback = None
        self._rate_limit_callback = None
        
        self._lock = Lock()
    
    def set_pricing_model(self, model: CostModel):
        """设置定价模型"""
        self._pricing = PRICING_MODELS.get(model, self._pricing)
    
    def set_budget(self, budget: Budget):
        """设置预算"""
        self._budget = budget
    
    def set_rate_limit(self, rate_limit: RateLimit):
        """设置限流"""
        self._rate_limit = rate_limit
    
    def set_budget_warning_callback(self, callback: Callable):
        """设置预算警告回调"""
        self._budget_warning_callback = callback
    
    def set_budget_exhausted_callback(self, callback: Callable):
        """设置预算耗尽回调"""
        self._budget_exhausted_callback = callback
    
    def set_rate_limit_callback(self, callback: Callable):
        """设置限流回调"""
        self._rate_limit_callback = callback
    
    def calculate_cost(self, input_tokens: int, output_tokens: int) -> float:
        """
        计算单次请求的成本
        
        Args:
            input_tokens: 输入Token数
            output_tokens: 输出Token数
            
        Returns:
            成本（元）
        """
        input_cost = (input_tokens / 1000) * self._pricing.input_price_per_1k
        output_cost = (output_tokens / 1000) * self._pricing.output_price_per_1k
        return input_cost + output_cost
    
    def check_budget(self) -> bool:
        """
        检查预算是否充足
        
        Returns:
            True: 预算充足，可以继续请求
            False: 预算不足，需要拒绝请求
        """
        today = self._get_today_str()
        daily_cost = self._get_daily_cost(today)
        monthly_cost = self._get_monthly_cost()
        
        # 检查硬限制
        if daily_cost >= self._budget.daily_limit * self._budget.hard_limit_ratio:
            logger.error(f"每日预算即将耗尽: {daily_cost:.2f}/{self._budget.daily_limit}")
            if self._budget_exhausted_callback:
                self._budget_exhausted_callback("daily", daily_cost, self._budget.daily_limit)
            return False
        
        if monthly_cost >= self._budget.monthly_limit * self._budget.hard_limit_ratio:
            logger.error(f"每月预算即将耗尽: {monthly_cost:.2f}/{self._budget.monthly_limit}")
            if self._budget_exhausted_callback:
                self._budget_exhausted_callback("monthly", monthly_cost, self._budget.monthly_limit)
            return False
        
        # 检查软限制（警告）
        if daily_cost >= self._budget.daily_limit * self._budget.soft_limit_ratio:
            logger.warning(f"每日预算警告: {daily_cost:.2f}/{self._budget.daily_limit}")
            if self._budget_warning_callback:
                self._budget_warning_callback("daily", daily_cost, self._budget.daily_limit)
        
        if monthly_cost >= self._budget.monthly_limit * self._budget.soft_limit_ratio:
            logger.warning(f"每月预算警告: {monthly_cost:.2f}/{self._budget.monthly_limit}")
            if self._budget_warning_callback:
                self._budget_warning_callback("monthly", monthly_cost, self._budget.monthly_limit)
        
        return True
    
    def check_rate_limit(self) -> bool:
        """
        检查是否超出限流
        
        Returns:
            True: 在限流范围内
            False: 超出限流
        """
        self._update_counters()
        
        if self._current_minute_requests >= self._rate_limit.requests_per_minute:
            logger.warning(f"每分钟请求数超出限制: {self._current_minute_requests}/{self._rate_limit.requests_per_minute}")
            if self._rate_limit_callback:
                self._rate_limit_callback("requests_per_minute", self._current_minute_requests)
            return False
        
        if self._current_minute_tokens >= self._rate_limit.tokens_per_minute:
            logger.warning(f"每分钟Token数超出限制: {self._current_minute_tokens}/{self._rate_limit.tokens_per_minute}")
            if self._rate_limit_callback:
                self._rate_limit_callback("tokens_per_minute", self._current_minute_tokens)
            return False
        
        if self._current_day_requests >= self._rate_limit.requests_per_day:
            logger.warning(f"每日请求数超出限制: {self._current_day_requests}/{self._rate_limit.requests_per_day}")
            if self._rate_limit_callback:
                self._rate_limit_callback("requests_per_day", self._current_day_requests)
            return False
        
        return True
    
    def record_consumption(self, input_tokens: int, output_tokens: int, model: str = None):
        """
        记录消费
        
        Args:
            input_tokens: 输入Token数
            output_tokens: 输出Token数
            model: 模型名称
        """
        today = self._get_today_str()
        model = model or self._pricing.model_name
        
        cost = self.calculate_cost(input_tokens, output_tokens)
        
        with self._lock:
            # 更新每日消费
            if today not in self._daily_consumption:
                self._daily_consumption[today] = Consumption(date=today, model=model)
            
            consumption = self._daily_consumption[today]
            consumption.input_tokens += input_tokens
            consumption.output_tokens += output_tokens
            consumption.cost += cost
            consumption.requests += 1
            
            # 更新月度消费
            month = today[:7]  # YYYY-MM
            if month not in self._monthly_consumption:
                self._monthly_consumption[month] = 0.0
            self._monthly_consumption[month] += cost
            
            # 更新实时计数器
            self._current_day_requests += 1
            self._current_minute_tokens += input_tokens + output_tokens
        
        logger.info(f"消费记录: {input_tokens}输入 + {output_tokens}输出 = {cost:.4f}元")
    
    def get_daily_cost(self, date: str = None) -> float:
        """获取指定日期的消费"""
        if date is None:
            date = self._get_today_str()
        consumption = self._daily_consumption.get(date)
        return consumption.cost if consumption else 0.0
    
    def get_monthly_cost(self, month: str = None) -> float:
        """获取指定月份的消费"""
        if month is None:
            month = self._get_current_month_str()
        return self._monthly_consumption.get(month, 0.0)
    
    def get_consumption_summary(self) -> Dict[str, Any]:
        """获取消费汇总"""
        today = self._get_today_str()
        month = self._get_current_month_str()
        
        daily = self._daily_consumption.get(today)
        
        return {
            'daily_cost': self.get_daily_cost(today),
            'daily_limit': self._budget.daily_limit,
            'daily_remaining': max(0, self._budget.daily_limit - self.get_daily_cost(today)),
            'monthly_cost': self.get_monthly_cost(month),
            'monthly_limit': self._budget.monthly_limit,
            'monthly_remaining': max(0, self._budget.monthly_limit - self.get_monthly_cost(month)),
            'today_requests': daily.requests if daily else 0,
            'today_input_tokens': daily.input_tokens if daily else 0,
            'today_output_tokens': daily.output_tokens if daily else 0,
            'model_name': self._pricing.model_name
        }
    
    def estimate_cost(self, input_tokens: int, output_tokens: int = None) -> float:
        """
        估算请求成本
        
        Args:
            input_tokens: 输入Token数
            output_tokens: 预计输出Token数（可选）
            
        Returns:
            预计成本（元）
        """
        if output_tokens is None:
            # 默认按输入的50%估算输出
            output_tokens = int(input_tokens * 0.5)
        
        return self.calculate_cost(input_tokens, output_tokens)
    
    def suggest_model(self, required_tokens: int, budget: float) -> Optional[str]:
        """
        根据预算和需求推荐模型
        
        Args:
            required_tokens: 需要的Token数
            budget: 可用预算
            
        Returns:
            推荐的模型名称
        """
        for model_enum, pricing in PRICING_MODELS.items():
            if pricing.context_window >= required_tokens:
                estimated_cost = (required_tokens / 1000) * pricing.input_price_per_1k
                if estimated_cost <= budget:
                    return pricing.model_name
        
        return None
    
    def _update_counters(self):
        """更新计数器（处理时间窗口）"""
        current_time = time.time()
        
        # 检查是否进入新的分钟
        if current_time - self._last_minute >= 60:
            self._current_minute_requests = 0
            self._current_minute_tokens = 0
            self._last_minute = current_time
        
        # 检查是否进入新的一天
        today = self._get_today_str()
        if today != self._last_day:
            self._current_day_requests = 0
            self._last_day = today
    
    def _get_today_str(self) -> str:
        """获取今天的日期字符串"""
        return datetime.now().strftime("%Y-%m-%d")
    
    def _get_current_month_str(self) -> str:
        """获取当前月份字符串"""
        return datetime.now().strftime("%Y-%m")


class TokenOptimizer:
    """Token优化器"""
    
    def __init__(self):
        self._compression_enabled = True
        self._truncation_strategy = "smart"  # smart, left, right
        self._max_context_length = 8192
    
    def set_compression_enabled(self, enabled: bool):
        """设置是否启用压缩"""
        self._compression_enabled = enabled
    
    def set_truncation_strategy(self, strategy: str):
        """设置截断策略"""
        if strategy in ["smart", "left", "right"]:
            self._truncation_strategy = strategy
    
    def set_max_context_length(self, length: int):
        """设置最大上下文长度"""
        self._max_context_length = length
    
    def compress_text(self, text: str, max_length: int = None) -> str:
        """
        压缩文本
        
        Args:
            text: 原始文本
            max_length: 最大长度
            
        Returns:
            压缩后的文本
        """
        if not self._compression_enabled:
            return text
        
        if max_length is None:
            max_length = self._max_context_length
        
        if len(text) <= max_length:
            return text
        
        return self._truncate_text(text, max_length)
    
    def _truncate_text(self, text: str, max_length: int) -> str:
        """
        截断文本
        
        Args:
            text: 原始文本
            max_length: 最大长度
            
        Returns:
            截断后的文本
        """
        if self._truncation_strategy == "right":
            return text[:max_length] + "..."
        elif self._truncation_strategy == "left":
            return "..." + text[-max_length:]
        else:  # smart
            # 保留开头和结尾，中间截断
            prefix_length = int(max_length * 0.3)
            suffix_length = int(max_length * 0.6)
            ellipsis = "..."
            
            return text[:prefix_length] + ellipsis + text[-suffix_length:]
    
    def calculate_token_count(self, text: str) -> int:
        """
        估算Token数量
        
        Args:
            text: 文本
            
        Returns:
            估算的Token数
        """
        # 简单估算：1 Token ≈ 4 个字符
        return max(1, len(text) // 4)
    
    def optimize_prompt(self, prompt: str, max_tokens: int = 4096) -> str:
        """
        优化提示词
        
        Args:
            prompt: 原始提示词
            max_tokens: 最大Token数
            
        Returns:
            优化后的提示词
        """
        token_count = self.calculate_token_count(prompt)
        
        if token_count <= max_tokens:
            return prompt
        
        # 需要压缩
        target_char_count = max_tokens * 4
        return self.compress_text(prompt, target_char_count)


# 全局成本控制器和Token优化器
_global_cost_controller = CostController()
_global_token_optimizer = TokenOptimizer()


def get_cost_controller() -> CostController:
    """获取全局成本控制器"""
    return _global_cost_controller


def get_token_optimizer() -> TokenOptimizer:
    """获取全局Token优化器"""
    return _global_token_optimizer