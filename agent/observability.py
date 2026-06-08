"""
可观测性模块
提供日志、指标、追踪和健康检查功能
"""
import logging
import time
import uuid
import json
from typing import Dict, Any, Optional, List, Callable
from datetime import datetime
from collections import defaultdict
from threading import Lock
from dataclasses import dataclass
from enum import Enum
from functools import wraps

logger = logging.getLogger(__name__)


class TraceLevel(Enum):
    """追踪级别"""
    DEBUG = "debug"
    INFO = "info"
    WARNING = "warning"
    ERROR = "error"


@dataclass
class Span:
    """追踪跨度"""
    trace_id: str
    span_id: str
    parent_span_id: Optional[str]
    operation_name: str
    start_time: float
    end_time: Optional[float] = None
    status_code: str = "OK"
    attributes: Dict[str, Any] = None
    events: List[Dict[str, Any]] = None
    
    def __post_init__(self):
        if self.attributes is None:
            self.attributes = {}
        if self.events is None:
            self.events = []
    
    @property
    def duration(self) -> float:
        """计算持续时间"""
        if self.end_time:
            return self.end_time - self.start_time
        return time.time() - self.start_time
    
    def add_event(self, name: str, attributes: Dict[str, Any] = None):
        """添加事件"""
        self.events.append({
            'name': name,
            'timestamp': time.time(),
            'attributes': attributes or {}
        })
    
    def to_dict(self):
        """转换为字典"""
        return {
            'trace_id': self.trace_id,
            'span_id': self.span_id,
            'parent_span_id': self.parent_span_id,
            'operation_name': self.operation_name,
            'start_time': self.start_time,
            'end_time': self.end_time,
            'duration': self.duration,
            'status_code': self.status_code,
            'attributes': self.attributes,
            'events': self.events
        }


class Tracer:
    """分布式追踪器"""
    
    def __init__(self, service_name: str = "hr_agent"):
        self.service_name = service_name
        self._spans: Dict[str, Span] = {}
        self._lock = Lock()
    
    def start_span(self, operation_name: str, parent_span_id: Optional[str] = None) -> Span:
        """
        启动一个新的追踪跨度
        
        Args:
            operation_name: 操作名称
            parent_span_id: 父跨度ID
            
        Returns:
            新创建的跨度
        """
        trace_id = str(uuid.uuid4())
        span_id = str(uuid.uuid4())
        
        span = Span(
            trace_id=trace_id,
            span_id=span_id,
            parent_span_id=parent_span_id,
            operation_name=operation_name,
            start_time=time.time()
        )
        
        with self._lock:
            self._spans[span_id] = span
        
        logger.debug(f"Started span: {operation_name} (trace_id={trace_id}, span_id={span_id})")
        return span
    
    def end_span(self, span_id: str, status_code: str = "OK"):
        """
        结束一个追踪跨度
        
        Args:
            span_id: 跨度ID
            status_code: 状态码
        """
        with self._lock:
            span = self._spans.get(span_id)
            if span:
                span.end_time = time.time()
                span.status_code = status_code
                logger.debug(f"Ended span: {span.operation_name} (duration={span.duration:.2f}s)")
    
    def get_span(self, span_id: str) -> Optional[Span]:
        """获取跨度信息"""
        return self._spans.get(span_id)
    
    def record_trace(self, span: Span):
        """记录追踪信息到日志"""
        trace_info = span.to_dict()
        logger.info(f"Trace recorded: {json.dumps(trace_info, indent=2)}")


class MetricType(Enum):
    """指标类型"""
    COUNTER = "counter"      # 计数器，只能增加
    GAUGE = "gauge"          # 仪表盘，可以增减
    HISTOGRAM = "histogram"  # 直方图，统计分布
    SUMMARY = "summary"      # 摘要统计


@dataclass
class Metric:
    """指标数据"""
    name: str
    type: MetricType
    value: float = 0.0
    labels: Dict[str, str] = None
    timestamp: float = None
    samples: List[float] = None
    
    def __post_init__(self):
        if self.labels is None:
            self.labels = {}
        if self.timestamp is None:
            self.timestamp = time.time()
        if self.samples is None:
            self.samples = []


class MetricsCollector:
    """指标收集器"""
    
    def __init__(self):
        self._metrics: Dict[str, Metric] = {}
        self._lock = Lock()
    
    def counter(self, name: str, value: float = 1.0, **labels):
        """
        增加计数器
        
        Args:
            name: 指标名称
            value: 增量值
            **labels: 标签
        """
        key = self._get_metric_key(name, labels)
        
        with self._lock:
            if key not in self._metrics:
                self._metrics[key] = Metric(
                    name=name,
                    type=MetricType.COUNTER,
                    labels=labels
                )
            self._metrics[key].value += value
            self._metrics[key].timestamp = time.time()
        
        logger.debug(f"Counter {name} += {value} ({labels})")
    
    def gauge(self, name: str, value: float, **labels):
        """
        设置仪表盘值
        
        Args:
            name: 指标名称
            value: 当前值
            **labels: 标签
        """
        key = self._get_metric_key(name, labels)
        
        with self._lock:
            if key not in self._metrics:
                self._metrics[key] = Metric(
                    name=name,
                    type=MetricType.GAUGE,
                    labels=labels
                )
            self._metrics[key].value = value
            self._metrics[key].timestamp = time.time()
        
        logger.debug(f"Gauge {name} = {value} ({labels})")
    
    def histogram(self, name: str, value: float, **labels):
        """
        记录直方图样本
        
        Args:
            name: 指标名称
            value: 样本值
            **labels: 标签
        """
        key = self._get_metric_key(name, labels)
        
        with self._lock:
            if key not in self._metrics:
                self._metrics[key] = Metric(
                    name=name,
                    type=MetricType.HISTOGRAM,
                    labels=labels,
                    samples=[]
                )
            self._metrics[key].samples.append(value)
            self._metrics[key].value = len(self._metrics[key].samples)
            self._metrics[key].timestamp = time.time()
        
        logger.debug(f"Histogram {name} + sample {value} ({labels})")
    
    def summary(self, name: str, value: float, **labels):
        """
        记录摘要样本
        
        Args:
            name: 指标名称
            value: 样本值
            **labels: 标签
        """
        key = self._get_metric_key(name, labels)
        
        with self._lock:
            if key not in self._metrics:
                self._metrics[key] = Metric(
                    name=name,
                    type=MetricType.SUMMARY,
                    labels=labels,
                    samples=[]
                )
            self._metrics[key].samples.append(value)
            self._metrics[key].value = sum(self._metrics[key].samples) / len(self._metrics[key].samples) if self._metrics[key].samples else 0
            self._metrics[key].timestamp = time.time()
        
        logger.debug(f"Summary {name} + sample {value} ({labels})")
    
    def get_metrics(self) -> Dict[str, Metric]:
        """获取所有指标"""
        with self._lock:
            return dict(self._metrics)
    
    def get_metric(self, name: str, **labels) -> Optional[Metric]:
        """获取指定指标"""
        key = self._get_metric_key(name, labels)
        return self._metrics.get(key)
    
    def _get_metric_key(self, name: str, labels: Dict[str, str]) -> str:
        """生成指标唯一键"""
        label_str = ",".join(f"{k}={v}" for k, v in sorted(labels.items()))
        return f"{name}|{label_str}"


class HealthStatus(Enum):
    """健康状态"""
    HEALTHY = "healthy"
    DEGRADED = "degraded"
    UNHEALTHY = "unhealthy"


@dataclass
class HealthCheckResult:
    """健康检查结果"""
    service: str
    status: HealthStatus
    message: str
    latency: float
    timestamp: float = None
    
    def __post_init__(self):
        if self.timestamp is None:
            self.timestamp = time.time()


class HealthChecker:
    """健康检查器"""
    
    def __init__(self):
        self._checks: Dict[str, Callable] = {}
    
    def register_check(self, name: str, check_func: Callable):
        """
        注册健康检查
        
        Args:
            name: 检查名称
            check_func: 检查函数，返回 (status: HealthStatus, message: str)
        """
        self._checks[name] = check_func
    
    async def check_all(self) -> List[HealthCheckResult]:
        """执行所有健康检查"""
        results = []
        
        for name, check_func in self._checks.items():
            start_time = time.time()
            try:
                status, message = await check_func()
            except Exception as e:
                status = HealthStatus.UNHEALTHY
                message = str(e)
            latency = time.time() - start_time
            
            results.append(HealthCheckResult(
                service=name,
                status=status,
                message=message,
                latency=latency
            ))
            
            logger.info(f"Health check [{name}]: {status.value} ({latency:.2f}s) - {message}")
        
        return results
    
    def get_overall_status(self) -> HealthStatus:
        """获取整体健康状态"""
        # 简化实现，实际应执行检查
        return HealthStatus.HEALTHY


class LoggingConfig:
    """日志配置"""
    
    def __init__(
        self,
        level: str = "INFO",
        format: str = "%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        date_format: str = "%Y-%m-%d %H:%M:%S",
        file_path: Optional[str] = None,
        max_file_size: int = 10 * 1024 * 1024,  # 10MB
        backup_count: int = 5
    ):
        self.level = level
        self.format = format
        self.date_format = date_format
        self.file_path = file_path
        self.max_file_size = max_file_size
        self.backup_count = backup_count


def setup_logging(config: LoggingConfig):
    """
    设置日志系统
    
    Args:
        config: 日志配置
    """
    level = getattr(logging, config.level.upper())
    
    handlers = [logging.StreamHandler()]
    
    if config.file_path:
        from logging.handlers import RotatingFileHandler
        file_handler = RotatingFileHandler(
            config.file_path,
            maxBytes=config.max_file_size,
            backupCount=config.backup_count,
            encoding='utf-8'
        )
        handlers.append(file_handler)
    
    logging.basicConfig(
        level=level,
        format=config.format,
        datefmt=config.date_format,
        handlers=handlers
    )
    
    logger.info(f"Logging initialized with level: {config.level}")


# 全局可观测性组件
_global_tracer = Tracer()
_global_metrics = MetricsCollector()
_global_health_checker = HealthChecker()


def get_tracer() -> Tracer:
    """获取全局追踪器"""
    return _global_tracer


def get_metrics_collector() -> MetricsCollector:
    """获取全局指标收集器"""
    return _global_metrics


def get_health_checker() -> HealthChecker:
    """获取全局健康检查器"""
    return _global_health_checker


# 方便的装饰器
def traced(operation_name: Optional[str] = None):
    """
    追踪装饰器
    
    Args:
        operation_name: 操作名称，默认为函数名
    
    Example:
        @traced
        def process_data():
            pass
    """
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args, **kwargs):
            name = operation_name or func.__name__
            span = _global_tracer.start_span(name)
            
            try:
                result = func(*args, **kwargs)
                span.status_code = "OK"
                return result
            except Exception as e:
                span.status_code = "ERROR"
                span.add_event("exception", {"error": str(e)})
                raise
            finally:
                _global_tracer.end_span(span.span_id)
        
        return wrapper
    return decorator


def record_metric(metric_name: str, metric_type: MetricType = MetricType.COUNTER):
    """
    记录指标装饰器
    
    Args:
        metric_name: 指标名称
        metric_type: 指标类型
    
    Example:
        @record_metric("api_requests")
        def handle_request():
            pass
    """
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args, **kwargs):
            start_time = time.time()
            
            try:
                result = func(*args, **kwargs)
                
                if metric_type == MetricType.COUNTER:
                    _global_metrics.counter(metric_name)
                elif metric_type == MetricType.HISTOGRAM:
                    _global_metrics.histogram(f"{metric_name}_duration", time.time() - start_time)
                
                return result
            except Exception as e:
                _global_metrics.counter(f"{metric_name}_errors")
                raise
        
        return wrapper
    return decorator


# 预定义的指标名称
METRIC_NAMES = {
    'API_REQUESTS': 'api_requests',
    'API_ERRORS': 'api_errors',
    'API_LATENCY': 'api_latency',
    'TOKEN_USAGE': 'token_usage',
    'MEMORY_HITS': 'memory_hits',
    'MEMORY_MISSES': 'memory_misses',
    'CACHE_HITS': 'cache_hits',
    'CACHE_MISSES': 'cache_misses',
    'LLM_CALLS': 'llm_calls',
    'LLM_ERRORS': 'llm_errors',
    'RATE_LIMITS': 'rate_limits',
    'ACTIVE_CONNECTIONS': 'active_connections',
    'QUEUE_SIZE': 'queue_size'
}