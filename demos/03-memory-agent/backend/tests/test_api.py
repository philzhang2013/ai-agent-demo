"""
API 端点测试
"""
import pytest
from starlette.testclient import TestClient

from app.main import app


class TestHealthEndpoint:
    """测试健康检查端点"""

    def test_should_return_ok(self):
        """测试应该返回 OK 状态"""
        client = TestClient(app)
        response = client.get("/api/health")

        assert response.status_code == 200
        assert response.json()["status"] == "ok"
        assert response.json()["service"] == "web-agent-demo"


class TestChatEndpoint:
    """测试聊天端点"""

    def test_should_return_mock_response(self):
        """测试应该返回模拟响应"""
        client = TestClient(app)
        response = client.post(
            "/api/chat",
            json={"message": "你好"}
        )

        assert response.status_code == 200
        data = response.json()
        assert "response" in data
        assert "session_id" in data

    def test_should_support_custom_session_id(self):
        """测试应该支持自定义会话 ID"""
        client = TestClient(app)
        response = client.post(
            "/api/chat",
            json={"message": "你好", "session_id": "custom-session"}
        )

        assert response.status_code == 200
        assert response.json()["session_id"] == "custom-session"

    def test_should_return_sse_stream(self):
        """测试应该返回 SSE 流"""
        client = TestClient(app)
        response = client.post(
            "/api/chat/stream",
            json={"message": "你好"}
        )

        assert response.status_code == 200
        assert "text/event-stream" in response.headers.get("content-type", "")


class TestRootEndpoint:
    """测试根路径端点"""

    def test_should_return_api_info(self):
        """测试应该返回 API 信息"""
        client = TestClient(app)
        response = client.get("/")

        assert response.status_code == 200
        data = response.json()
        assert "message" in data
        assert "version" in data
        assert data["docs"] == "/docs"
