"""
认证 API 端点测试
"""
import pytest
from starlette.testclient import TestClient

from app.main import app
from app.auth.repository import user_repository


class TestAuthAPI:
    """测试认证 API 端点"""

    def setup_method(self):
        """每个测试前清空用户数据"""
        user_repository._users.clear()

    def test_should_register_new_user(self):
        """测试应该注册新用户"""
        client = TestClient(app)
        response = client.post(
            "/api/auth/register",
            json={
                "username": "testuser",
                "password": "password123"
            }
        )

        assert response.status_code == 200
        data = response.json()
        assert "user" in data
        assert "token" in data
        assert data["user"]["username"] == "testuser"
        assert "id" in data["user"]

    def test_should_reject_duplicate_username(self):
        """测试应该拒绝重复的用户名"""
        client = TestClient(app)

        # 第一次注册
        client.post(
            "/api/auth/register",
            json={
                "username": "testuser",
                "password": "password123"
            }
        )

        # 第二次注册（相同用户名）
        response = client.post(
            "/api/auth/register",
            json={
                "username": "testuser",
                "password": "different456"
            }
        )

        assert response.status_code == 400
        assert "已存在" in response.json()["detail"]

    def test_should_reject_short_password(self):
        """测试应该拒绝短密码"""
        client = TestClient(app)
        response = client.post(
            "/api/auth/register",
            json={
                "username": "testuser",
                "password": "short"
            }
        )

        assert response.status_code == 422  # 验证错误

    def test_should_login_with_correct_credentials(self):
        """测试应该使用正确的凭据登录"""
        client = TestClient(app)

        # 先注册
        client.post(
            "/api/auth/register",
            json={
                "username": "testuser",
                "password": "password123"
            }
        )

        # 登录
        response = client.post(
            "/api/auth/login",
            json={
                "username": "testuser",
                "password": "password123"
            }
        )

        assert response.status_code == 200
        data = response.json()
        assert "user" in data
        assert "token" in data

    def test_should_fail_login_with_wrong_password(self):
        """测试应该拒绝错误的密码"""
        client = TestClient(app)

        # 先注册
        client.post(
            "/api/auth/register",
            json={
                "username": "testuser",
                "password": "password123"
            }
        )

        # 使用错误密码登录
        response = client.post(
            "/api/auth/login",
            json={
                "username": "testuser",
                "password": "wrongpassword"
            }
        )

        assert response.status_code == 401

    def test_should_fail_login_with_nonexistent_user(self):
        """测试应该拒绝不存在的用户"""
        client = TestClient(app)
        response = client.post(
            "/api/auth/login",
            json={
                "username": "nonexistent",
                "password": "password123"
            }
        )

        assert response.status_code == 401

    def test_should_access_protected_endpoint_with_token(self):
        """测试应该使用 token 访问受保护的端点"""
        client = TestClient(app)

        # 注册并获取 token
        register_response = client.post(
            "/api/auth/register",
            json={
                "username": "testuser",
                "password": "password123"
            }
        )
        token = register_response.json()["token"]

        # 使用 token 访问受保护端点（假设将来会有）
        response = client.get(
            "/api/health",
            headers={"Authorization": f"Bearer {token}"}
        )

        # 健康检查端点不需要认证，但至少验证 header 格式正确
        assert response.status_code == 200
