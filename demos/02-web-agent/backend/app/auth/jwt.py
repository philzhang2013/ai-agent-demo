"""
JWT Token 生成和验证
"""
from datetime import datetime, timedelta
from typing import Optional
from jose import JWTError, jwt
from pydantic import BaseModel

from app.config import get_settings


class TokenPayload(BaseModel):
    """Token 负载"""
    sub: str  # 用户 ID
    username: str
    exp: Optional[datetime] = None


def create_access_token(user_id: str, username: str) -> str:
    """
    创建访问令牌

    Args:
        user_id: 用户 ID
        username: 用户名

    Returns:
        JWT Token
    """
    settings = get_settings()

    # 设置过期时间
    expire = datetime.utcnow() + timedelta(days=settings.jwt_expiration_days)

    # 创建 payload
    payload = {
        "sub": user_id,
        "username": username,
        "exp": expire
    }

    # 生成 token
    token = jwt.encode(
        payload,
        settings.jwt_secret_key,
        algorithm=settings.jwt_algorithm
    )

    return token


def decode_access_token(token: str) -> TokenPayload:
    """
    解码访问令牌

    Args:
        token: JWT Token

    Returns:
        Token 负载

    Raises:
        Exception: Token 无效或过期
    """
    settings = get_settings()

    try:
        payload = jwt.decode(
            token,
            settings.jwt_secret_key,
            algorithms=[settings.jwt_algorithm]
        )

        # 验证必需字段
        if "sub" not in payload or "username" not in payload:
            raise Exception("Token 缺少必需字段")

        return TokenPayload(
            sub=payload["sub"],
            username=payload["username"],
            exp=datetime.fromtimestamp(payload["exp"]) if "exp" in payload else None
        )

    except JWTError as e:
        raise Exception(f"Token 无效: {e}")
