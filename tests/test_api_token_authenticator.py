"""Tests for the APITokenAuthenticator class."""

from fastapi.testclient import TestClient
from my_rest_api.authentication import APITokenAuthenticator


def test_user_property(
        api_client: TestClient,  # pylint: disable=unused-argument
        random_api_token_root: str) -> None:
    """Test the `user` property of the APITokenAuthenticator class.

    Args:
        api_client: the test client for making API requests. Not used in this
            test but needed to create the database.
        random_api_token_root: a random API token for a root user.
    """
    authenticator = APITokenAuthenticator(api_key=random_api_token_root)
    assert authenticator.user is not None
    assert authenticator.user.username == 'root'


def test_user_property_wrong_token(
        api_client: TestClient,  # pylint: disable=unused-argument
) -> None:
    """Test the `user` property of the APITokenAuthenticator class.

    Args:
        api_client: the test client for making API requests. Not used in this
            test but needed to create the database.
    """
    authenticator = APITokenAuthenticator(api_key='wrong_token')
    assert authenticator.user is None


def test_api_token_property(
        api_client: TestClient,  # pylint: disable=unused-argument
        random_api_token_root: str) -> None:
    """Test the `api_token` property of the APITokenAuthenticator class.

    Args:
        api_client: the test client for making API requests. Not used in this
            test but needed to create the database.
        random_api_token_root: a random API token for a root user.
    """
    authenticator = APITokenAuthenticator(api_key=random_api_token_root)
    assert authenticator.api_token is not None
    assert authenticator.api_token.token == random_api_token_root


def test_token_property_wrong_token(
        api_client: TestClient,  # pylint: disable=unused-argument
) -> None:
    """Test the `api_token` property of the APITokenAuthenticator class.

    Args:
        api_client: the test client for making API requests. Not used in this
            test but needed to create the database.
    """
    authenticator = APITokenAuthenticator(api_key='wrong_token')
    assert authenticator.api_token is None


def test_role_property_root(
        api_client: TestClient,  # pylint: disable=unused-argument
        random_api_token_root: str) -> None:
    """Test the roles property of the APITokenAuthenticator class.

    For root users.

    Args:
        api_client: the test client for making API requests. Not used in this
            test but needed to create the database.
        random_api_token_root: a random API token for a root user.
    """
    authenticator = APITokenAuthenticator(api_key=random_api_token_root)
    assert authenticator.is_root
    assert not authenticator.is_normal_user
    assert not authenticator.is_service_user


def test_role_property_wrong_token(
        api_client: TestClient,  # pylint: disable=unused-argument
) -> None:
    """Test the roles property of the APITokenAuthenticator class.

    For wrong tokens.

    Args:
        api_client: the test client for making API requests. Not used in this
            test but needed to create the database.
    """
    authenticator = APITokenAuthenticator(api_key='wrong_token')
    assert not authenticator.is_root
    assert not authenticator.is_normal_user
    assert not authenticator.is_service_user


def test_role_property_normal_user(
        api_client: TestClient,  # pylint: disable=unused-argument
        random_api_token_normal_user: str) -> None:
    """Test the roles property of the APITokenAuthenticator class.

    For normal user.

    Args:
        api_client: the test client for making API requests. Not used in this
            test but needed to create the database.
        random_api_token_normal_user: a random API token for a normal user.
    """
    authenticator = APITokenAuthenticator(api_key=random_api_token_normal_user)
    assert not authenticator.is_root
    assert authenticator.is_normal_user
    assert not authenticator.is_service_user


def test_user_property_without_api_token(
        api_client: TestClient,  # pylint: disable=unused-argument
) -> None:
    """Test the `user` property of the APITokenAuthenticator class.

    Args:
        api_client: the test client for making API requests. Not used in this
            test but needed to create the database.
    """
    authenticator = APITokenAuthenticator()
    assert authenticator.user is None


def test_api_token_property_without_api_token(
        api_client: TestClient,  # pylint: disable=unused-argument
) -> None:
    """Test the `api_token` property of the APITokenAuthenticator class.

    Args:
        api_client: the test client for making API requests. Not used in this
            test but needed to create the database.
    """
    authenticator = APITokenAuthenticator()
    assert authenticator.api_token is None
