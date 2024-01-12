"""API endpoints for authentication."""
from fastapi import APIRouter, Depends, HTTPException
from my_data.exceptions import UnknownUserAccountException
from my_data.my_data import MyData

from .app_config import AppConfig
from .dependencies import my_data_object
from .model import AuthenticationDetails, AuthenticationResult

from my_model.user_scoped_models import User, APIToken, UserRole

api_router = APIRouter()


def create_api_token_for_valid_user(user: User) -> str:
    """Create a API token for a valid user.

    Creates a API token for a valid user and returns the created token.

    Args:
        user: the user for which to create the API token.
    """
    new_api_token = APIToken(
        api_client_id=None,
        title='Interactive API token')
    token = new_api_token.set_random_token()
    my_data = my_data_object()
    with my_data.get_context(user=user) as context:
        context.api_tokens.create(new_api_token)
    return token


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
            incomplete.
    """
    my_data = my_data_object()

    # Defaults
    valid_user = False
    second_factor_required = False

    # Log in with a service user to retrieve the user.
    with my_data.get_context_for_service_user(
            username=AppConfig().service_user,
            password=AppConfig().service_password) as context:
        # Retrieve the user.
        try:
            user = context.get_user_account_by_username(
                username=authentication.username)

            interactive_user = user.role is not UserRole.SERVICE

            valid_credentials = user.verify_credentials(
                username=authentication.username,
                password=authentication.password,
                second_factor=authentication.second_factor)

            valid_user = interactive_user and valid_credentials

            if (user.second_factor is not None and
                    authentication.second_factor is None):
                second_factor_required = True
        except UnknownUserAccountException:
            pass

    if second_factor_required:
        raise HTTPException(
            status_code=412,
            detail=AuthenticationResult(
                status='correct',
                api_key=None)
        )

    if valid_user:
        token = create_api_token_for_valid_user(user=user)
        return AuthenticationResult(
            status='correct',
            api_key=token)

    raise HTTPException(
        status_code=401,
        detail=AuthenticationResult(
            status='incorrect',
            api_key=None)
    )
