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
    title: str | None = None


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
        pattern=r'^[a-z0-9_\-\.]+\@[a-z0-9_\-\.]+\.[a-z\.]+$', max_length=128
    )
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
        default=None, pattern=r'^[a-fA-F0-9]{6}$', min_length=6, max_length=6
    )


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


class APIUserSettingIn(BaseModel):
    """UserSetting object for the REST API body.

    Attributes:
        setting: the name of the setting.
        value: the value for the setting.
    """

    setting: str = Field(max_length=32)
    value: str = Field(max_length=32)


class APIUserSetting(APIUserSettingIn):
    """UserSetting object for the REST API response.

    Adds the `id` field to the UserSetting model.

    Attributes:
        id: the id of the tag.
    """

    id: int | None = None


class APIAPIClientIn(BaseModel):
    """Client object for the REST API.

    Attributes:
        created: the creation datetime of the object.
        expires: the expiration datetime of the object.
        enabled: whether the client is enabled.
        app_name: the name of the app.
        app_publisher: the publisher of the app.
        redirect_url: the URL to redirect to after authentication.
    """

    created: datetime = Field(default_factory=datetime.utcnow)
    expires: datetime = Field(default_factory=datetime.utcnow)
    enabled: bool = True
    app_name: str = Field(max_length=64)
    app_publisher: str = Field(max_length=64)
    redirect_url: str | None = Field(
        default=None, pattern=r'^https?://', max_length=1024
    )


class APIAPIClient(APIAPIClientIn):
    """APIClient object for the REST API response.

    Adds the `id` field to the APIClient model.

    Attributes:
        id: the id of the api_client.
    """

    id: int | None = None


class APIAPIToken(BaseModel):
    """API Token object for the REST API.

    Attributes:
        id: the id of the api_token.
        created: the creation datetime of the object.
        expires: the expiration datetime of the object.
        api_client_id: the id of the api client.
        enabled: whether the token is enabled.
        title: the title of the token.
    """

    id: int | None = None
    created: datetime = Field(default_factory=datetime.utcnow)
    expires: datetime = Field(default_factory=datetime.utcnow)
    api_client_id: int | None = Field(default=None)
    enabled: bool = True
    title: str = Field(max_length=64)
