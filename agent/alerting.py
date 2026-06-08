"""
监控告警配置
定义告警规则和通知方式
"""
import logging
import time
from typing import Dict, Any, Optional, List, Callable
from datetime import datetime, timedelta
from enum import Enum
from dataclasses import dataclass

logger = logging.getLogger(__name__)


class AlertSeverity(Enum):
    """告警级别"""
    INFO = "info"
    WARNING = "warning"
    CRITICAL = "critical"


class AlertStatus(Enum):
    """告警状态"""
    FIRING = "firing"           # 触发中
    RESOLVED = "resolved"       # 已解决
    PENDING = "pending"         # 待确认


@dataclass
class AlertRule:
    """告警规则"""
    name: str                    # 规则名称
    severity: AlertSeverity      # 告警级别
    metric_name: str             # 指标名称
    operator: str                # 比较操作符 (>, <, >=, <=, ==, !=)
    threshold: float             # 阈值
    duration: int = 0            # 持续时间（秒），超过此时间才触发
    description: str = ""        # 规则描述
    tags: List[str] = None       # 标签
    
    def __post_init__(self):
        if self.tags is None:
            self.tags = []


@dataclass
class Alert:
    """告警实例"""
    rule_name: str
    severity: AlertSeverity
    status: AlertStatus
    message: str
    metric_value: float
    threshold: float
    timestamp: float
    resolved_at: Optional[float] = None
    annotations: Dict[str, Any] = None
    
    def __post_init__(self):
        if self.annotations is None:
            self.annotations = {}


class NotificationChannel(Enum):
    """通知渠道"""
    LOG = "log"                       # 日志
    EMAIL = "email"                   # 邮件
    WEBHOOK = "webhook"               # Webhook
    SMS = "sms"                       # 短信
    DINGTALK = "dingtalk"             # 钉钉
    WECHAT = "wechat"                 # 微信


class AlertManager:
    """告警管理器"""
    
    def __init__(self):
        self._rules: List[AlertRule] = []
        self._alerts: Dict[str, Alert] = {}
        self._notification_channels: List[NotificationChannel] = []
        
        # 回调函数
        self._alert_trigger_callback = None
        self._alert_resolve_callback = None
    
    def add_rule(self, rule: AlertRule):
        """添加告警规则"""
        self._rules.append(rule)
        logger.info(f"添加告警规则: {rule.name}")
    
    def remove_rule(self, rule_name: str):
        """移除告警规则"""
        self._rules = [r for r in self._rules if r.name != rule_name]
        logger.info(f"移除告警规则: {rule_name}")
    
    def get_rules(self) -> List[AlertRule]:
        """获取所有规则"""
        return self._rules
    
    def set_notification_channels(self, channels: List[NotificationChannel]):
        """设置通知渠道"""
        self._notification_channels = channels
    
    def set_alert_trigger_callback(self, callback: Callable):
        """设置告警触发回调"""
        self._alert_trigger_callback = callback
    
    def set_alert_resolve_callback(self, callback: Callable):
        """设置告警解决回调"""
        self._alert_resolve_callback = callback
    
    def evaluate_rules(self, metrics: Dict[str, float]) -> List[Alert]:
        """
        评估所有告警规则
        
        Args:
            metrics: 指标字典
            
        Returns:
            触发的告警列表
        """
        triggered_alerts = []
        
        for rule in self._rules:
            if rule.metric_name not in metrics:
                continue
            
            metric_value = metrics[rule.metric_name]
            
            # 执行比较
            if self._compare(metric_value, rule.operator, rule.threshold):
                alert_key = f"{rule.name}_{rule.metric_name}"
                
                if alert_key not in self._alerts:
                    # 创建新告警
                    alert = Alert(
                        rule_name=rule.name,
                        severity=rule.severity,
                        status=AlertStatus.FIRING,
                        message=self._format_message(rule, metric_value),
                        metric_value=metric_value,
                        threshold=rule.threshold,
                        timestamp=time.time()
                    )
                    self._alerts[alert_key] = alert
                    triggered_alerts.append(alert)
                    
                    logger.warning(f"告警触发: {rule.name} - {alert.message}")
                    
                    # 发送通知
                    self._send_notifications(alert)
                    
                    # 触发回调
                    if self._alert_trigger_callback:
                        self._alert_trigger_callback(alert)
                else:
                    # 更新现有告警
                    existing_alert = self._alerts[alert_key]
                    existing_alert.metric_value = metric_value
                    existing_alert.timestamp = time.time()
            else:
                # 指标恢复正常，检查是否有对应的告警需要解决
                alert_key = f"{rule.name}_{rule.metric_name}"
                if alert_key in self._alerts and self._alerts[alert_key].status == AlertStatus.FIRING:
                    alert = self._alerts[alert_key]
                    alert.status = AlertStatus.RESOLVED
                    alert.resolved_at = time.time()
                    
                    logger.info(f"告警解决: {rule.name}")
                    
                    # 发送解决通知
                    self._send_notifications(alert)
                    
                    # 触发回调
                    if self._alert_resolve_callback:
                        self._alert_resolve_callback(alert)
        
        return triggered_alerts
    
    def get_alerts(self, status: Optional[AlertStatus] = None) -> List[Alert]:
        """
        获取告警列表
        
        Args:
            status: 过滤状态
            
        Returns:
            告警列表
        """
        alerts = list(self._alerts.values())
        
        if status:
            alerts = [a for a in alerts if a.status == status]
        
        return alerts
    
    def acknowledge_alert(self, rule_name: str):
        """确认告警"""
        for key, alert in self._alerts.items():
            if alert.rule_name == rule_name and alert.status == AlertStatus.FIRING:
                alert.annotations['acknowledged'] = True
                alert.annotations['acknowledged_at'] = time.time()
                logger.info(f"告警已确认: {rule_name}")
    
    def _compare(self, value: float, operator: str, threshold: float) -> bool:
        """执行比较操作"""
        if operator == '>':
            return value > threshold
        elif operator == '<':
            return value < threshold
        elif operator == '>=':
            return value >= threshold
        elif operator == '<=':
            return value <= threshold
        elif operator == '==':
            return value == threshold
        elif operator == '!=':
            return value != threshold
        return False
    
    def _format_message(self, rule: AlertRule, value: float) -> str:
        """格式化告警消息"""
        return f"{rule.description or rule.name}: {rule.metric_name} {rule.operator} {rule.threshold} (当前值: {value})"
    
    def _send_notifications(self, alert: Alert):
        """发送告警通知"""
        for channel in self._notification_channels:
            try:
                if channel == NotificationChannel.LOG:
                    self._notify_log(alert)
                elif channel == NotificationChannel.WEBHOOK:
                    self._notify_webhook(alert)
                # 其他渠道可以在这里扩展
            except Exception as e:
                logger.error(f"发送通知失败 ({channel}): {e}")
    
    def _notify_log(self, alert: Alert):
        """记录日志通知"""
        if alert.status == AlertStatus.FIRING:
            if alert.severity == AlertSeverity.CRITICAL:
                logger.critical(f"[告警] {alert.message}")
            elif alert.severity == AlertSeverity.WARNING:
                logger.warning(f"[告警] {alert.message}")
            else:
                logger.info(f"[告警] {alert.message}")
        else:
            logger.info(f"[告警恢复] {alert.rule_name}")
    
    def _notify_webhook(self, alert: Alert):
        """发送Webhook通知"""
        # 这里需要配置Webhook URL
        # 实际实现需要调用HTTP请求
        pass


# 默认告警规则配置
DEFAULT_ALERT_RULES = [
    # === 系统资源告警 ===
    AlertRule(
        name="CPU使用率过高",
        severity=AlertSeverity.WARNING,
        metric_name="cpu_usage",
        operator=">",
        threshold=70.0,
        duration=60,
        description="CPU使用率超过70%",
        tags=["system", "resource"]
    ),
    AlertRule(
        name="CPU使用率严重过高",
        severity=AlertSeverity.CRITICAL,
        metric_name="cpu_usage",
        operator=">",
        threshold=90.0,
        duration=30,
        description="CPU使用率超过90%",
        tags=["system", "resource", "critical"]
    ),
    AlertRule(
        name="内存使用率过高",
        severity=AlertSeverity.WARNING,
        metric_name="memory_usage",
        operator=">",
        threshold=75.0,
        duration=60,
        description="内存使用率超过75%",
        tags=["system", "resource"]
    ),
    AlertRule(
        name="内存使用率严重过高",
        severity=AlertSeverity.CRITICAL,
        metric_name="memory_usage",
        operator=">",
        threshold=90.0,
        duration=30,
        description="内存使用率超过90%",
        tags=["system", "resource", "critical"]
    ),
    
    # === Token使用告警 ===
    AlertRule(
        name="每日Token消耗接近上限",
        severity=AlertSeverity.WARNING,
        metric_name="daily_token_usage_ratio",
        operator=">",
        threshold=0.8,
        duration=0,
        description="每日Token消耗超过预算的80%",
        tags=["cost", "token"]
    ),
    AlertRule(
        name="每日Token消耗达到上限",
        severity=AlertSeverity.CRITICAL,
        metric_name="daily_token_usage_ratio",
        operator=">",
        threshold=0.95,
        duration=0,
        description="每日Token消耗超过预算的95%",
        tags=["cost", "token", "critical"]
    ),
    
    # === 服务质量告警 ===
    AlertRule(
        name="API错误率过高",
        severity=AlertSeverity.WARNING,
        metric_name="api_error_rate",
        operator=">",
        threshold=5.0,
        duration=60,
        description="API错误率超过5%",
        tags=["api", "quality"]
    ),
    AlertRule(
        name="API延迟过高",
        severity=AlertSeverity.WARNING,
        metric_name="api_latency_p95",
        operator=">",
        threshold=3.0,
        duration=60,
        description="API P95延迟超过3秒",
        tags=["api", "performance"]
    ),
    
    # === 缓存告警 ===
    AlertRule(
        name="缓存命中率过低",
        severity=AlertSeverity.WARNING,
        metric_name="cache_hit_rate",
        operator="<",
        threshold=0.7,
        duration=120,
        description="缓存命中率低于70%",
        tags=["cache", "performance"]
    ),
    
    # === 数据库告警 ===
    AlertRule(
        name="数据库连接数过高",
        severity=AlertSeverity.WARNING,
        metric_name="db_connections",
        operator=">",
        threshold=100,
        duration=60,
        description="数据库连接数超过100",
        tags=["database", "resource"]
    ),
    
    # === LLM服务告警 ===
    AlertRule(
        name="LLM调用失败率过高",
        severity=AlertSeverity.WARNING,
        metric_name="llm_error_rate",
        operator=">",
        threshold=10.0,
        duration=60,
        description="LLM调用失败率超过10%",
        tags=["llm", "service"]
    ),
    AlertRule(
        name="LLM响应超时率过高",
        severity=AlertSeverity.WARNING,
        metric_name="llm_timeout_rate",
        operator=">",
        threshold=5.0,
        duration=60,
        description="LLM响应超时率超过5%",
        tags=["llm", "performance"]
    )
]


# 创建全局告警管理器并加载默认规则
_global_alert_manager = AlertManager()

for rule in DEFAULT_ALERT_RULES:
    _global_alert_manager.add_rule(rule)

# 默认启用日志通知
_global_alert_manager.set_notification_channels([NotificationChannel.LOG])


def get_alert_manager() -> AlertManager:
    """获取全局告警管理器"""
    return _global_alert_manager