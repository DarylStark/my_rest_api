"""API endpoints for authentication."""
from typing import Annotated

from fastapi import APIRouter, Depends, Header, HTTPException
from my_data.exceptions import UnknownUserAccountException
from my_data.my_data import MyData
from my_model.user_scoped_models import UserRole

from .app_config import AppConfig
from .authentication import (APITokenAuthenticator, LoggedOnAuthenticator,
                             create_api_token_for_valid_user)
from .dependencies import app_config_object, my_data_object
from .model import (APIAuthStatus, APIAuthStatusToken, AuthenticationDetails,
                    AuthenticationResult, AuthenticationResultStatus,
                    LogoutResult)

api_router = APIRouter()


@api_router.post('/login')
def login(
    authentication: AuthenticationDetails,
    my_data: MyData = Depends(my_data_object),
    app_config: AppConfig = Depends(app_config_object)
) -> AuthenticationResult:
    """Login to the REST API.

    Args:
        authentication: authentication details.
        my_data: a global MyData object.
        app_config: a global AppConfig object.

    Returns:
        A dictionary containing the authentication token.

    Raises:
        HTTPException: if the authentication details are incorrect or
            incomplete. This can also mean that the username and password are
            correct, but that the user needs to provide a second factor.
    """
    service_user = app_config.service_user
    service_password = app_config.service_password

    # Log in with a service user to retrieve the user.
    with my_data.get_context_for_service_user(
            username=service_user,
            password=service_password) as context:
        try:
            user = context.get_user_account_by_username(
                username=authentication.username)

            if (user.second_factor is None and
                    authentication.second_factor is not None):
                raise UnknownUserAccountException

            valid_credentials = user.verify_credentials(
                username=authentication.username,
                password=authentication.password,
                second_factor=authentication.second_factor)

            if valid_credentials and (user.role is not UserRole.SERVICE):
                token = create_api_token_for_valid_user(user=user)
                return AuthenticationResult(
                    status=AuthenticationResultStatus.SUCCESS,
                    api_key=token)
        except UnknownUserAccountException:
            pass

    raise HTTPException(
        status_code=401,
        detail=AuthenticationResult(
            status=AuthenticationResultStatus.FAILURE,
            api_key=None)
    )


@api_router.get('/logout')
def logout(
    x_api_key: Annotated[str | None, Header()] = None,
    my_data: MyData = Depends(my_data_object)
) -> LogoutResult:
    """Logout from the REST API.

    Args:
        x_api_key: The API key to use for authentication.
        my_data: a global MyData object.

    Returns:
        An empty dictionary.
    """
    auth = APITokenAuthenticator(
        api_key=x_api_key,
        authenticator=LoggedOnAuthenticator)
    auth.authenticate()

    user = auth.user
    if user:
        with my_data.get_context(user=user) as context:
            if auth.api_token:
                context.api_tokens.delete(auth.api_token)
    return LogoutResult(status=AuthenticationResultStatus.SUCCESS)


@api_router.get('/status')
def status(
        x_api_key: Annotated[str | None, Header()] = None) -> APIAuthStatus:
    """Get API token information.

    Args:
        x_api_key: The API key to use for authentication.

    Returns:
        An status information object.
    """
    auth = APITokenAuthenticator(
        api_key=x_api_key,
        authenticator=LoggedOnAuthenticator)
    auth.authenticate()

    return APIAuthStatus(
        token=APIAuthStatusToken.LONG_LIVED
        if auth.is_long_lived_token else APIAuthStatusToken.SHORT_LIVED)
