"""
弹性伸缩模块
提供资源监控、自动伸缩和负载均衡功能
"""
import logging
import time
import psutil
from typing import Dict, Any, Optional, List, Callable
from datetime import datetime, timedelta
from threading import Lock, Thread
from dataclasses import dataclass
from enum import Enum

logger = logging.getLogger(__name__)


class ScaleEventType(Enum):
    """伸缩事件类型"""
    SCALE_UP = "scale_up"       # 扩容
    SCALE_DOWN = "scale_down"   # 缩容
    SCALE_OUT = "scale_out"     # 横向扩展
    SCALE_IN = "scale_in"       # 横向收缩
    ALERT = "alert"             # 告警


@dataclass
class ScaleEvent:
    """伸缩事件"""
    event_type: ScaleEventType
    timestamp: float
    reason: str
    current_replicas: int
    target_replicas: int
    metrics: Dict[str, float]


@dataclass
class ScalePolicy:
    """伸缩策略"""
    # CPU阈值
    cpu_scale_up_threshold: float = 70.0    # CPU使用率超过此值触发扩容
    cpu_scale_down_threshold: float = 30.0  # CPU使用率低于此值触发缩容
    
    # 内存阈值
    memory_scale_up_threshold: float = 75.0
    memory_scale_down_threshold: float = 35.0
    
    # 连接数阈值
    connection_scale_up_threshold: int = 1000
    connection_scale_down_threshold: int = 200
    
    # 请求队列阈值
    queue_scale_up_threshold: int = 500
    queue_scale_down_threshold: int = 50
    
    # 时间窗口（秒）- 连续满足条件才触发伸缩
    scale_up_window: int = 60
    scale_down_window: int = 120
    
    # 实例数量限制
    min_replicas: int = 1
    max_replicas: int = 10
    
    # 伸缩步长
    scale_up_step: int = 1
    scale_down_step: int = 1


@dataclass
class ResourceMetrics:
    """资源指标"""
    timestamp: float
    cpu_usage: float           # CPU使用率 (%)
    memory_usage: float        # 内存使用率 (%)
    disk_usage: float          # 磁盘使用率 (%)
    network_io: float          # 网络IO (MB/s)
    active_connections: int    # 活跃连接数
    pending_requests: int      # 待处理请求数
    request_rate: float        # 请求速率 (req/s)
    error_rate: float          # 错误率 (%)


class ResourceMonitor:
    """资源监控器"""
    
    def __init__(self, interval: int = 5):
        """
        Args:
            interval: 监控间隔（秒）
        """
        self._interval = interval
        self._running = False
        self._thread = None
        self._metrics_history: List[ResourceMetrics] = []
        self._max_history_size = 60  # 保留60个样本（5分钟@5秒间隔）
        self._lock = Lock()
        
        # 回调函数
        self._metric_update_callback = None
    
    def set_metric_update_callback(self, callback: Callable):
        """设置指标更新回调"""
        self._metric_update_callback = callback
    
    def start(self):
        """启动监控"""
        if self._running:
            return
        
        self._running = True
        self._thread = Thread(target=self._monitor_loop, daemon=True)
        self._thread.start()
        logger.info("资源监控器已启动")
    
    def stop(self):
        """停止监控"""
        self._running = False
        if self._thread:
            self._thread.join()
        logger.info("资源监控器已停止")
    
    def get_current_metrics(self) -> ResourceMetrics:
        """获取当前资源指标"""
        cpu_usage = psutil.cpu_percent(interval=0.1)
        memory = psutil.virtual_memory()
        disk = psutil.disk_usage('/')
        
        # 网络IO（简化计算）
        net_io = psutil.net_io_counters()
        network_io = (net_io.bytes_sent + net_io.bytes_recv) / (1024 * 1024)
        
        # 获取活跃连接数（简化实现）
        try:
            connections = len(psutil.net_connections())
        except:
            connections = 0
        
        return ResourceMetrics(
            timestamp=time.time(),
            cpu_usage=cpu_usage,
            memory_usage=memory.percent,
            disk_usage=disk.percent,
            network_io=network_io,
            active_connections=connections,
            pending_requests=0,  # 需要外部设置
            request_rate=0,      # 需要外部设置
            error_rate=0         # 需要外部设置
        )
    
    def get_historical_metrics(self, window_seconds: int = 60) -> List[ResourceMetrics]:
        """获取历史指标"""
        with self._lock:
            cutoff_time = time.time() - window_seconds
            return [m for m in self._metrics_history if m.timestamp >= cutoff_time]
    
    def get_average_metrics(self, window_seconds: int = 60) -> ResourceMetrics:
        """获取平均指标"""
        history = self.get_historical_metrics(window_seconds)
        
        if not history:
            return self.get_current_metrics()
        
        count = len(history)
        return ResourceMetrics(
            timestamp=time.time(),
            cpu_usage=sum(m.cpu_usage for m in history) / count,
            memory_usage=sum(m.memory_usage for m in history) / count,
            disk_usage=sum(m.disk_usage for m in history) / count,
            network_io=sum(m.network_io for m in history) / count,
            active_connections=sum(m.active_connections for m in history) // count,
            pending_requests=sum(m.pending_requests for m in history) // count,
            request_rate=sum(m.request_rate for m in history) / count,
            error_rate=sum(m.error_rate for m in history) / count
        )
    
    def set_additional_metrics(self, pending_requests: int, request_rate: float, error_rate: float):
        """设置额外的指标（由外部系统提供）"""
        with self._lock:
            if self._metrics_history:
                latest = self._metrics_history[-1]
                latest.pending_requests = pending_requests
                latest.request_rate = request_rate
                latest.error_rate = error_rate
    
    def _monitor_loop(self):
        """监控循环"""
        while self._running:
            try:
                metrics = self.get_current_metrics()
                
                with self._lock:
                    self._metrics_history.append(metrics)
                    if len(self._metrics_history) > self._max_history_size:
                        self._metrics_history.pop(0)
                
                if self._metric_update_callback:
                    self._metric_update_callback(metrics)
                
                logger.debug(f"资源指标: CPU={metrics.cpu_usage:.1f}% | 内存={metrics.memory_usage:.1f}% | 连接数={metrics.active_connections}")
            except Exception as e:
                logger.error(f"资源监控出错: {e}")
            
            time.sleep(self._interval)


class AutoScaler:
    """自动伸缩器"""
    
    def __init__(
        self,
        policy: ScalePolicy = None,
        resource_monitor: ResourceMonitor = None
    ):
        self._policy = policy or ScalePolicy()
        self._resource_monitor = resource_monitor or ResourceMonitor()
        
        self._current_replicas = 1
        self._scale_up_triggered = False
        self._scale_down_triggered = False
        self._scale_up_time = 0
        self._scale_down_time = 0
        
        # 回调函数
        self._scale_event_callback = None
        
        self._lock = Lock()
    
    def set_policy(self, policy: ScalePolicy):
        """设置伸缩策略"""
        self._policy = policy
    
    def set_resource_monitor(self, monitor: ResourceMonitor):
        """设置资源监控器"""
        self._resource_monitor = monitor
    
    def set_scale_event_callback(self, callback: Callable):
        """设置伸缩事件回调"""
        self._scale_event_callback = callback
    
    def start(self):
        """启动自动伸缩"""
        self._resource_monitor.start()
        logger.info("自动伸缩器已启动")
    
    def stop(self):
        """停止自动伸缩"""
        self._resource_monitor.stop()
        logger.info("自动伸缩器已停止")
    
    def check_and_scale(self) -> Optional[ScaleEvent]:
        """
        检查并执行伸缩
        
        Returns:
            ScaleEvent: 伸缩事件（如果发生）
        """
        metrics = self._resource_monitor.get_average_metrics(
            window_seconds=self._policy.scale_up_window
        )
        
        return self._evaluate_scale(metrics)
    
    def _evaluate_scale(self, metrics: ResourceMetrics) -> Optional[ScaleEvent]:
        """评估是否需要伸缩"""
        now = time.time()
        event = None
        
        # 检查是否需要扩容
        needs_scale_up = (
            metrics.cpu_usage >= self._policy.cpu_scale_up_threshold or
            metrics.memory_usage >= self._policy.memory_scale_up_threshold or
            metrics.active_connections >= self._policy.connection_scale_up_threshold or
            metrics.pending_requests >= self._policy.queue_scale_up_threshold
        )
        
        # 检查是否需要缩容
        needs_scale_down = (
            metrics.cpu_usage <= self._policy.cpu_scale_down_threshold and
            metrics.memory_usage <= self._policy.memory_scale_down_threshold and
            metrics.active_connections <= self._policy.connection_scale_down_threshold and
            metrics.pending_requests <= self._policy.queue_scale_down_threshold
        )
        
        with self._lock:
            # 处理扩容逻辑
            if needs_scale_up and self._current_replicas < self._policy.max_replicas:
                if not self._scale_up_triggered:
                    self._scale_up_triggered = True
                    self._scale_up_time = now
                elif now - self._scale_up_time >= self._policy.scale_up_window:
                    # 连续满足条件，执行扩容
                    target_replicas = min(
                        self._current_replicas + self._policy.scale_up_step,
                        self._policy.max_replicas
                    )
                    
                    event = ScaleEvent(
                        event_type=ScaleEventType.SCALE_UP,
                        timestamp=now,
                        reason=self._get_scale_reason(metrics, "up"),
                        current_replicas=self._current_replicas,
                        target_replicas=target_replicas,
                        metrics={
                            'cpu_usage': metrics.cpu_usage,
                            'memory_usage': metrics.memory_usage,
                            'active_connections': metrics.active_connections,
                            'pending_requests': metrics.pending_requests
                        }
                    )
                    
                    self._current_replicas = target_replicas
                    self._scale_up_triggered = False
                    logger.info(f"执行扩容: {event.current_replicas} -> {event.target_replicas}")
            
            # 处理缩容逻辑
            elif needs_scale_down and self._current_replicas > self._policy.min_replicas:
                if not self._scale_down_triggered:
                    self._scale_down_triggered = True
                    self._scale_down_time = now
                elif now - self._scale_down_time >= self._policy.scale_down_window:
                    # 连续满足条件，执行缩容
                    target_replicas = max(
                        self._current_replicas - self._policy.scale_down_step,
                        self._policy.min_replicas
                    )
                    
                    event = ScaleEvent(
                        event_type=ScaleEventType.SCALE_DOWN,
                        timestamp=now,
                        reason=self._get_scale_reason(metrics, "down"),
                        current_replicas=self._current_replicas,
                        target_replicas=target_replicas,
                        metrics={
                            'cpu_usage': metrics.cpu_usage,
                            'memory_usage': metrics.memory_usage,
                            'active_connections': metrics.active_connections,
                            'pending_requests': metrics.pending_requests
                        }
                    )
                    
                    self._current_replicas = target_replicas
                    self._scale_down_triggered = False
                    logger.info(f"执行缩容: {event.current_replicas} -> {event.target_replicas}")
            
            # 重置触发器
            else:
                if not needs_scale_up:
                    self._scale_up_triggered = False
                if not needs_scale_down:
                    self._scale_down_triggered = False
        
        # 触发回调
        if event and self._scale_event_callback:
            self._scale_event_callback(event)
        
        return event
    
    def _get_scale_reason(self, metrics: ResourceMetrics, direction: str) -> str:
        """获取伸缩原因"""
        reasons = []
        
        if direction == "up":
            if metrics.cpu_usage >= self._policy.cpu_scale_up_threshold:
                reasons.append(f"CPU使用率 {metrics.cpu_usage:.1f}% >= {self._policy.cpu_scale_up_threshold}%")
            if metrics.memory_usage >= self._policy.memory_scale_up_threshold:
                reasons.append(f"内存使用率 {metrics.memory_usage:.1f}% >= {self._policy.memory_scale_up_threshold}%")
            if metrics.active_connections >= self._policy.connection_scale_up_threshold:
                reasons.append(f"连接数 {metrics.active_connections} >= {self._policy.connection_scale_up_threshold}")
            if metrics.pending_requests >= self._policy.queue_scale_up_threshold:
                reasons.append(f"待处理请求 {metrics.pending_requests} >= {self._policy.queue_scale_up_threshold}")
        else:
            reasons.append("资源使用率低于阈值")
        
        return "; ".join(reasons)
    
    def get_status(self) -> Dict[str, Any]:
        """获取伸缩器状态"""
        metrics = self._resource_monitor.get_current_metrics()
        
        return {
            'current_replicas': self._current_replicas,
            'min_replicas': self._policy.min_replicas,
            'max_replicas': self._policy.max_replicas,
            'metrics': {
                'cpu_usage': metrics.cpu_usage,
                'memory_usage': metrics.memory_usage,
                'active_connections': metrics.active_connections,
                'pending_requests': metrics.pending_requests,
                'request_rate': metrics.request_rate,
                'error_rate': metrics.error_rate
            },
            'scale_up_pending': self._scale_up_triggered,
            'scale_down_pending': self._scale_down_triggered
        }


class LoadBalancer:
    """负载均衡器"""
    
    def __init__(self):
        self._servers: Dict[str, Dict[str, Any]] = {}
        self._current_index = 0
        self._lock = Lock()
    
    def register_server(self, server_id: str, url: str, weight: int = 1):
        """
        注册服务器
        
        Args:
            server_id: 服务器ID
            url: 服务器地址
            weight: 权重
        """
        with self._lock:
            self._servers[server_id] = {
                'url': url,
                'weight': weight,
                'active': True,
                'requests': 0,
                'last_access': time.time()
            }
        
        logger.info(f"注册服务器: {server_id} -> {url}")
    
    def unregister_server(self, server_id: str):
        """注销服务器"""
        with self._lock:
            if server_id in self._servers:
                del self._servers[server_id]
                logger.info(f"注销服务器: {server_id}")
    
    def set_server_active(self, server_id: str, active: bool):
        """设置服务器状态"""
        with self._lock:
            if server_id in self._servers:
                self._servers[server_id]['active'] = active
                logger.info(f"服务器状态更新: {server_id} -> {'活跃' if active else '停用'}")
    
    def get_next_server(self) -> Optional[str]:
        """获取下一个服务器（轮询策略）"""
        with self._lock:
            active_servers = [
                sid for sid, info in self._servers.items()
                if info['active']
            ]
            
            if not active_servers:
                return None
            
            # 简单轮询
            server_id = active_servers[self._current_index % len(active_servers)]
            self._current_index += 1
            
            # 更新统计信息
            self._servers[server_id]['requests'] += 1
            self._servers[server_id]['last_access'] = time.time()
            
            return self._servers[server_id]['url']
    
    def get_server_stats(self) -> Dict[str, Any]:
        """获取服务器统计信息"""
        with self._lock:
            stats = {}
            for server_id, info in self._servers.items():
                stats[server_id] = {
                    'url': info['url'],
                    'weight': info['weight'],
                    'active': info['active'],
                    'requests': info['requests'],
                    'last_access': info['last_access']
                }
            return stats
    
    def get_server_count(self) -> int:
        """获取服务器数量"""
        with self._lock:
            return len(self._servers)


# 全局弹性伸缩组件
_global_resource_monitor = ResourceMonitor()
_global_auto_scaler = AutoScaler(resource_monitor=_global_resource_monitor)
_global_load_balancer = LoadBalancer()


def get_resource_monitor() -> ResourceMonitor:
    """获取全局资源监控器"""
    return _global_resource_monitor


def get_auto_scaler() -> AutoScaler:
    """获取全局自动伸缩器"""
    return _global_auto_scaler


def get_load_balancer() -> LoadBalancer:
    """获取全局负载均衡器"""
    return _global_load_balancer


# 启动资源监控器
_global_resource_monitor.start()