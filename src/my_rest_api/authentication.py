"""Functions for authentication."""
from abc import ABC, abstractmethod
from datetime import datetime, timedelta
from typing import Optional

from my_data.exceptions import UnknownUserAccountException
from my_model.user_scoped_models import APIToken, User, UserRole

from my_rest_api.exception import (APIAuthenticationFailed,
                                   APITokenAuthenticatorAlreadySetException)

from .dependencies import app_config_object, my_data_object


class Authenticator(ABC):
    """Abstract base class for authenticators."""

    def __init__(self, api_authenticator: Optional['APIAuthenticator'] = None):
        """Initialize the authenticator.

        Args:
            api_authenticator: The API authenticator to use.
        """
        self._api_authenticator = api_authenticator

    def set_api_authenticator(self, api_authenticator: 'APIAuthenticator'):
        """Set the API authenticator.

        Args:
            api_authenticator: The API authenticator to use.

        Raises:
            APITokenAuthenticatorAlreadySetException: when the API token
                authenticator is already set.
        """
        if self._api_authenticator is not None:
            raise APITokenAuthenticatorAlreadySetException(
                'API token authenticator is already set.')
        self._api_authenticator = api_authenticator

    @abstractmethod
    def authenticate(self) -> User:
        """Authenticate the user.

        Returns:
            The authenticated user.
        """


class CredentialsAuthenticator(Authenticator):
    """Authenticator for credentials.

    Authenticates a user using his username, saved (hashed) password and
    optionally a two-factor authentication code. Gives a error when this
    fails.
    """

    def __init__(
        self,
        username: str,
        password: str,
        second_factor: Optional[str],
        api_authenticator: Optional['APIAuthenticator'] = None
    ) -> None:
        """Initialize the credentials authenticator.

        Will validate credentials and return the user if valid. If the user
        is a service user, the authentication will fail.

        Args:
            username: The username to use.
            password: The password to use.
            second_factor: The second factor to use.
            api_authenticator: The API authenticator to use.
        """
        super().__init__(api_authenticator=api_authenticator)
        self._username = username
        self._password = password
        self._second_factor = second_factor

    def authenticate(self) -> User:
        """Authenticate the user.

        If the authentication fails

        Returns:
            The authenticated user.

        Raises:
            APIAuthenticationFailed: when the authentication fails.
        """
        service_user = app_config_object().service_user
        service_password = app_config_object().service_password

        with my_data_object().get_context_for_service_user(
                username=service_user,
                password=service_password) as context:
            try:
                user = context.get_user_account_by_username(
                    username=self._username)

                if (user.second_factor is None and
                        self._second_factor is not None):
                    raise UnknownUserAccountException

                valid_credentials = user.verify_credentials(
                    username=self._username,
                    password=self._password,
                    second_factor=self._second_factor)

                if valid_credentials and (user.role is not UserRole.SERVICE):
                    return user
            except UnknownUserAccountException:
                pass

        raise APIAuthenticationFailed


class APIAuthenticator:
    """Authenticator for the API."""

    def __init__(self, authenticator: Authenticator) -> None:
        """Initialize the API authenticator.

        Args:
            authenticator: The authenticator to use.
        """
        self._authenticator: Authenticator = authenticator
        self._authenticator.set_api_authenticator(self)

    def authenticate(self) -> User:
        """Authenticate the user.

        This method is delegated to the authenticator. This way, the configured
        authenticator can be changed at runtime.

        Returns:
            The authenticated user.
        """
        return self._authenticator.authenticate()

    def create_api_token(self, title: str) -> str:
        """Create a API token for the authenticated user.

        Creates a API token for the authenticated user and returns the created
        token.

        Args:
            title: The title of the API token.

        Returns:
            The created API token.
        """
        app_config = app_config_object()
        new_api_token = APIToken(
            api_client_id=None,
            title=title,
            expires=datetime.now() + timedelta(
                seconds=app_config.session_timeout_in_seconds))
        token = new_api_token.set_random_token()
        my_data = my_data_object()
        with my_data.get_context(user=self.authenticate()) as context:
            context.api_tokens.create(new_api_token)
        return token
