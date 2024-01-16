"""API endpoints for authentication."""
from typing import Annotated
from fastapi import APIRouter, Depends, HTTPException, Header
from my_data.exceptions import UnknownUserAccountException
from my_data.my_data import MyData
from my_model.user_scoped_models import UserRole, APIToken

from my_rest_api.my_rest_api import MyRESTAPI

from .app_config import AppConfig
from .authentication import create_api_token_for_valid_user, get_user_for_api_key
from .dependencies import app_config_object, my_data_object
from .model import (AuthenticationDetails, AuthenticationResult,
                    AuthenticationResultStatus)

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


@api_router.post('/logout')
def logout(
    x_api_key: Annotated[str | None, Header()] = None,
    my_data: MyData = Depends(my_data_object)
) -> dict[str, str]:
    """Logout from the REST API.

    Args:
        x_api_key: The API key to use for authentication.

    Returns:
        An empty dictionary.

    Raises:
        HTTPException: if the API key is invalid or not a short lived API
            token.
    """
    user = get_user_for_api_key(api_key=x_api_key)
    if user:
        with my_data.get_context(user=user) as context:
            api_token = context.api_tokens.retrieve(
                APIToken.token == x_api_key)
            if api_token and len(api_token) == 1 and api_token[0].api_client is None:
                context.api_tokens.delete(api_token)
    return {'status': 'success'}
