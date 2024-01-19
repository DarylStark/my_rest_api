"""Functions for authentication."""
from datetime import datetime, timedelta

from my_model.user_scoped_models import APIToken, User

from .dependencies import app_config_object, my_data_object


def create_api_token_for_valid_user(user: User) -> str:
    """Create a API token for a valid user.

    Creates a API token for a valid user and returns the created token.

    Args:
        user: the user for which to create the API token.

    Returns:
        The created API token.
    """
    app_config = app_config_object()
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
