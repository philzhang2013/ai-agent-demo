"""
会话管理端点
"""
import logging
from typing import List
from fastapi import APIRouter, HTTPException, status, Depends

from app.models import Session as APISession, Message as APIMessage
from app.db.repositories import SessionRepository, MessageRepository
from app.auth.dependencies import get_current_user
from app.auth.jwt import TokenPayload
from app.db.repositories import UserRepository

router = APIRouter(prefix="/api/sessions", tags=["sessions"])
logger = logging.getLogger(__name__)

user_repo = UserRepository()
session_repo = SessionRepository()
message_repo = MessageRepository()


@router.get("", response_model=List[APISession])
async def get_sessions(
    current_user: TokenPayload = Depends(get_current_user)
) -> List[APISession]:
    """
    获取当前用户的会话列表

    需要认证
    """
    logger.debug(f"[GET /api/sessions] 获取会话列表: user_id={current_user.sub}")

    # 验证用户存在
    user = await user_repo.find_by_id(current_user.sub)
    if not user:
        logger.warning(f"[GET /api/sessions] 用户不存在: user_id={current_user.sub}")
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="用户不存在"
        )

    # 获取会话列表
    sessions = await session_repo.find_by_user_id(user.id)
    logger.info(f"[GET /api/sessions] 返回 {len(sessions)} 个会话: user_id={user.id}")

    return [
        APISession(
            id=s.id,
            user_id=s.user_id,
            created_at=s.created_at,
            updated_at=s.updated_at,
            messages=[]
        )
        for s in sessions
    ]


@router.get("/{session_id}", response_model=APISession)
async def get_session(
    session_id: str,
    current_user: TokenPayload = Depends(get_current_user)
) -> APISession:
    """
    获取会话详情（包含消息）

    需要认证
    """
    logger.debug(f"[GET /api/sessions/{session_id}] 获取会话详情: user_id={current_user.sub}")

    # 验证用户存在
    user = await user_repo.find_by_id(current_user.sub)
    if not user:
        logger.warning(f"[GET /api/sessions/{session_id}] 用户不存在: user_id={current_user.sub}")
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="用户不存在"
        )

    # 获取会话
    session = await session_repo.find_by_id(session_id)
    if not session:
        logger.warning(f"[GET /api/sessions/{session_id}] 会话不存在: session_id={session_id}")
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="会话不存在"
        )

    # 验证会话所有权
    if session.user_id != user.id:
        logger.warning(f"[GET /api/sessions/{session_id}] 无权访问: session_user_id={session.user_id}, request_user_id={user.id}")
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="无权访问此会话"
        )

    # 获取消息
    messages = await message_repo.find_by_session_id(session.id)
    logger.debug(f"[GET /api/sessions/{session_id}] 返回 {len(messages)} 条消息")

    return APISession(
        id=session.id,
        user_id=session.user_id,
        created_at=session.created_at,
        updated_at=session.updated_at,
        messages=[
            APIMessage(
                id=m.id,
                role=m.role,
                content=m.content,
                timestamp=m.created_at,
                tool_calls=None
            )
            for m in messages
        ]
    )


@router.delete("/{session_id}")
async def delete_session(
    session_id: str,
    current_user: TokenPayload = Depends(get_current_user)
):
    """
    删除会话

    需要认证
    """
    logger.info(f"[DELETE /api/sessions/{session_id}] 删除会话请求: user_id={current_user.sub}")

    # 验证用户存在
    user = await user_repo.find_by_id(current_user.sub)
    if not user:
        logger.warning(f"[DELETE /api/sessions/{session_id}] 用户不存在: user_id={current_user.sub}")
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="用户不存在"
        )

    # 获取会话
    session = await session_repo.find_by_id(session_id)
    if not session:
        logger.warning(f"[DELETE /api/sessions/{session_id}] 会话不存在: session_id={session_id}")
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="会话不存在"
        )

    # 验证会话所有权
    if session.user_id != user.id:
        logger.warning(f"[DELETE /api/sessions/{session_id}] 无权删除: session_user_id={session.user_id}, request_user_id={user.id}")
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="无权删除此会话"
        )

    # 删除消息
    deleted_messages = await message_repo.delete_by_session_id(session_id)

    # 删除会话
    await session_repo.delete(session_id)

    logger.info(f"[DELETE /api/sessions/{session_id}] 删除成功: 删除了 {deleted_messages} 条消息")
    return {"success": True}
