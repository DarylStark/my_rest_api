"""Module with the configuration model of the application."""

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class AppConfig(BaseSettings):
    """Configuration model of the application."""

    model_config = SettingsConfigDict(env_prefix='MY_REST_API_')
    database_str: str = 'sqlite:///:memory:/'
    service_user: str = Field(default=...)
    service_password: str = Field(default=...)
