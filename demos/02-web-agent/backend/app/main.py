"""
FastAPI 应用入口
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.config import get_settings
from app.api.health import router as health_router
from app.api.chat import router as chat_router
from app.api.auth import router as auth_router
from app.api.sessions import router as sessions_router
from app.db.connection import close_pool

# 创建 FastAPI 应用
settings = get_settings()
app = FastAPI(
    title=settings.app_name,
    version=settings.app_version,
    docs_url="/docs",
    redoc_url="/redoc"
)

# 配置 CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=[settings.frontend_url, "http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 注册路由
app.include_router(health_router)
app.include_router(chat_router)
app.include_router(auth_router)
app.include_router(sessions_router)


@app.on_event("shutdown")
async def shutdown_event():
    """应用关闭时清理资源"""
    await close_pool()


@app.get("/")
async def root():
    """根路径"""
    return {
        "message": "Web Agent Demo API",
        "version": settings.app_version,
        "docs": "/docs"
    }
