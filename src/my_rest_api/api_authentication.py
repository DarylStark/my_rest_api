"""API endpoints for authentication."""
from fastapi import APIRouter, HTTPException
from my_data.exceptions import UnknownUserAccountException
from my_model.user_scoped_models import UserRole

from .app_config import AppConfig
from .authentication import create_api_token_for_valid_user
from .dependencies import my_data_object
from .model import AuthenticationDetails, AuthenticationResult, AuthenticationResultStatus

api_router = APIRouter()


@api_router.post('/login')
def login(
    authentication: AuthenticationDetails
) -> AuthenticationResult:
    """Login to the REST API.

    Args:
        authentication: authentication details.

    Returns:
        A dictionary containing the authentication token.

    Raises:
        HTTPException: if the authentication details are incorrect or
            incomplete. This can also mean that the username and password are
            correct, but that the user needs to provide a second factor.
    """
    my_data = my_data_object()
    app_config = AppConfig()
    service_user = app_config.service_user
    service_password = app_config.service_password

    # Log in with a service user to retrieve the user.
    with my_data.get_context_for_service_user(
            username=service_user,
            password=service_password) as context:
        try:
            user = context.get_user_account_by_username(
                username=authentication.username)

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
