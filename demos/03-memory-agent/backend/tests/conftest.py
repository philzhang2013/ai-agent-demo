"""
Pytest 配置文件
设置测试环境变量和 fixtures
"""
import os
import pytest
import pytest_asyncio

# 设置测试环境变量（不覆盖 DATABASE_URL，从 .env 读取）
os.environ.update({
    'ZHIPUAI_API_KEY': 'test_api_key',
    'JWT_SECRET_KEY': 'test-secret-key-for-testing-only',
})


# 使用 pytest-asyncio 默认的 event_loop fixture 配置
pytestmark = pytest.mark.asyncio(loop_scope="function")


