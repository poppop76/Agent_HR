import redis
from core.config import settings
from typing import Optional

class LazyRedisClient:
    """延迟初始化的Redis客户端"""
    
    def __init__(self):
        self._client: Optional[redis.Redis] = None
        self._connection_attempted = False
    
    def _get_client(self) -> Optional[redis.Redis]:
        """获取Redis客户端（延迟初始化）"""
        if self._client is not None:
            return self._client
        
        if self._connection_attempted:
            return None
        
        self._connection_attempted = True
        
        try:
            client = redis.Redis(
                host=settings.REDIS_HOST,
                port=settings.REDIS_PORT,
                password=settings.REDIS_PASSWORD,
                db=settings.REDIS_DB,
                decode_responses=True,
                socket_connect_timeout=3,  # 3秒超时
                socket_timeout=5           # 5秒操作超时
            )
            # 测试连接
            client.ping()
            self._client = client
            print("[Redis] 连接成功")
            return self._client
        except redis.ConnectionError as e:
            print(f"[Redis] 连接失败: {e}")
            return None
        except Exception as e:
            print(f"[Redis] 连接错误: {e}")
            return None
    
    def __getattr__(self, name):
        """代理所有属性访问到实际的Redis客户端"""
        client = self._get_client()
        if client is None:
            # 如果客户端未连接，返回一个空操作的代理对象
            class NoOpRedis:
                def __getattr__(self, _):
                    return lambda *args, **kwargs: None
                def __call__(self, *args, **kwargs):
                    return None
            return NoOpRedis()
        return getattr(client, name)

# 使用延迟初始化的Redis客户端
redis_client = LazyRedisClient()