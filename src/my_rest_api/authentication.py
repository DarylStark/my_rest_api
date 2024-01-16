"""Functions for authentication."""
from curses.ascii import US
from datetime import datetime, timedelta
from typing import Optional

from my_data.exceptions import UnknownUserAccountException
from my_model.user_scoped_models import APIToken, User, UserRole

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
    app_config = app_config_object()
    service_user = app_config.service_user
    service_password = app_config.service_password

    # Log in with a service user to retrieve the user.
    user = None
    with my_data.get_context_for_service_user(
            username=service_user,
            password=service_password) as context:
        user = context.get_user_account_by_api_token(api_token=api_key)
    return user


class APITokenAuthenticator:
    """Authenticator for API tokens."""

    def __init__(self, api_key: str | None = None):
        """Initialize the API token authenticator.

        Args:
            api_key: The API key to authenticate with.
        """
        self.api_key = api_key

        # Caches
        self._user: Optional[User] = None
        self._api_token: Optional[APIToken] = None

    def _get_user(self) -> Optional[User]:
        """Get the user for the given API key.

        Returns:
            The user for the API key, or None if the API key is invalid.
        """
        if not self.api_key:
            return None

        my_data = my_data_object()
        app_config = app_config_object()
        service_user = app_config.service_user
        service_password = app_config.service_password

        # Log in with a service user to retrieve the user.
        with my_data.get_context_for_service_user(
                username=service_user,
                password=service_password) as context:
            try:
                user = context.get_user_account_by_api_token(
                    api_token=self.api_key)
            except UnknownUserAccountException:
                pass
            else:
                return user
        return None

    def _get_api_token(self) -> Optional[APIToken]:
        """Get the API token for the given API key.

        Returns:
            The API token for the API key, or None if the API key is invalid.
        """
        if not self.api_key:
            return None

        my_data = my_data_object()
        user = self._get_user()
        if user:
            with my_data.get_context(user=user) as context:
                api_token = context.api_tokens.retrieve(
                    APIToken.token == self.api_key)  # type: ignore
                if api_token:
                    return api_token[0]
        return None

    def _get_user_role(self) -> Optional[UserRole]:
        """Get the user role for the given API key.

        Returns:
            The user role for the API key, or None if the API key is invalid.
        """
        user = self.user
        if not user:
            return None
        return user.role

    @property
    def user(self) -> Optional[User]:
        """Get the user for the given API key.

        When the user is not loaded yet, it will be loaded from the database
        and cached. When the user is already loaded, the cached user will be
        returned.

        Returns:
            The user for the API key, or None if the API key is invalid.
        """
        if not self._user:
            self._user = self._get_user()
        return self._user

    @property
    def api_token(self) -> Optional[APIToken]:
        """Get the API token for the given API key.

        When the API token is not loaded yet, it will be loaded from the
        database and cached. When the API token is already loaded, the cached
        API token will be returned.

        Returns:
            The API token for the API key, or None if the API key is invalid.
        """
        if not self._api_token:
            self._api_token = self._get_api_token()
        return self._api_token

    @property
    def is_root(self) -> bool:
        """Check if the user is a root user.

        Returns:
            True if the user is a root user, False otherwise.
        """
        return self._get_user_role() == UserRole.ROOT

    @property
    def is_normal_user(self) -> bool:
        """Check if the user is a normal user.

        Returns:
            True if the user is a normal user, False otherwise.
        """
        if not self.user:
            return False
        return self._get_user_role() == UserRole.USER

    @property
    def is_service_user(self) -> bool:
        """Check if the user is a service user.

        Returns:
            True if the user is a service user, False otherwise.
        """
        if not self.user:
            return False
        return self._get_user_role() == UserRole.SERVICE
