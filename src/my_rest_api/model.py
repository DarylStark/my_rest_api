"""Module that contains extra models for the REST API."""

from datetime import datetime
from enum import Enum
from typing import Generic, Optional, TypeVar

from my_model import UserRole
from pydantic import BaseModel, Field

T = TypeVar('T')


class Version(BaseModel):
    """Version information for the REST API.

    Attributes:
        version: The version of the REST API.
    """

    version: str | None


class Resource(BaseModel):
    """Base model for all resources.

    Contains all fields that models from the database have, like a unique id,
    a creation date and a last update date.
    """

    id: int
    uri: str
    created: datetime
    updated: datetime


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


class APIRefreshStatus(BaseModel):
    """Result of the API token refresh.

    Attributes:
        title: the title of the token.
        expires: the new expiration date of the token.
    """

    title: Optional[str]
    expires: Optional[datetime]
    new_token: Optional[str] = None


class APIAuthStatus(BaseModel):
    """Result of the API authentication status.

    Attributes:
        token_type: the type of the token (see APIAuthStatusToken).
        title: the title of the token.
        created: the creation datetime of the token.
        expires: the expiration datetime of the token.
    """

    token_type: APIAuthStatusToken
    title: Optional[str]
    created: Optional[datetime]
    expires: Optional[datetime]


class UserResourceIn(BaseModel):
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


class UserResource(UserResourceIn, Resource):
    """User object for the REST API."""


class TagResourceIn(BaseModel):
    """Tag object for the REST API.

    Attributes:
        title: the title of the tag.
        color: the color of the tag.
    """

    title: str
    color: str | None = Field(
        default=None, pattern=r'^[a-fA-F0-9]{6}$', min_length=6, max_length=6
    )


class TagResource(TagResourceIn, Resource):
    """Tag object for the REST API."""


class DeletionResult(BaseModel):
    """Model for the result of a deletion operation.

    Attributes:
        deleted_ids: a list with IDs that were deleted.
    """

    deleted: list[int]


class UserSettingResourceIn(BaseModel):
    """UserSetting object for the REST API body.

    Attributes:
        setting: the name of the setting.
        value: the value for the setting.
    """

    setting: str = Field(max_length=32)
    value: str = Field(max_length=32)


class UserSettingResource(UserSettingResourceIn, Resource):
    """UserSetting object for the REST API response."""


class APIClientResourceIn(BaseModel):
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


class APIClientResource(APIClientResourceIn, Resource):
    """APIClient object for the REST API response."""


class APITokenResource(Resource):
    """API Token object for the REST API.

    Attributes:
        expires: the expiration datetime of the object.
        api_client_id: the id of the api client.
        enabled: whether the token is enabled.
        title: the title of the token.
    """

    expires: datetime = Field(default_factory=datetime.utcnow)
    api_client_id: int | None = Field(default=None)
    enabled: bool = True
    title: str = Field(max_length=64)


class PaginationResult(BaseModel):
    """Pagination details for a retrieval result.

    Attributes:
        page: the current page.
        page_size: the maximum number of items on a page.
        total_pages: the total number of pages.
        total_items: the total number of items.
    """

    page: int
    page_size: int
    total_pages: int
    total_items: int


class RetrieveResult(BaseModel, Generic[T]):
    """Model for the result of a retrieval operation.

    Attributes:
        pagination: the pagination information.
        resources: the resources retrieved.
    """

    pagination: PaginationResult
    resources: list[T]


class APIError(BaseModel):
    """Model for error messages.

    Attributes:
        error: the error message.
    """

    error: str


class PasswordResetTokenRequest(BaseModel):
    """Model for request a password reset token.

    Attributes:
        password: the password for the user.
        second_factor: the second factor for the user.
    """

    password: str
    second_factor: str | None = None


class PasswordResetToken(BaseModel):
    """Model with a token for password reset.

    Attributes:
        token: the token that is generated for this request.
    """

    token: str


class PasswordResetRequest(BaseModel):
    """Model to set a new password for a user.

    Attributes:
        new_password: the password for the user.
        reset_token: the token that is generated for this request.
    """

    new_password: str
    reset_token: str


class PasswordResetStatus(str, Enum):
    """Enum for the status of the password reset result."""

    SUCCESS = 'success'
    FAILURE = 'failure'


class PasswordResetResult(BaseModel):
    """Result of a password reset.

    Attributes:
        status: The status of the reset.
    """

    status: PasswordResetStatus


class SecondFactorChangeTokenRequest(BaseModel):
    """Model for request a token to update the second factor settings.

    Attributes:
        password: the password for the user.
        second_factor: the second factor for the user.
        new_status: the new status for the second factor authentication.
    """

    password: str
    second_factor: str | None = None
    new_status: bool


class SecondFactorChangeToken(BaseModel):
    """Model with a token for second factor change.

    Attributes:
        token: the token that is generated for this request.
    """

    token: str


class SecondFactorChangeRequest(BaseModel):
    """Model to update the second factor settings for a user.

    Attributes:
        new_status: the new status for the second factor authentication.
        reset_token: the token that is generated for this request.
    """

    new_status: bool
    reset_token: str


class SecondFactorChangeRequestStatus(str, Enum):
    """Enum for the status of the second factor change result."""

    SUCCESS = 'success'
    FAILURE = 'failure'


class SecondFactorChangeRequestResult(BaseModel):
    """Result of a second factor change.

    Attributes:
        status: The status of the reset.
    """

    status: SecondFactorChangeRequestStatus
