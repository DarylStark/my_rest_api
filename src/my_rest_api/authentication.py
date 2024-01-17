"""Functions for authentication."""
from abc import ABC, abstractmethod
from datetime import datetime, timedelta
from typing import Optional, Type

from my_data.exceptions import UnknownUserAccountException
from my_model.user_scoped_models import APIToken, User, UserRole

from my_rest_api.exception import PermissionDeniedException

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


class Authenticator(ABC):
    """Base class for authenticators."""

    def __init__(
            self,
            api_token_authenticator: 'APITokenAuthenticator') -> None:
        """Initialize the authenticator.

        Args:
            api_token_authenticator: the API token authenticator.
        """
        self._api_token_authenticator = api_token_authenticator

    @abstractmethod
    def authenticate(self) -> None:
        """Authenticate the user."""


class LoggedOnAuthenticator(Authenticator):
    """Authenticator for logged on users."""

    def authenticate(self) -> None:
        """Authenticate the user and fail if he is not logged on.

        If the user is not logged on, a exception will be raised.

        Raises:
            PermissionDeniedException: when the user it not logged on.
        """
        if self._api_token_authenticator.user is None:
            raise PermissionDeniedException


class APITokenAuthenticator:
    """Authenticator for API tokens."""

    def __init__(
            self,
            api_token: str | None = None,
            authenticator: Type[Authenticator] | None = None):
        """Initialize the API token authenticator.

        Args:
            api_token: The API token to authenticate with.
            authenticator: The authenticator to use.
        """
        self._api_token_str = api_token
        if authenticator:
            self._authenticator: Optional[Authenticator] = authenticator(self)
        else:
            self._authenticator = None

        # Caches
        self._user: Optional[User] = None
        self._api_token: Optional[APIToken] = None

    def _get_user(self) -> Optional[User]:
        """Get the user for the given API token.

        Returns:
            The user for the API token, or None if the API token is invalid.
        """
        if not self._api_token_str:
            return None

        my_data = my_data_object()
        app_config = app_config_object()
        service_password = app_config.service_password
        service_user = app_config.service_user

        # Log in with a service user to retrieve the user.
        with my_data.get_context_for_service_user(
                username=service_user,
                password=service_password) as context:
            try:
                user = context.get_user_account_by_api_token(
                    api_token=self._api_token_str)
            except UnknownUserAccountException:
                pass
            else:
                return user
        return None

    def _get_api_token(self) -> Optional[APIToken]:
        """Get the API token for the given API token.

        Returns:
            The API token for the API token, or None if the API token is
            invalid.
        """
        if not self._api_token_str:
            return None

        my_data = my_data_object()
        user = self._get_user()
        if user:
            with my_data.get_context(user=user) as context:
                api_token = context.api_tokens.retrieve(
                    APIToken.token == self._api_token_str)  # type: ignore
                if api_token:
                    return api_token[0]
        return None

    def _get_user_role(self) -> Optional[UserRole]:
        """Get the user role for the given API token.

        Returns:
            The user role for the API token, or None if the API token is
            invalid.
        """
        user = self.user
        if not user:
            return None
        return user.role

    def authenticate(self) -> None:
        """Authenticate the user."""
        if self._authenticator:
            self._authenticator.authenticate()

    @property
    def user(self) -> Optional[User]:
        """Get the user for the given API token.

        When the user is not loaded yet, it will be loaded from the database
        and cached. When the user is already loaded, the cached user will be
        returned.

        Returns:
            The user for the API token, or None if the API token is invalid.
        """
        if not self._user:
            self._user = self._get_user()
        return self._user

    @property
    def api_token(self) -> Optional[APIToken]:
        """Get the API token for the given API token.

        When the API token is not loaded yet, it will be loaded from the
        database and cached. When the API token is already loaded, the cached
        API token will be returned.

        Returns:
            The API token for the API token, or None if the API token is
            invalid.
        """
        if not self._api_token:
            self._api_token = self._get_api_token()
        return self._api_token

    @property
    def is_valid_user(self) -> bool:
        """Check if the user is a valid user.

        Returns:
            True if the user is a valid user, False otherwise.
        """
        return self.user is not None

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
        return self._get_user_role() == UserRole.SERVICE

    @property
    def is_long_lived_token(self) -> bool:
        """Check if the token is a long lived token.

        Returns:
            True if the token is a long lived token, False otherwise.
        """
        if not self.api_token:
            return False
        return self.api_token.api_client_id is not None

    @property
    def is_short_lived_token(self) -> bool:
        """Check if the token is a short lived token.

        Returns:
            True if the token is a short lived token, False otherwise.
        """
        if not self.api_token:
            return False
        return self.api_token.api_client_id is None
