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


class APIUserIn(BaseModel):
    """User object for the REST API.

    Attributes:
        fullname: the fullname for the user.
        username: the username for the user.
        email: the emailaddress of the user.
        role: the role of the user (see UserRole).
    """

    fullname: str = Field(pattern=r'^[A-Za-z0-9\- ]+$', max_length=128)
    username: str = Field(pattern=r'^[a-zA-Z][a-zA-Z0-9_\.]+$', max_length=128)
    email: str = Field(
        pattern=r'^[a-z0-9_\-\.]+\@[a-z0-9_\-\.]+\.[a-z\.]+$',
        max_length=128)
    role: UserRole = Field(default=UserRole.USER)


class APIUser(APIUserIn):
    """User object for the REST API.

    Adds the `id` and `created` fields to the User model.

    Attributes:
        id: the id of the user.
        created: the creation datetime of the object
    """

    id: int | None = None
    created: datetime = Field(default_factory=datetime.utcnow)


class APITagIn(BaseModel):
    """Tag object for the REST API.

    Attributes:
        title: the title of the tag.
        color: the color of the tag.
    """

    title: str
    color: str | None = Field(
        default=None,
        pattern=r'^[a-fA-F0-9]{6}$',
        min_length=6,
        max_length=6)


class APITag(APITagIn):
    """Tag object for the REST API.

    Adds the `id` field to the Tag model.

    Attributes:
        id: the id of the tag.
    """

    id: int | None = None


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


class DeletionResult(BaseModel):
    """Model for the result of a deletion operation.

    Attributes:
        deleted_ids: a list with IDs that were deleted.
    """

    deleted: list[int]
