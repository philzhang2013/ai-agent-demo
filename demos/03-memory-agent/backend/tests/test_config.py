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
            if key.startswith(('ZHIPUAI_', 'SUPABASE_', 'JWT_', 'APP_', 'LOG_', 'MAX_', 'FRONTEND_', 'DATABASE_')):
                monkeypatch.delenv(key, raising=False)

        # 设置必需的环境变量
        monkeypatch.setenv('ZHIPUAI_API_KEY', 'test-key')
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

        assert settings.zhipuai_api_key == 'test-key'
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

        monkeypatch.setenv('ZHIPUAI_API_KEY', 'custom-key')
        monkeypatch.setenv('ZHIPUAI_MODEL', 'glm-5')
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

        assert settings.zhipuai_api_key == 'custom-key'
        assert settings.zhipuai_model == 'glm-5'
        assert settings.log_level == 'DEBUG'
        assert settings.max_iterations == 10

    def test_should_raise_error_when_missing_required_field(self, monkeypatch, tmp_path):
        """测试缺少必需字段时应该抛出错误"""
        # 创建一个空的 .env 文件在临时目录
        env_file = tmp_path / ".env"
        env_file.write_text("")

        # 清除环境变量
        monkeypatch.delenv('ZHIPUAI_API_KEY', raising=False)
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

        assert 'zhipuai_api_key' in str(exc_info.value).lower() or 'database_url' in str(exc_info.value).lower()

    def test_should_validate_jwt_settings(self, monkeypatch):
        """测试 JWT 配置验证"""
        monkeypatch.setenv('ZHIPUAI_API_KEY', 'test-key')
        monkeypatch.setenv('JWT_SECRET_KEY', 'custom-secret')
        monkeypatch.setenv('JWT_ALGORITHM', 'HS512')
        monkeypatch.setenv('JWT_EXPIRATION_DAYS', '30')

        settings = Settings()

        assert settings.jwt_secret_key == 'custom-secret'
        assert settings.jwt_algorithm == 'HS512'
        assert settings.jwt_expiration_days == 30

    def test_should_validate_supabase_settings(self, monkeypatch):
        """测试 Supabase 配置验证"""
        monkeypatch.setenv('ZHIPUAI_API_KEY', 'test-key')
        monkeypatch.setenv('SUPABASE_URL', 'https://test.supabase.co')
        monkeypatch.setenv('SUPABASE_ANON_KEY', 'anon-key')
        monkeypatch.setenv('SUPABASE_SERVICE_ROLE_KEY', 'service-key')

        settings = Settings()

        assert settings.supabase_url == 'https://test.supabase.co'
        assert settings.supabase_anon_key == 'anon-key'
        assert settings.supabase_service_role_key == 'service-key'

    def test_should_validate_frontend_url(self, monkeypatch):
        """测试前端 URL 配置"""
        monkeypatch.setenv('ZHIPUAI_API_KEY', 'test-key')
        monkeypatch.setenv('FRONTEND_URL', 'http://localhost:3000')

        settings = Settings()

        assert settings.frontend_url == 'http://localhost:3000'


class TestGetSettings:
    """测试 get_settings 单例函数"""

    def test_should_return_singleton_instance(self, monkeypatch):
        """测试应该返回单例实例"""
        monkeypatch.setenv('ZHIPUAI_API_KEY', 'test-key')

        settings1 = get_settings()
        settings2 = get_settings()

        assert settings1 is settings2

    def test_should_cache_settings(self, monkeypatch):
        """测试应该缓存配置"""
        monkeypatch.setenv('ZHIPUAI_API_KEY', 'test-key')

        settings = get_settings()
        model = settings.zhipuai_model

        # 修改环境变量
        monkeypatch.setenv('ZHIPUAI_MODEL', 'glm-5')

        # 获取的应该是缓存的配置
        cached_settings = get_settings()
        assert cached_settings.zhipuai_model == model
