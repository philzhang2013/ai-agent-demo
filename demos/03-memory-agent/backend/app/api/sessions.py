"""
会话管理端点
"""
import logging
from typing import List
from fastapi import APIRouter, HTTPException, status, Depends

from app.models import Session as APISession, Message as APIMessage, SessionPreview, TitleUpdateRequest
from app.db.repositories import SessionRepository, MessageRepository
from app.auth.dependencies import get_current_user
from app.auth.jwt import TokenPayload
from app.db.repositories import UserRepository

router = APIRouter(prefix="/api/sessions", tags=["sessions"])
logger = logging.getLogger(__name__)

user_repo = UserRepository()
session_repo = SessionRepository()
message_repo = MessageRepository()


@router.get("", response_model=List[SessionPreview])
async def get_sessions(
    current_user: TokenPayload = Depends(get_current_user)
) -> List[SessionPreview]:
    """
    获取当前用户的会话列表（含预览信息）

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

    # 获取会话列表（含预览）
    sessions = await session_repo.find_with_preview(user.id)
    logger.info(f"[GET /api/sessions] 返回 {len(sessions)} 个会话: user_id={user.id}")

    return [
        SessionPreview(
            id=s.id,
            title=s.title,
            last_message=s.last_message,
            message_count=s.message_count,
            updated_at=s.updated_at
        )
        for s in sessions
    ]


@router.post("", response_model=APISession, status_code=status.HTTP_201_CREATED)
async def create_session(
    current_user: TokenPayload = Depends(get_current_user)
) -> APISession:
    """
    创建新会话

    需要认证
    """
    logger.debug(f"[POST /api/sessions] 创建会话请求: user_id={current_user.sub}")

    # 验证用户存在
    user = await user_repo.find_by_id(current_user.sub)
    if not user:
        logger.warning(f"[POST /api/sessions] 用户不存在: user_id={current_user.sub}")
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="用户不存在"
        )

    # 创建会话
    new_session = await session_repo.create(user.id, title="新对话")
    logger.info(f"[POST /api/sessions] 会话创建成功: session_id={new_session.id}")

    return APISession(
        id=new_session.id,
        user_id=new_session.user_id,
        title=new_session.title,
        created_at=new_session.created_at,
        updated_at=new_session.updated_at,
        messages=[]
    )


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
        title=session.title,
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


@router.put("/{session_id}/title", response_model=APISession)
async def update_session_title(
    session_id: str,
    request: TitleUpdateRequest,
    current_user: TokenPayload = Depends(get_current_user)
) -> APISession:
    """
    更新会话标题

    需要认证
    """
    logger.info(f"[PUT /api/sessions/{session_id}/title] 更新会话标题请求: user_id={current_user.sub}, title={request.title}")

    # 验证用户存在
    user = await user_repo.find_by_id(current_user.sub)
    if not user:
        logger.warning(f"[PUT /api/sessions/{session_id}/title] 用户不存在: user_id={current_user.sub}")
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="用户不存在"
        )

    # 获取会话
    session = await session_repo.find_by_id(session_id)
    if not session:
        logger.warning(f"[PUT /api/sessions/{session_id}/title] 会话不存在: session_id={session_id}")
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="会话不存在"
        )

    # 验证会话所有权
    if session.user_id != user.id:
        logger.warning(f"[PUT /api/sessions/{session_id}/title] 无权更新: session_user_id={session.user_id}, request_user_id={user.id}")
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="无权更新此会话"
        )

    # 更新标题
    updated_session = await session_repo.update_title(session_id, request.title)
    if not updated_session:
        logger.warning(f"[PUT /api/sessions/{session_id}/title] 更新失败: session_id={session_id}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="更新失败"
        )

    logger.info(f"[PUT /api/sessions/{session_id}/title] 更新成功: new_title={request.title}")

    return APISession(
        id=updated_session.id,
        user_id=updated_session.user_id,
        title=updated_session.title,
        created_at=updated_session.created_at,
        updated_at=updated_session.updated_at,
        messages=[]
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
