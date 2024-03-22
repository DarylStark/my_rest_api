"""Module with the configuration model of the application."""

from typing import Any

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class AppConfig(BaseSettings):
    """Configuration model of the application."""

    model_config = SettingsConfigDict(env_prefix='MY_REST_API_')

    # FastAPI configuration
    debug: bool = Field(default=False)

    # Database configuration
    database_str: str = 'sqlite:////database.sqlite'
    database_args: dict[str, Any] | None = {'echo': False}
    service_user: str = Field(default='service.user')
    service_password: str = Field(default='service_password')

    # Authentication-session configuration
    session_timeout_in_seconds: int = Field(default=3600 * 24 * 7)
    session_refresh_in_seconds: int = Field(default=3600 * 24 * 2)

    # Paginating configuration
    default_page_size: int = 25
    max_page_size: int = 250

    # Logging configuration
    log_level: int = Field(default=30)
