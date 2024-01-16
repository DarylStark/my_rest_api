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
    # database_str: str = 'sqlite:///database.sqlite'
    # database_str: str = 'sqlite:///database.sqlite'
    database_str: str = 'sqlite:///database.sqlite'
    database_args: dict[str, Any] | None = None
    service_user: str = Field(default='service.user')
    service_password: str = Field(default='service_password')

    # Authentication-session configuration
    session_timeout_in_seconds: int = Field(default=3600 * 24 * 7)

    # Configuration for `/version` for unauthorized users
    version_unauthorized: bool = False
    version_unauthorized_show_version: bool = False
    version_unauthorized_show_python_version: bool = False
    version_unauthorized_show_internal_libraries: bool = False
    version_unauthorized_show_external_libraries: bool = False

    # Configuration for `/version` for authorized users
    version_authorized_show_version: bool = True
    version_authorized_show_python_version: bool = False
    version_authorized_show_internal_libraries: bool = False
    version_authorized_show_external_libraries: bool = False
