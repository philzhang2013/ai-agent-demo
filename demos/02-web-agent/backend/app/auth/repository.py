"""
用户数据仓储（内存存储）
第三阶段将迁移到 Supabase
"""
from typing import Dict, Optional
from datetime import datetime
from uuid import uuid4

from pydantic import BaseModel


class User(BaseModel):
    """用户模型"""
    id: str
    username: str
    password_hash: str
    created_at: datetime


class UserRepository:
    """用户仓储（内存存储）"""

    def __init__(self):
        # 内存存储用户数据
        # 格式: {username: User}
        self._users: Dict[str, User] = {}

    def create(self, username: str, password_hash: str) -> User:
        """
        创建新用户

        Args:
            username: 用户名
            password_hash: 密码哈希

        Returns:
            创建的用户

        Raises:
            ValueError: 用户名已存在
        """
        if username in self._users:
            raise ValueError(f"用户名 '{username}' 已存在")

        user = User(
            id=str(uuid4()),
            username=username,
            password_hash=password_hash,
            created_at=datetime.utcnow()
        )

        self._users[username] = user
        return user

    def find_by_username(self, username: str) -> Optional[User]:
        """
        根据用户名查找用户

        Args:
            username: 用户名

        Returns:
            用户对象，不存在返回 None
        """
        return self._users.get(username)

    def find_by_id(self, user_id: str) -> Optional[User]:
        """
        根据 ID 查找用户

        Args:
            user_id: 用户 ID

        Returns:
            用户对象，不存在返回 None
        """
        for user in self._users.values():
            if user.id == user_id:
                return user
        return None


# 全局单例
user_repository = UserRepository()
