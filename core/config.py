# config.py 完整修改后代码
from dotenv import load_dotenv
from pydantic_settings import BaseSettings
import os

# 加载 .env 文件（确保路径正确，若.env在项目根目录则无需额外配置）
load_dotenv()

class Settings(BaseSettings):
    # ========== 数据库配置 ==========
    DB_HOST: str = os.getenv("DB_HOST", "127.0.0.1")  # 增加默认值，防止环境变量缺失
    DB_PORT: int = int(os.getenv("DB_PORT", 3306))
    DB_USER: str = os.getenv("DB_USER", "root")
    DB_PASSWORD: str = os.getenv("DB_PWD", "")
    DB_NAME: str = os.getenv("DB_NAME", "hr_matching_system")

    # ========== Redis ==========
    REDIS_HOST: str = os.getenv("REDIS_HOST", "127.0.0.1")
    REDIS_PORT: int = int(os.getenv("REDIS_PORT", 6379))
    REDIS_PASSWORD: str = os.getenv("REDIS_PASSWORD", None)
    REDIS_DB: int = int(os.getenv("REDIS_DB", 0))

    # ========== 项目配置 ==========
    APP_TITLE: str = os.getenv("APP_TITLE", "HR人岗匹配系统")
    API_PREFIX: str = os.getenv("API_PREFIX", "/hr/api/v1")

    # ========== 模型配置 ==========
    CHAT_MODEL_NAME: str = os.getenv("ChatModel_NAME", "qwen3-max")
    EMBEDDINGS_MODEL_NAME: str = os.getenv("Embeddings_model_NAME", "")

    # ========== JWT 配置 ==========
    JWT_KEY: str = os.getenv("JWT_KEY", "hr_connect")
    ALGORITHM: str = os.getenv("ALGORITHM", "HS256")
    EXPIRE_MINUTES: int = int(os.getenv("EXPIRE_MINUTES", 60))

    #响应配置
    RES_CODE: dict = {
        "200": 200,
        "400": 400,
        "401": 401,
        "403": 403,
        "404": 404,
        "500": 500,
        "1001": 1001,
        "1002": 1002,
    }

    RES_MSG: dict = {
        "200": "操作成功",
        "400": "参数错误",
        "401": "未登录/Token过期/Token无效",
        "403": "无操作权限",
        "404": "资源不存在",
        "500": "服务端异常",
        "1001": "简历解析中",
        "1002": "简历解析失败",
    }

    # 拼接数据库连接地址
    @property
    def DATABASE_URL(self):
        return f"mysql+pymysql://{self.DB_USER}:{self.DB_PASSWORD}@{self.DB_HOST}:{self.DB_PORT}/{self.DB_NAME}?charset=utf8mb4"

# 实例化配置对象，供其他模块导入使用
settings = Settings()