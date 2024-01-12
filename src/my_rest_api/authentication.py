"""Functions for authentication."""
from datetime import datetime, timedelta
from typing import Optional

from my_model.user_scoped_models import APIToken, User

from .app_config import AppConfig
from .dependencies import my_data_object


def create_api_token_for_valid_user(user: User) -> str:
    """Create a API token for a valid user.

    Creates a API token for a valid user and returns the created token.

    Args:
        user: the user for which to create the API token.

    Returns:
        The created API token.
    """
    app_config = AppConfig()
    new_api_token = APIToken(
        api_client_id=None,
        title='Interactive API token',
        expires=datetime.now() + timedelta(
            seconds=app_config.session_timeout_in_seconds))
    token = new_api_token.set_random_token()
    my_data = my_data_object()
    with my_data.get_context(user=user) as context:
        context.api_tokens.create(new_api_token)
    return token


def get_user_for_api_key(api_key: str | None) -> Optional[User]:
    """Get the user for the given API key.

    Args:
        api_key: The API key to get the user for.

    Returns:
        The user for the API key, or None if the API key is invalid.
    """
    if not api_key:
        return None

    my_data = my_data_object()
    app_config = AppConfig()
    service_user = app_config.service_user
    service_password = app_config.service_password

    # Log in with a service user to retrieve the user.
    user = None
    with my_data.get_context_for_service_user(
            username=service_user,
            password=service_password) as context:
        user = context.get_user_account_by_api_token(api_token=api_key)
    return user
