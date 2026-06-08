"""
系统优化集成模块
将异常处理、可观测性、成本控制和弹性伸缩整合到现有系统
"""
import logging
import time
from typing import Dict, Any, Optional
from fastapi import FastAPI, Request, Response
from fastapi.middleware.cors import CORSMiddleware
from starlette.middleware.base import BaseHTTPMiddleware

logger = logging.getLogger(__name__)


class SystemOptimizer:
    """系统优化器"""
    
    def __init__(self):
        self._initialized = False
        
        # 延迟导入以避免循环依赖
        self._exception_handler = None
        self._observability = None
        self._cost_control = None
        self._scaling = None
        self._alerting = None
    
    def initialize(self):
        """初始化所有优化组件"""
        if self._initialized:
            return
        
        # 导入组件
        from .exception_handler import (
            get_exception_handler, RetryConfig, retry, circuit_breaker,
            CircuitBreaker, CustomException, ErrorType
        )
        from .observability import (
            get_tracer, get_metrics_collector, get_health_checker,
            traced, record_metric, METRIC_NAMES
        )
        from .cost_control import (
            get_cost_controller, get_token_optimizer, CostModel
        )
        from .scaling import (
            get_resource_monitor, get_auto_scaler, get_load_balancer,
            ScalePolicy
        )
        from .alerting import (
            get_alert_manager, AlertSeverity, NotificationChannel
        )
        
        # 保存类引用
        self._ScalePolicy = ScalePolicy
        self._AlertSeverity = AlertSeverity
        self._NotificationChannel = NotificationChannel
        
        self._exception_handler = get_exception_handler()
        self._tracer = get_tracer()
        self._metrics = get_metrics_collector()
        self._health_checker = get_health_checker()
        self._cost_controller = get_cost_controller()
        self._token_optimizer = get_token_optimizer()
        self._resource_monitor = get_resource_monitor()
        self._auto_scaler = get_auto_scaler()
        self._load_balancer = get_load_balancer()
        self._alert_manager = get_alert_manager()
        
        # 配置组件
        self._configure_exception_handler()
        self._configure_cost_control()
        self._configure_scaling()
        self._configure_alerting()
        
        # 注册健康检查
        self._register_health_checks()
        
        self._initialized = True
        logger.info("系统优化组件初始化完成")
    
    def _configure_exception_handler(self):
        """配置异常处理"""
        # 可以在这里添加自定义的错误处理器
        pass
    
    def _configure_cost_control(self):
        """配置成本控制"""
        # 设置预算警告回调
        self._cost_controller.set_budget_warning_callback(
            self._on_budget_warning
        )
        self._cost_controller.set_budget_exhausted_callback(
            self._on_budget_exhausted
        )
        self._cost_controller.set_rate_limit_callback(
            self._on_rate_limit
        )
    
    def _configure_scaling(self):
        """配置弹性伸缩"""
        policy = self._ScalePolicy(
            cpu_scale_up_threshold=70.0,
            cpu_scale_down_threshold=30.0,
            memory_scale_up_threshold=75.0,
            memory_scale_down_threshold=35.0,
            min_replicas=1,
            max_replicas=5,
            scale_up_window=60,
            scale_down_window=120
        )
        self._auto_scaler.set_policy(policy)
        self._auto_scaler.set_scale_event_callback(self._on_scale_event)
        
        # 启动自动伸缩器
        self._auto_scaler.start()
    
    def _configure_alerting(self):
        """配置告警"""
        # 添加更多通知渠道（如果需要）
        # self._alert_manager.set_notification_channels([
        #     NotificationChannel.LOG,
        #     NotificationChannel.WEBHOOK
        # ])
        
        # 设置告警回调
        self._alert_manager.set_alert_trigger_callback(self._on_alert_trigger)
        self._alert_manager.set_alert_resolve_callback(self._on_alert_resolve)
    
    def _register_health_checks(self):
        """注册健康检查"""
        # 注册Redis健康检查
        async def check_redis():
            try:
                from .memory.redis_memory import RedisMemory
                redis = RedisMemory()
                if await redis.ping():
                    return "healthy", "Redis连接正常"
                return "degraded", "Redis连接异常"
            except Exception as e:
                return "unhealthy", str(e)
        
        # 注册MySQL健康检查
        async def check_mysql():
            try:
                from sqlalchemy import create_engine
                from agent.settings import settings
                engine = create_engine(settings.DATABASE_URL)
                with engine.connect():
                    return "healthy", "MySQL连接正常"
            except Exception as e:
                return "unhealthy", str(e)
        
        # 注册Milvus健康检查（如果已配置）
        async def check_milvus():
            try:
                from .memory.milvus_memory import MilvusMemory
                milvus = MilvusMemory()
                if milvus.is_available():
                    return "healthy", "Milvus连接正常"
                return "degraded", "Milvus不可用"
            except Exception as e:
                return "unhealthy", str(e)
        
        self._health_checker.register_check("redis", check_redis)
        self._health_checker.register_check("mysql", check_mysql)
        self._health_checker.register_check("milvus", check_milvus)
    
    def _on_budget_warning(self, period: str, current: float, limit: float):
        """预算警告回调"""
        logger.warning(f"预算警告 ({period}): {current:.2f}/{limit}")
        self._metrics.counter(
            "budget_warnings",
            period=period
        )
    
    def _on_budget_exhausted(self, period: str, current: float, limit: float):
        """预算耗尽回调"""
        logger.error(f"预算耗尽 ({period}): {current:.2f}/{limit}")
        self._metrics.counter(
            "budget_exhausted",
            period=period
        )
    
    def _on_rate_limit(self, limit_type: str, current: int):
        """限流回调"""
        logger.warning(f"限流触发: {limit_type} = {current}")
        self._metrics.counter(
            "rate_limit_triggers",
            limit_type=limit_type
        )
    
    def _on_scale_event(self, event):
        """伸缩事件回调"""
        logger.info(f"伸缩事件: {event.event_type.value} - {event.reason}")
        self._metrics.counter(
            "scale_events",
            event_type=event.event_type.value
        )
    
    def _on_alert_trigger(self, alert):
        """告警触发回调"""
        logger.warning(f"告警触发: {alert.rule_name} - {alert.message}")
    
    def _on_alert_resolve(self, alert):
        """告警解决回调"""
        logger.info(f"告警解决: {alert.rule_name}")
    
    def get_fastapi_middleware(self) -> BaseHTTPMiddleware:
        """获取FastAPI中间件"""
        class OptimizerMiddleware(BaseHTTPMiddleware):
            def __init__(self, app: FastAPI, optimizer: SystemOptimizer):
                super().__init__(app)
                self.optimizer = optimizer
            
            async def dispatch(self, request: Request, call_next):
                start_time = time.time()
                request_id = str(id(request))
                
                # 记录请求指标
                self.optimizer._metrics.counter(
                    METRIC_NAMES['API_REQUESTS'],
                    endpoint=request.url.path,
                    method=request.method
                )
                
                # 检查预算和限流
                if not self.optimizer._cost_controller.check_budget():
                    return Response(
                        content="预算不足，请联系管理员",
                        status_code=402
                    )
                
                if not self.optimizer._cost_controller.check_rate_limit():
                    return Response(
                        content="请求过于频繁，请稍后重试",
                        status_code=429
                    )
                
                try:
                    response = await call_next(request)
                    
                    # 记录响应时间
                    latency = time.time() - start_time
                    self.optimizer._metrics.histogram(
                        METRIC_NAMES['API_LATENCY'],
                        latency,
                        endpoint=request.url.path,
                        status_code=response.status_code
                    )
                    
                    return response
                except Exception as e:
                    # 记录错误
                    self.optimizer._metrics.counter(
                        METRIC_NAMES['API_ERRORS'],
                        endpoint=request.url.path,
                        error_type=type(e).__name__
                    )
                    
                    # 使用异常处理器处理
                    result = self.optimizer._exception_handler.handle(e)
                    if isinstance(result, dict) and 'error' in result:
                        return Response(
                            content=str(result.get('message', str(e))),
                            status_code=500
                        )
                    
                    raise
        
        return OptimizerMiddleware
    
    def register_middlewares(self, app: FastAPI):
        """注册中间件"""
        app.add_middleware(
            self.get_fastapi_middleware(),
            optimizer=self
        )
    
    def record_llm_usage(self, input_tokens: int, output_tokens: int, model: str = None):
        """记录LLM使用"""
        # 记录Token使用
        self._cost_controller.record_consumption(input_tokens, output_tokens, model)
        
        # 更新指标
        self._metrics.counter(
            METRIC_NAMES['LLM_CALLS'],
            model=model or "unknown"
        )
        self._metrics.counter(
            METRIC_NAMES['TOKEN_USAGE'],
            input_tokens=input_tokens,
            output_tokens=output_tokens,
            model=model or "unknown"
        )
    
    def evaluate_alerts(self):
        """评估告警规则"""
        # 获取当前指标
        metrics = {
            'cpu_usage': self._resource_monitor.get_current_metrics().cpu_usage,
            'memory_usage': self._resource_monitor.get_current_metrics().memory_usage,
            'api_error_rate': 0,  # 需要从其他地方获取
            'api_latency_p95': 0,  # 需要从其他地方获取
            'cache_hit_rate': 0,  # 需要从其他地方获取
            'db_connections': 0,  # 需要从其他地方获取
            'llm_error_rate': 0,  # 需要从其他地方获取
            'llm_timeout_rate': 0,  # 需要从其他地方获取
        }
        
        # 评估告警
        self._alert_manager.evaluate_rules(metrics)
    
    def get_status(self) -> Dict[str, Any]:
        """获取系统状态"""
        return {
            'initialized': self._initialized,
            'cost_control': self._cost_controller.get_consumption_summary(),
            'scaling': self._auto_scaler.get_status(),
            'alerts': [
                {
                    'rule_name': a.rule_name,
                    'severity': a.severity.value,
                    'status': a.status.value,
                    'message': a.message,
                    'timestamp': a.timestamp
                }
                for a in self._alert_manager.get_alerts()
            ]
        }


# 创建全局系统优化器
_global_optimizer = SystemOptimizer()


def get_optimizer() -> SystemOptimizer:
    """获取全局系统优化器"""
    return _global_optimizer


def initialize_optimizer():
    """初始化系统优化器"""
    _global_optimizer.initialize()


# FastAPI启动时初始化
def setup_optimizer_on_startup(app: FastAPI):
    """在FastAPI启动时设置优化器"""
    @app.on_event("startup")
    async def startup_event():
        initialize_optimizer()
        _global_optimizer.register_middlewares(app)
        logger.info("系统优化器已集成到FastAPI应用")
    
    return startup_event


# 方便的装饰器
def optimized_endpoint(func=None, *, retry_config=None, circuit=None):
    """
    优化端点装饰器
    自动添加重试、熔断和指标记录
    
    Example:
        @optimized_endpoint
        async def my_endpoint():
            pass
    """
    def decorator(func):
        # 添加重试
        if retry_config:
            func = retry(retry_config)(func)
        
        # 添加熔断
        if circuit:
            func = circuit_breaker(circuit)(func)
        
        # 添加追踪
        func = traced()(func)
        
        # 添加指标记录
        func = record_metric("api_requests")(func)
        
        return func
    
    if func:
        return decorator(func)
    return decorator