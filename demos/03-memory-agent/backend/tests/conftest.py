"""
Pytest 配置文件
设置测试环境变量和 fixtures
"""
import os
import pytest

# 设置测试环境变量（不覆盖 DATABASE_URL，从 .env 读取）
os.environ.update({
    'ZHIPUAI_API_KEY': 'test_api_key',
    'JWT_SECRET_KEY': 'test-secret-key-for-testing-only',
})


@pytest.fixture(scope="session")
def event_loop():
    """创建事件循环用于所有测试"""
    import asyncio
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()
