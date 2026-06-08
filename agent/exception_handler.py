"""
异常处理机制
提供统一的异常处理、重试机制和熔断保护
"""
import logging
import time
import traceback
from typing import Callable, Any, Optional
from functools import wraps
from enum import Enum
from concurrent.futures import ThreadPoolExecutor, as_completed
from threading import Lock

logger = logging.getLogger(__name__)


class ErrorType(Enum):
    """错误类型枚举"""
    NETWORK_ERROR = "network_error"           # 网络错误
    TIMEOUT_ERROR = "timeout_error"           # 超时错误
    RATE_LIMIT_ERROR = "rate_limit_error"     # 限流错误
    AUTH_ERROR = "auth_error"                 # 认证错误
    SERVER_ERROR = "server_error"             # 服务端错误
    CLIENT_ERROR = "client_error"             # 客户端错误
    RETRY_EXHAUSTED = "retry_exhausted"       # 重试耗尽


class CustomException(Exception):
    """自定义异常基类"""
    
    def __init__(self, error_type: ErrorType, message: str, original_exception: Exception = None):
        super().__init__(message)
        self.error_type = error_type
        self.original_exception = original_exception
        self.timestamp = time.time()
    
    def to_dict(self):
        return {
            'error_type': self.error_type.value,
            'message': str(self),
            'timestamp': self.timestamp,
            'original_exception': str(self.original_exception) if self.original_exception else None
        }


class RetryConfig:
    """重试配置"""
    
    def __init__(
        self,
        max_retries: int = 3,
        initial_delay: float = 1.0,
        backoff_factor: float = 2.0,
        retry_on_errors: tuple = (Exception,),
        max_delay: float = 30.0
    ):
        """
        Args:
            max_retries: 最大重试次数
            initial_delay: 初始延迟（秒）
            backoff_factor: 退避因子
            retry_on_errors: 需要重试的异常类型
            max_delay: 最大延迟（秒）
        """
        self.max_retries = max_retries
        self.initial_delay = initial_delay
        self.backoff_factor = backoff_factor
        self.retry_on_errors = retry_on_errors
        self.max_delay = max_delay


class CircuitBreaker:
    """熔断保护器"""
    
    def __init__(
        self,
        failure_threshold: int = 5,
        recovery_timeout: int = 30,
        half_open_max_calls: int = 3
    ):
        """
        Args:
            failure_threshold: 失败阈值，超过后触发熔断
            recovery_timeout: 熔断恢复时间（秒）
            half_open_max_calls: 半开状态下允许的最大调用数
        """
        self.failure_threshold = failure_threshold
        self.recovery_timeout = recovery_timeout
        self.half_open_max_calls = half_open_max_calls
        
        self._failure_count = 0
        self._last_failure_time = 0
        self._state = 'CLOSED'  # CLOSED, OPEN, HALF_OPEN
        self._lock = Lock()
    
    @property
    def state(self):
        """获取当前状态"""
        with self._lock:
            if self._state == 'OPEN':
                # 检查是否可以进入半开状态
                if time.time() - self._last_failure_time >= self.recovery_timeout:
                    self._state = 'HALF_OPEN'
                    self._failure_count = 0
            return self._state
    
    def record_success(self):
        """记录成功调用"""
        with self._lock:
            self._failure_count = 0
            self._state = 'CLOSED'
    
    def record_failure(self):
        """记录失败调用"""
        with self._lock:
            self._failure_count += 1
            self._last_failure_time = time.time()
            
            if self._failure_count >= self.failure_threshold:
                self._state = 'OPEN'
    
    def allow_request(self) -> bool:
        """判断是否允许请求"""
        current_state = self.state
        
        if current_state == 'CLOSED':
            return True
        elif current_state == 'HALF_OPEN':
            # 半开状态下限制调用次数
            return self._failure_count < self.half_open_max_calls
        else:  # OPEN
            return False


def retry(config: RetryConfig = None):
    """
    重试装饰器
    
    Args:
        config: 重试配置
    
    Example:
        @retry(RetryConfig(max_retries=3, initial_delay=1.0))
        def call_api():
            # API调用逻辑
            pass
    """
    if config is None:
        config = RetryConfig()
    
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args, **kwargs) -> Any:
            last_exception = None
            delay = config.initial_delay
            
            for attempt in range(config.max_retries + 1):
                try:
                    return func(*args, **kwargs)
                except config.retry_on_errors as e:
                    last_exception = e
                    logger.warning(f"调用失败 (尝试 {attempt + 1}/{config.max_retries + 1}): {e}")
                    
                    if attempt < config.max_retries:
                        time.sleep(min(delay, config.max_delay))
                        delay *= config.backoff_factor
                    else:
                        logger.error(f"重试耗尽，共尝试 {config.max_retries + 1} 次")
            
            raise CustomException(
                error_type=ErrorType.RETRY_EXHAUSTED,
                message=f"重试耗尽: {str(last_exception)}",
                original_exception=last_exception
            )
        
        return wrapper
    return decorator


def circuit_breaker(circuit: CircuitBreaker = None):
    """
    熔断保护装饰器
    
    Args:
        circuit: 熔断器实例
    
    Example:
        breaker = CircuitBreaker()
        
        @circuit_breaker(breaker)
        def call_api():
            # API调用逻辑
            pass
    """
    if circuit is None:
        circuit = CircuitBreaker()
    
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args, **kwargs) -> Any:
            if not circuit.allow_request():
                logger.error(f"熔断器已打开，拒绝请求")
                raise CustomException(
                    error_type=ErrorType.SERVER_ERROR,
                    message="服务暂时不可用，请稍后重试"
                )
            
            try:
                result = func(*args, **kwargs)
                circuit.record_success()
                return result
            except Exception as e:
                circuit.record_failure()
                raise
        
        return wrapper
    return decorator


def async_retry(config: RetryConfig = None):
    """
    异步重试装饰器
    
    Args:
        config: 重试配置
    """
    if config is None:
        config = RetryConfig()
    
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        async def wrapper(*args, **kwargs) -> Any:
            last_exception = None
            delay = config.initial_delay
            
            for attempt in range(config.max_retries + 1):
                try:
                    return await func(*args, **kwargs)
                except config.retry_on_errors as e:
                    last_exception = e
                    logger.warning(f"异步调用失败 (尝试 {attempt + 1}/{config.max_retries + 1}): {e}")
                    
                    if attempt < config.max_retries:
                        await asyncio.sleep(min(delay, config.max_delay))
                        delay *= config.backoff_factor
                    else:
                        logger.error(f"异步重试耗尽")
            
            raise CustomException(
                error_type=ErrorType.RETRY_EXHAUSTED,
                message=f"异步重试耗尽: {str(last_exception)}",
                original_exception=last_exception
            )
        
        return wrapper
    return decorator


class ExceptionHandler:
    """异常处理器"""
    
    def __init__(self):
        self._error_handlers = {}
        self._default_handler = self._default_error_handler
    
    def register_handler(self, error_type: ErrorType, handler: Callable):
        """
        注册错误处理器
        
        Args:
            error_type: 错误类型
            handler: 处理器函数
        """
        self._error_handlers[error_type] = handler
    
    def handle(self, exception: Exception) -> Any:
        """
        处理异常
        
        Args:
            exception: 异常对象
            
        Returns:
            处理结果或重新抛出异常
        """
        # 检查是否是自定义异常
        if isinstance(exception, CustomException):
            handler = self._error_handlers.get(exception.error_type)
            if handler:
                try:
                    return handler(exception)
                except Exception as e:
                    logger.error(f"错误处理器执行失败: {e}")
                    return self._default_handler(exception)
            else:
                return self._default_handler(exception)
        
        # 处理标准异常
        return self._default_handler(exception)
    
    def _default_error_handler(self, exception: Exception) -> None:
        """默认错误处理器"""
        logger.error(f"未处理的异常: {type(exception).__name__}: {exception}")
        logger.error(traceback.format_exc())
        raise exception


# 全局异常处理器
_global_exception_handler = ExceptionHandler()

def get_exception_handler() -> ExceptionHandler:
    """获取全局异常处理器"""
    return _global_exception_handler


# 预定义的错误处理器示例
def handle_network_error(exc: CustomException):
    """处理网络错误"""
    logger.error(f"网络错误: {exc.message}")
    # 可以在这里添加告警逻辑
    return {"error": "network_error", "message": "网络连接失败，请检查网络设置"}


def handle_timeout_error(exc: CustomException):
    """处理超时错误"""
    logger.error(f"超时错误: {exc.message}")
    return {"error": "timeout_error", "message": "请求超时，请稍后重试"}


def handle_rate_limit_error(exc: CustomException):
    """处理限流错误"""
    logger.error(f"限流错误: {exc.message}")
    return {"error": "rate_limit_error", "message": "请求过于频繁，请稍后重试"}


# 注册预定义的错误处理器
_global_exception_handler.register_handler(ErrorType.NETWORK_ERROR, handle_network_error)
_global_exception_handler.register_handler(ErrorType.TIMEOUT_ERROR, handle_timeout_error)
_global_exception_handler.register_handler(ErrorType.RATE_LIMIT_ERROR, handle_rate_limit_error)