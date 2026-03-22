"""
认证模块测试
"""
import pytest
from passlib.context import CryptContext

from app.auth.password import hash_password, verify_password
from app.auth.jwt import create_access_token, decode_access_token, TokenPayload
from app.models import RegisterRequest, LoginRequest


class TestPasswordHashing:
    """测试密码哈希"""

    def test_should_hash_password(self):
        """测试应该哈希密码"""
        password = "mypassword123"
        hashed = hash_password(password)

        assert hashed != password
        assert len(hashed) > 20

    def test_should_verify_correct_password(self):
        """测试应该验证正确的密码"""
        password = "mypassword123"
        hashed = hash_password(password)

        assert verify_password(password, hashed) is True

    def test_should_fail_incorrect_password(self):
        """测试应该拒绝错误的密码"""
        password = "mypassword123"
        wrong_password = "wrongpassword"
        hashed = hash_password(password)

        assert verify_password(wrong_password, hashed) is False


class TestJWT:
    """测试 JWT 功能"""

    def test_should_create_access_token(self):
        """测试应该创建访问令牌"""
        user_id = "user-123"
        username = "testuser"

        token = create_access_token(user_id, username)

        assert isinstance(token, str)
        assert len(token) > 50  # JWT 通常很长

    def test_should_decode_valid_token(self):
        """测试应该解码有效的令牌"""
        user_id = "user-123"
        username = "testuser"

        token = create_access_token(user_id, username)
        payload = decode_access_token(token)

        assert payload.sub == user_id
        assert payload.username == username

    def test_should_fail_invalid_token(self):
        """测试应该拒绝无效的令牌"""
        invalid_token = "invalid.token.here"

        with pytest.raises(Exception):
            decode_access_token(invalid_token)

    def test_should_fail_expired_token(self):
        """测试应该拒绝过期的令牌"""
        # 创建一个已过期的令牌
        from datetime import datetime, timedelta
        from jose import jwt, ExpiredSignatureError

        # 手动创建过期令牌用于测试
        secret_key = "test-secret-key"
        expired_payload = {
            "sub": "user-123",
            "username": "testuser",
            "exp": datetime.utcnow() - timedelta(hours=1)  # 1小时前过期
        }

        expired_token = jwt.encode(expired_payload, secret_key, algorithm="HS256")

        with pytest.raises(Exception):
            decode_access_token(expired_token)


class TestAuthModels:
    """测试认证数据模型"""

    def test_should_validate_register_request(self):
        """测试应该验证注册请求"""
        request = RegisterRequest(username="testuser", password="pass123")

        assert request.username == "testuser"
        assert request.password == "pass123"

    def test_should_reject_short_password(self):
        """测试应该拒绝短密码"""
        from pydantic import ValidationError

        with pytest.raises(ValidationError):
            RegisterRequest(username="testuser", password="short")

    def test_should_validate_login_request(self):
        """测试应该验证登录请求"""
        request = LoginRequest(username="testuser", password="pass123")

        assert request.username == "testuser"
        assert request.password == "pass123"
