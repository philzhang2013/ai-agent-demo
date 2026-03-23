"""
FastAPI 应用入口
"""
import logging
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

# 配置日志输出
log_level = getattr(logging, settings.log_level.upper(), logging.INFO)
logging.basicConfig(
    level=log_level,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)

# 创建日志记录器
logger = logging.getLogger(__name__)
logger.info(f"[应用启动] {settings.app_name} v{settings.app_version}")
logger.info(f"[配置] LLM提供商=zhipuai, 模型={settings.zhipuai_model}, 最大迭代={settings.max_iterations}")

app = FastAPI(
    title=settings.app_name,
    version=settings.app_version,
    docs_url="/docs",
    redoc_url="/redoc"
)

# 配置 CORS
allowed_origins = [settings.frontend_url, "http://localhost:5173"]
logger.info(f"[CORS 配置] 允许来源: {allowed_origins}")

app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 注册路由
logger.info("[注册路由] /api/health - 健康检查")
app.include_router(health_router)

logger.info("[注册路由] /api/chat - 聊天端点")
app.include_router(chat_router)

logger.info("[注册路由] /api/auth - 认证端点")
app.include_router(auth_router)

logger.info("[注册路由] /api/sessions - 会话管理")
app.include_router(sessions_router)

logger.info("[路由注册完成] 所有端点已注册")


@app.on_event("shutdown")
async def shutdown_event():
    """应用关闭时清理资源"""
    logger.info("[应用关闭] 正在清理资源...")
    await close_pool()
    logger.info("[应用关闭] 资源清理完成")


@app.get("/")
async def root():
    """根路径"""
    logger.debug("[访问根路径] 返回 API 信息")
    return {
        "message": "Web Agent Demo API",
        "version": settings.app_version,
        "docs": "/docs"
    }
