"""Functions for authorization."""
from abc import ABC, abstractmethod
from typing import Optional

from my_data.exceptions import UnknownUserAccountException
from my_model.user_scoped_models import APIToken, User, UserRole

from my_rest_api.exception import (APITokenAuthorizerAlreadySetException,
                                   PermissionDeniedException)

from .dependencies import app_config_object, my_data_object


class Authorizer(ABC):
    """Base class for authorizers."""

    def __init__(
            self,
            api_token_authorizer: Optional['APITokenAuthorizer'] = None
    ) -> None:
        """Initialize the authorizer.

        Args:
            api_token_authorizer: the API token authorizer.
        """
        self._api_token_authorizer: Optional['APITokenAuthorizer'] = \
            api_token_authorizer

    def set_api_token_authorizer(
            self,
            api_token_authorizer: 'APITokenAuthorizer') -> None:
        """Set the API token authorizer.

        Fails if the API token authorizer is already set.

        Args:
            api_token_authorizer: the API token authorizer.

        Raises:
            APITokenAuthorizerAlreadySetException: when the API token
                authorizer is already set.
        """
        if self._api_token_authorizer is not None:
            raise APITokenAuthorizerAlreadySetException(
                'API token authorizer is already set.')
        self._api_token_authorizer = api_token_authorizer

    @abstractmethod
    def authorize(self) -> None:
        """Authorize the user."""


class LoggedOffAuthorizer(Authorizer):
    """Authorizer for logged off users.

    This authorizer will only fail if the user is logged on. If there
    is no user logged on, the authorization will succeed. This can be useful
    for endpoints that are only accessible for logged off users.
    """

    def authorize(self) -> None:
        """Authorize the user and fail if he is logged on.

        If the user is logged on, a exception will be raised.

        Raises:
            PermissionDeniedException: when the user it logged on.
        """
        if (self._api_token_authorizer and
                self._api_token_authorizer.user is not None):
            raise PermissionDeniedException


class LoggedOnAuthorizer(Authorizer):
    """Authorizer for logged on users.

    This authorizer will only fail if the user is not logged on. If there
    is a user logged on, the authorization will succeed. This can be useful
    for endpoints that are only accessible for logged on users, but that don't
    need any special permissions.
    """

    def authorize(self) -> None:
        """Authorize the user and fail if he is not logged on.

        If the user is not logged on, a exception will be raised.

        Raises:
            PermissionDeniedException: when the user it not logged on.
        """
        if (not self._api_token_authorizer or
                self._api_token_authorizer.user is None):
            raise PermissionDeniedException


class LoggedOnWithShortLivedAuthorizer(LoggedOnAuthorizer):
    """Authorization for logged on users with short lived tokens.

    This authorizer will fail if the logged on user is logged on with a API
    token that is not a short lived token. We subclass this class from
    LoggedOnAutorizer, because we want to reuse the authorize method.
    """

    def authorize(self) -> None:
        """Fails if he is not logged on with a short lived token.

        If the user is not logged on with a short lived token, a exception
        will be raised.

        Raises:
            PermissionDeniedException: when the user is not logged on with a
                short lived token.
        """
        super().authorize()
        if (not self._api_token_authorizer or
                self._api_token_authorizer.is_long_lived_token):
            raise PermissionDeniedException


class APITokenAuthorizer:
    """Authorizer for API tokens."""

    def __init__(
            self,
            api_token: str | None = None,
            authorizer: Authorizer | None = None):
        """Initialize the API token authorizer.

        Args:
            api_token: The API token to authorize with.
            authorizer: The authorizer to use.
        """
        self._api_token_str = api_token
        self._authorizer: Optional[Authorizer] = None

        # Set objects if authorizer is given
        if authorizer:
            self._authorizer = authorizer
            self._authorizer.set_api_token_authorizer(self)

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

    def authorize(self) -> None:
        """Authorize the user.

        This method is delegated to the authorizer. This way, the configured
        authorizer can be used to authorize the user and the user of the
        library can decide which authorize-scheme to use.
        """
        if self._authorizer:
            self._authorizer.authorize()

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
