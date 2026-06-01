from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from api.auth import router as auth_router
from api.user import router as user_router
from api.job import router as job_router
from api.department import router as department_router
from api.resume import router as resume_router
from api.matching import router as matching_router
from api.statistics import router as statistics_router
from api.category import router as category_router
from api.ai import router as ai_router
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

#登录模块
app.include_router(auth_router)
#用户模块
app.include_router(user_router)
#岗位模块
app.include_router(job_router)
#部门模块
app.include_router(department_router)
#简历模块
app.include_router(resume_router)
#人岗匹配模块
app.include_router(matching_router)
#数据统计模块
app.include_router(statistics_router)
#岗位类别模块
app.include_router(category_router)
#AI智能模块
app.include_router(ai_router)


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True
    )