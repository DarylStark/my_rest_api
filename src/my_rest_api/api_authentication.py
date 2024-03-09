"""API endpoints for authentication."""
from datetime import datetime, timedelta
from typing import Annotated

from fastapi import APIRouter, Depends, Header
from my_data.authenticator import CredentialsAuthenticator, UserAuthenticator
from my_data.authorizer import (
    APITokenAuthorizer,
    InvalidTokenAuthorizer,
    ShortLivedTokenAuthorizer,
    ValidTokenAuthorizer,
)
from my_data.my_data import MyData

from .app_config import AppConfig
from .dependencies import my_data_object
from .model import (
    APIAuthStatus,
    APIAuthStatusToken,
    APIRefreshStatus,
    AuthenticationDetails,
    AuthenticationResult,
    AuthenticationResultStatus,
    LogoutResult,
)

api_router = APIRouter()


@api_router.post('/login')
def login(
    authentication: AuthenticationDetails,
    x_api_token: Annotated[str | None, Header()] = None,
    my_data: MyData = Depends(my_data_object),
) -> AuthenticationResult:
    """Login to the REST API.

    Args:
        authentication: authentication details.
        x_api_token: The API token to use for authentication. Should be empty
            or a invalid token.
        my_data: a global MyData object.

    Returns:
        A dictionary containing the authentication token.

    Raises:
        HTTPException: if the authentication details are incorrect or
            incomplete. This can also mean that the username and password are
            correct, but that the user needs to provide a second factor.
    """
    auth = APITokenAuthorizer(
        my_data_object=my_data,
        api_token=x_api_token,
        authorizer=InvalidTokenAuthorizer(),
    )
    auth.authorize()

    authenticator = UserAuthenticator(
        my_data_object=my_data,
        authenticator=CredentialsAuthenticator(
            username=authentication.username,
            password=authentication.password,
            second_factor=authentication.second_factor,
        ),
    )
    authenticator.authenticate()

    token_title: str = (
        authentication.title
        or f'Session from {datetime.now().strftime("%Y-%m-%d, %H:%M:%S")}'
    )
    return AuthenticationResult(
        status=AuthenticationResultStatus.SUCCESS,
        api_token=authenticator.create_api_token(
            session_timeout_in_seconds=AppConfig().session_timeout_in_seconds,
            title=token_title,
        ),
    )


@api_router.get('/logout')
def logout(
    x_api_token: Annotated[str | None, Header()] = None,
    my_data: MyData = Depends(my_data_object),
) -> LogoutResult:
    """Logout from the REST API.

    Args:
        x_api_token: The API token to use for authentication.
        my_data: a global MyData object.

    Returns:
        An empty dictionary.
    """
    auth = APITokenAuthorizer(
        my_data_object=my_data,
        api_token=x_api_token,
        authorizer=ShortLivedTokenAuthorizer(),
    )
    auth.authorize()

    user = auth.user
    if user:
        with my_data.get_context(user=user) as context:
            if auth.api_token:
                context.api_tokens.delete(auth.api_token)
    return LogoutResult(status=AuthenticationResultStatus.SUCCESS)


@api_router.get('/status')
def status(
    x_api_token: Annotated[str | None, Header()] = None,
    my_data: MyData = Depends(my_data_object),
) -> APIAuthStatus:
    """Get API token information.

    Args:
        x_api_token: The API token to use for authentication.
        my_data: a global MyData object.

    Returns:
        An status information object.
    """
    auth = APITokenAuthorizer(
        my_data_object=my_data,
        api_token=x_api_token,
        authorizer=ValidTokenAuthorizer(),
    )
    auth.authorize()

    token_type = (
        APIAuthStatusToken.LONG_LIVED
        if auth.is_long_lived_token
        else APIAuthStatusToken.SHORT_LIVED
    )

    return APIAuthStatus(
        token_type=token_type,
        title=auth.api_token.title if auth.api_token else None,
        created=auth.api_token.created if auth.api_token else None,
        expires=auth.api_token.expires if auth.api_token else None,
    )


@api_router.get('/refresh')
def refresh(
    x_api_token: Annotated[str | None, Header()] = None,
    my_data: MyData = Depends(my_data_object),
) -> APIRefreshStatus:
    """Refresh a short-lived token.

    Refreshing a short live token make sure the token is valid longer. The user
    has to do this before the token expires. The new expiration date is
    calculated from the current date and the session_refresh_in_seconds
    configuration value. If the token is already valid longer, the expiration
    date is not changed.

    Args:
        x_api_token: The API token to use for authentication.
        my_data: a global MyData object.

    Returns:
        The new token.
    """
    auth = APITokenAuthorizer(
        my_data_object=my_data,
        api_token=x_api_token,
        authorizer=ShortLivedTokenAuthorizer(),
    )
    auth.authorize()

    new_expiration_date = datetime.now() + timedelta(
        seconds=AppConfig().session_refresh_in_seconds
    )

    user = auth.user
    if user:
        with my_data.get_context(user=user) as context:
            if auth.api_token:
                if new_expiration_date < auth.api_token.expires:
                    new_expiration_date = auth.api_token.expires
                api_token = auth.api_token
                api_token.expires = new_expiration_date
                context.api_tokens.update(api_token)
    return APIRefreshStatus(
        title=auth.api_token.title if auth.api_token else None,
        expires=auth.api_token.expires if auth.api_token else None,
    )
