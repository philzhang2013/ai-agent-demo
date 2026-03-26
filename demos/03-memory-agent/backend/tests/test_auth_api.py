"""
认证 API 端点测试
"""
import pytest
from uuid import uuid4
from httpx import AsyncClient, ASGITransport

from app.main import app


def create_test_client():
    """创建测试客户端"""
    transport = ASGITransport(app=app)
    return AsyncClient(transport=transport, base_url="http://test")


class TestAuthAPI:
    """测试认证 API 端点"""

    @pytest.mark.asyncio
    async def test_should_register_new_user(self):
        """测试应该注册新用户"""
        unique_id = str(uuid4())[:8]
        username = f"testuser_{unique_id}"

        client = create_test_client()
        async with client:
            response = await client.post(
                "/api/auth/register",
                json={
                    "username": username,
                    "password": "password123"
                }
            )

        assert response.status_code == 200
        data = response.json()
        assert "user" in data
        assert "token" in data
        assert data["user"]["username"] == username
        assert "id" in data["user"]

    @pytest.mark.asyncio
    async def test_should_reject_duplicate_username(self):
        """测试应该拒绝重复的用户名"""
        unique_id = str(uuid4())[:8]
        username = f"testuser_{unique_id}"

        client = create_test_client()
        async with client:
            # 第一次注册
            await client.post(
                "/api/auth/register",
                json={
                    "username": username,
                    "password": "password123"
                }
            )

            # 第二次注册（相同用户名）
            response = await client.post(
                "/api/auth/register",
                json={
                    "username": username,
                    "password": "different456"
                }
            )

        assert response.status_code == 400
        assert "已存在" in response.json()["detail"]

    @pytest.mark.asyncio
    async def test_should_reject_short_password(self):
        """测试应该拒绝短密码"""
        unique_id = str(uuid4())[:8]
        username = f"testuser_{unique_id}"

        client = create_test_client()
        async with client:
            response = await client.post(
                "/api/auth/register",
                json={
                    "username": username,
                    "password": "short"
                }
            )

        assert response.status_code == 422  # 验证错误

    @pytest.mark.asyncio
    async def test_should_login_with_correct_credentials(self):
        """测试应该使用正确的凭据登录"""
        unique_id = str(uuid4())[:8]
        username = f"testuser_{unique_id}"

        client = create_test_client()
        async with client:
            # 先注册
            await client.post(
                "/api/auth/register",
                json={
                    "username": username,
                    "password": "password123"
                }
            )

            # 登录
            response = await client.post(
                "/api/auth/login",
                json={
                    "username": username,
                    "password": "password123"
                }
            )

        assert response.status_code == 200
        data = response.json()
        assert "user" in data
        assert "token" in data

    @pytest.mark.asyncio
    async def test_should_fail_login_with_wrong_password(self):
        """测试应该拒绝错误的密码"""
        unique_id = str(uuid4())[:8]
        username = f"testuser_{unique_id}"

        client = create_test_client()
        async with client:
            # 先注册
            await client.post(
                "/api/auth/register",
                json={
                    "username": username,
                    "password": "password123"
                }
            )

            # 使用错误密码登录
            response = await client.post(
                "/api/auth/login",
                json={
                    "username": username,
                    "password": "wrongpassword"
                }
            )

        assert response.status_code == 401

    @pytest.mark.asyncio
    async def test_should_fail_login_with_nonexistent_user(self):
        """测试应该拒绝不存在的用户"""
        unique_id = str(uuid4())[:8]
        username = f"nonexistent_{unique_id}"

        client = create_test_client()
        async with client:
            response = await client.post(
                "/api/auth/login",
                json={
                    "username": username,
                    "password": "password123"
                }
            )

        assert response.status_code == 401

    @pytest.mark.asyncio
    async def test_should_access_protected_endpoint_with_token(self):
        """测试应该使用 token 访问受保护的端点"""
        unique_id = str(uuid4())[:8]
        username = f"testuser_{unique_id}"

        client = create_test_client()
        async with client:
            # 注册并获取 token
            register_response = await client.post(
                "/api/auth/register",
                json={
                    "username": username,
                    "password": "password123"
                }
            )
            token = register_response.json()["token"]

            # 使用 token 访问受保护端点
            response = await client.get(
                "/api/auth/me",
                headers={"Authorization": f"Bearer {token}"}
            )

        assert response.status_code == 200
        data = response.json()
        assert data["username"] == username
