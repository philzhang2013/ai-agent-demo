"""
配置管理模块测试
"""
import os
import pytest
from pydantic import ValidationError
from pydantic_settings import SettingsConfigDict

from app.config import Settings, get_settings


class TestSettings:
    """测试 Settings 配置类"""

    def test_should_load_default_values(self, monkeypatch, tmp_path):
        """测试应该加载默认值"""
        # 创建一个空的 .env 文件在临时目录
        env_file = tmp_path / ".env"
        env_file.write_text("")

        # 清除所有环境变量
        for key in os.environ.copy():
            if key.startswith(('KIMI_', 'ZHIPUAI_', 'SUPABASE_', 'JWT_', 'APP_', 'LOG_', 'MAX_', 'FRONTEND_', 'DATABASE_', 'LLM_')):
                monkeypatch.delenv(key, raising=False)

        # 设置必需的环境变量（现在默认使用 Kimi）
        monkeypatch.setenv('KIMI_API_KEY', 'test-kimi-key')
        monkeypatch.setenv('DATABASE_URL', 'postgresql://localhost/test')

        # 使用临时 .env 文件创建 Settings
        class TestSettings(Settings):
            model_config = SettingsConfigDict(
                env_file=str(env_file),
                env_file_encoding="utf-8",
                case_sensitive=False,
                extra="ignore"
            )

        settings = TestSettings()

        # 验证 Kimi 是默认配置
        assert settings.llm_provider == 'kimi'
        assert settings.kimi_api_key == 'test-kimi-key'
        assert settings.kimi_model == 'kimi-for-coding'
        assert settings.kimi_base_url == 'https://api.moonshot.cn/v1'
        # 智谱 AI 有默认值
        assert settings.zhipuai_model == 'glm-5'
        assert settings.app_name == 'Web Agent Demo'
        assert settings.app_version == '0.1.0'
        assert settings.log_level == 'INFO'
        assert settings.max_iterations == 5

    def test_should_load_from_environment(self, monkeypatch, tmp_path):
        """测试应该从环境变量加载配置"""
        # 创建一个空的 .env 文件在临时目录
        env_file = tmp_path / ".env"
        env_file.write_text("")

        # 测试 Kimi 配置
        monkeypatch.setenv('KIMI_API_KEY', 'custom-kimi-key')
        monkeypatch.setenv('KIMI_MODEL', 'kimi-k2.5')
        monkeypatch.setenv('LLM_PROVIDER', 'kimi')
        monkeypatch.setenv('LOG_LEVEL', 'DEBUG')
        monkeypatch.setenv('MAX_ITERATIONS', '10')
        monkeypatch.setenv('DATABASE_URL', 'postgresql://localhost/test')

        class TestSettings(Settings):
            model_config = SettingsConfigDict(
                env_file=str(env_file),
                env_file_encoding="utf-8",
                case_sensitive=False,
                extra="ignore"
            )

        settings = TestSettings()

        assert settings.kimi_api_key == 'custom-kimi-key'
        assert settings.kimi_model == 'kimi-k2.5'
        assert settings.llm_provider == 'kimi'
        assert settings.log_level == 'DEBUG'
        assert settings.max_iterations == 10

    def test_should_support_zhipuai_provider(self, monkeypatch, tmp_path):
        """测试应该支持智谱 AI 作为备选提供商"""
        env_file = tmp_path / ".env"
        env_file.write_text("")

        monkeypatch.setenv('LLM_PROVIDER', 'zhipuai')
        monkeypatch.setenv('ZHIPUAI_API_KEY', 'custom-zhipu-key')
        monkeypatch.setenv('ZHIPUAI_MODEL', 'glm-5')
        monkeypatch.setenv('KIMI_API_KEY', 'dummy-key')  # 仍需要提供，因为验证时无法知道 provider
        monkeypatch.setenv('DATABASE_URL', 'postgresql://localhost/test')

        class TestSettings(Settings):
            model_config = SettingsConfigDict(
                env_file=str(env_file),
                env_file_encoding="utf-8",
                case_sensitive=False,
                extra="ignore"
            )

        settings = TestSettings()

        assert settings.llm_provider == 'zhipuai'
        assert settings.zhipuai_api_key == 'custom-zhipu-key'
        assert settings.zhipuai_model == 'glm-5'

    def test_should_raise_error_when_missing_required_field(self, monkeypatch, tmp_path):
        """测试缺少必需字段时应该抛出错误"""
        # 创建一个空的 .env 文件在临时目录
        env_file = tmp_path / ".env"
        env_file.write_text("")

        # 清除环境变量
        monkeypatch.delenv('KIMI_API_KEY', raising=False)
        monkeypatch.delenv('DATABASE_URL', raising=False)

        class TestSettings(Settings):
            model_config = SettingsConfigDict(
                env_file=str(env_file),
                env_file_encoding="utf-8",
                case_sensitive=False,
                extra="ignore"
            )

        with pytest.raises(ValidationError) as exc_info:
            TestSettings()

        assert 'kimi_api_key' in str(exc_info.value).lower() or 'database_url' in str(exc_info.value).lower()

    def test_should_validate_jwt_settings(self, monkeypatch):
        """测试 JWT 配置验证"""
        monkeypatch.setenv('KIMI_API_KEY', 'test-key')
        monkeypatch.setenv('JWT_SECRET_KEY', 'custom-secret')
        monkeypatch.setenv('JWT_ALGORITHM', 'HS512')
        monkeypatch.setenv('JWT_EXPIRATION_DAYS', '30')

        settings = Settings()

        assert settings.jwt_secret_key == 'custom-secret'
        assert settings.jwt_algorithm == 'HS512'
        assert settings.jwt_expiration_days == 30

    def test_should_validate_supabase_settings(self, monkeypatch):
        """测试 Supabase 配置验证"""
        monkeypatch.setenv('KIMI_API_KEY', 'test-key')
        monkeypatch.setenv('SUPABASE_URL', 'https://test.supabase.co')
        monkeypatch.setenv('SUPABASE_ANON_KEY', 'anon-key')
        monkeypatch.setenv('SUPABASE_SERVICE_ROLE_KEY', 'service-key')

        settings = Settings()

        assert settings.supabase_url == 'https://test.supabase.co'
        assert settings.supabase_anon_key == 'anon-key'
        assert settings.supabase_service_role_key == 'service-key'

    def test_should_validate_frontend_url(self, monkeypatch):
        """测试前端 URL 配置"""
        monkeypatch.setenv('KIMI_API_KEY', 'test-key')
        monkeypatch.setenv('FRONTEND_URL', 'http://localhost:3000')

        settings = Settings()

        assert settings.frontend_url == 'http://localhost:3000'


class TestGetSettings:
    """测试 get_settings 单例函数"""

    def test_should_return_singleton_instance(self, monkeypatch):
        """测试应该返回单例实例"""
        monkeypatch.setenv('KIMI_API_KEY', 'test-key')

        settings1 = get_settings()
        settings2 = get_settings()

        assert settings1 is settings2

    def test_should_cache_settings(self, monkeypatch):
        """测试应该缓存配置"""
        monkeypatch.setenv('KIMI_API_KEY', 'test-key')

        settings = get_settings()
        model = settings.kimi_model

        # 修改环境变量
        monkeypatch.setenv('KIMI_MODEL', 'kimi-k2.5')

        # 获取的应该是缓存的配置
        cached_settings = get_settings()
        assert cached_settings.kimi_model == model
