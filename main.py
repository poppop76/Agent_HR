from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from api.auth import router as auth_router

from core.config import settings
from db.database import engine, Base

# 初始化数据表
Base.metadata.create_all(bind=engine)

# 控制台打印启动信息（等同Java启动打印）
print("======================================")
print("          FastAPI 后端服务启动成功")
print(f"          访问地址：http://127.0.0.1:8000")
print("======================================")

app = FastAPI(
    title=settings.APP_TITLE,
    version="1.0.0",
    description="后端接口服务"
)

# 跨域
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth_router)


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True
    )