"""
会话管理端点
"""
from typing import List
from fastapi import APIRouter, HTTPException, status, Depends

from app.models import Session as APISession, Message as APIMessage
from app.db.repositories import SessionRepository, MessageRepository
from app.auth.dependencies import get_current_user
from app.auth.jwt import TokenPayload
from app.db.repositories import UserRepository

router = APIRouter(prefix="/api/sessions", tags=["sessions"])

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
    # 验证用户存在
    user = await user_repo.find_by_id(current_user.sub)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="用户不存在"
        )

    # 获取会话列表
    sessions = await session_repo.find_by_user_id(user.id)

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
    # 验证用户存在
    user = await user_repo.find_by_id(current_user.sub)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="用户不存在"
        )

    # 获取会话
    session = await session_repo.find_by_id(session_id)
    if not session:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="会话不存在"
        )

    # 验证会话所有权
    if session.user_id != user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="无权访问此会话"
        )

    # 获取消息
    messages = await message_repo.find_by_session_id(session.id)

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
    # 验证用户存在
    user = await user_repo.find_by_id(current_user.sub)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="用户不存在"
        )

    # 获取会话
    session = await session_repo.find_by_id(session_id)
    if not session:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="会话不存在"
        )

    # 验证会话所有权
    if session.user_id != user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="无权删除此会话"
        )

    # 删除消息
    await message_repo.delete_by_session_id(session_id)

    # 删除会话
    await session_repo.delete(session_id)

    return {"success": True}
