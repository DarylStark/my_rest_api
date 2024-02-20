"""Module that contains extra models for the REST API."""

from datetime import datetime
from enum import Enum
from typing import Optional

from my_model import UserRole
from pydantic import BaseModel, Field

from my_rest_api.app_config import AppConfig


class Version(BaseModel):
    """Version information for the REST API.

    Attributes:
        version: The version of the REST API.
    """

    version: str | None


class AuthenticationDetails(BaseModel):
    """Authentication details for the REST API.

    Attributes:
        username: The username for the user.
        password: The password for the user.
        second_factor: The second factor for authentication, if applicable.
    """

    username: str
    password: str
    second_factor: str | None = None


class AuthenticationResultStatus(str, Enum):
    """Enum for the status of the authentication result."""

    SUCCESS = 'success'
    FAILURE = 'failure'


class AuthenticationResult(BaseModel):
    """Result of authentication.

    Attributes:
        status: The status of the authentication.
        api_token: The API token for the user, if applicable.
    """

    status: AuthenticationResultStatus
    api_token: str | None = Field(default=None, pattern=r'^[a-zA-Z0-9]{32}$')


class ErrorModel(BaseModel):
    """Error model for the REST API.

    Attributes:
        error: The error message.
    """

    error: str = 'Unknown error'


class LogoutResult(BaseModel):
    """Result of logout.

    Attributes:
        status: The status of the logout.
    """

    status: AuthenticationResultStatus


class APIAuthStatusToken(str, Enum):
    """Enum for the status of the authentication result."""

    LONG_LIVED = 'long-lived'
    SHORT_LIVED = 'short-lived'


class APIAuthStatus(BaseModel):
    """Result of the API authentication status.

    Attributes:
        token: information about the token.
        title: the title of the token.
    """

    token_type: APIAuthStatusToken
    title: Optional[str]
    created: Optional[datetime]
    expires: Optional[datetime]


class UserWithoutPassword(BaseModel):
    """User object without password.

    Attributes:
        id: the id of the user.
        created: the datetime when this user was created.
        fullname: the fullname for the user.
        username: the username for the user.
        email: the emailaddress of the user.
        role: the role of the user (see UserRole).
    """

    id: int
    created: datetime = Field(default_factory=datetime.utcnow)
    fullname: str
    username: str
    email: str
    role: UserRole = Field(default=UserRole.USER)


class PaginationError(BaseModel):
    """Model for errors that indicate a pagination error.

    Attributes:
        message: The detail of the error.
        max_page_size: The maximum page size allowed.
    """

    message: str
    max_page_size: int = AppConfig().max_page_size
    max_page: int | None = None


class SortError(BaseModel):
    """Model for errors that indicate a sort error.

    Attributes:
        message: The detail of the error.
    """

    message: str
    allowed_sort_fields: list[str]
