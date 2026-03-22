"""
配置管理模块
使用 pydantic-settings 管理环境变量配置
"""
from typing import Optional
from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import Field, field_validator


class Settings(BaseSettings):
    """应用配置类"""

    # ========== LLM 提供商配置 ==========
    zhipuai_api_key: str = Field(..., description="智谱 AI API Key")
    zhipuai_base_url: Optional[str] = Field(
        default="https://open.bigmodel.cn/api/coding/paas/v4",
        description="智谱 AI Base URL (Coding Plan)"
    )
    zhipuai_model: str = Field(default="glm-5", description="智谱 AI 模型 (Coding Plan 使用 glm-5)")

    # ========== Supabase 配置 ==========
    supabase_url: Optional[str] = Field(default=None, description="Supabase URL")
    supabase_anon_key: Optional[str] = Field(default=None, description="Supabase 匿名密钥")
    supabase_service_role_key: Optional[str] = Field(
        default=None,
        description="Supabase 服务角色密钥"
    )

    # ========== 数据库配置 ==========
    database_url: str = Field(..., description="数据库连接字符串")

    # ========== JWT 配置 ==========
    jwt_secret_key: str = Field(
        default="dev-secret-key-change-in-production",
        description="JWT 密钥"
    )
    jwt_algorithm: str = Field(default="HS256", description="JWT 算法")
    jwt_expiration_days: int = Field(default=7, description="JWT 过期时间（天）")

    # ========== 应用配置 ==========
    app_name: str = Field(default="Web Agent Demo", description="应用名称")
    app_version: str = Field(default="0.1.0", description="应用版本")
    log_level: str = Field(default="INFO", description="日志级别")
    max_iterations: int = Field(default=5, description="最大迭代次数")

    # ========== CORS 配置 ==========
    frontend_url: str = Field(
        default="http://localhost:5173",
        description="前端 URL"
    )

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore"
    )

    @field_validator("log_level")
    @classmethod
    def validate_log_level(cls, v: str) -> str:
        """验证日志级别"""
        valid_levels = ["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"]
        if v.upper() not in valid_levels:
            raise ValueError(f"日志级别必须是以下之一: {', '.join(valid_levels)}")
        return v.upper()

    @field_validator("max_iterations")
    @classmethod
    def validate_max_iterations(cls, v: int) -> int:
        """验证最大迭代次数"""
        if v < 1 or v > 20:
            raise ValueError("最大迭代次数必须在 1-20 之间")
        return v


# 全局配置实例（单例）
_settings: Optional[Settings] = None


def get_settings() -> Settings:
    """获取配置单例"""
    global _settings
    if _settings is None:
        _settings = Settings()
    return _settings
