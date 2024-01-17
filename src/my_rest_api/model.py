"""Module that contains extra models for the REST API."""

from enum import Enum
from pydantic import BaseModel, Field


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
        api_key: The API key for the user, if applicable.
    """

    status: AuthenticationResultStatus
    api_key: str | None = Field(pattern=r'^[a-zA-Z0-9]{32}$')


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
    """

    token_type: APIAuthStatusToken
