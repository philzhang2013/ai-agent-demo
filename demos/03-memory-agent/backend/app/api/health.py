"""
健康检查端点
"""
from fastapi import APIRouter

router = APIRouter(prefix="/api", tags=["health"])


@router.get("/health")
async def health_check():
    """健康检查端点"""
    return {"status": "ok", "service": "web-agent-demo"}
