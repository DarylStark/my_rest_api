"""Module with the configuration model of the application."""

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Configuration model of the application."""

    model_config = SettingsConfigDict(env_prefix='MY_REST_API_')
    database_str: str = 'sqlite:///:memory:/'
