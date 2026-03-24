"""
认证依赖注入
用于保护需要认证的端点
"""
from typing import Optional
from fastapi import Header, HTTPException, status

from app.auth.jwt import decode_access_token, TokenPayload


async def get_current_user(
    authorization: Optional[str] = Header(None)
) -> TokenPayload:
    """
    获取当前认证用户

    Args:
        authorization: Authorization header (Bearer token)

    Returns:
        Token 负载

    Raises:
        HTTPException: 未认证或 token 无效
    """
    if not authorization:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="未提供认证凭据",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # 验证 Bearer 格式
    if not authorization.startswith("Bearer "):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="无效的认证格式",
            headers={"WWW-Authenticate": "Bearer"},
        )

    token = authorization[7:]  # 移除 "Bearer " 前缀

    try:
        payload = decode_access_token(token)
        return payload
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=str(e),
            headers={"WWW-Authenticate": "Bearer"},
        )


async def get_current_user_optional(
    authorization: Optional[str] = Header(None)
) -> Optional[TokenPayload]:
    """
    获取当前认证用户（可选）

    Args:
        authorization: Authorization header (Bearer token)

    Returns:
        Token 负载，如果未提供或无效则返回 None
    """
    if not authorization:
        return None

    if not authorization.startswith("Bearer "):
        return None

    token = authorization[7:]

    try:
        return decode_access_token(token)
    except Exception:
        return None
