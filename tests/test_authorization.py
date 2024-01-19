"""Tests for the APITokenAuthorizer class."""

from fastapi.testclient import TestClient
import pytest
from my_rest_api.authorization import APITokenAuthorizer, LoggedOffAuthorizer
from my_rest_api.exception import APITokenAuthorizerAlreadySetException


def test_user_property(
        api_client: TestClient,  # pylint: disable=unused-argument
        random_api_token_root: str) -> None:
    """Test the `user` property of the APITokenAuthorizer class.

    Args:
        api_client: the test client for making API requests. Not used in this
            test but needed to create the database.
        random_api_token_root: a random API token for a root user.
    """
    authorizer = APITokenAuthorizer(api_token=random_api_token_root)
    assert authorizer.user is not None
    assert authorizer.user.username == 'root'


def test_user_property_wrong_token(
        api_client: TestClient,  # pylint: disable=unused-argument
) -> None:
    """Test the `user` property of the APITokenAuthenticator class.

    Args:
        api_client: the test client for making API requests. Not used in this
            test but needed to create the database.
    """
    authorizer = APITokenAuthorizer(api_token='wrong_token')
    assert authorizer.user is None


def test_api_token_property(
        api_client: TestClient,  # pylint: disable=unused-argument
        random_api_token_root: str) -> None:
    """Test the `api_token` property of the APITokenAuthorizer class.

    Args:
        api_client: the test client for making API requests. Not used in this
            test but needed to create the database.
        random_api_token_root: a random API token for a root user.
    """
    authorizer = APITokenAuthorizer(api_token=random_api_token_root)
    assert authorizer.api_token is not None
    assert authorizer.api_token.token == random_api_token_root


def test_token_property_wrong_token(
        api_client: TestClient,  # pylint: disable=unused-argument
) -> None:
    """Test the `api_token` property of the APITokenAuthorizer class.

    Args:
        api_client: the test client for making API requests. Not used in this
            test but needed to create the database.
    """
    authorizer = APITokenAuthorizer(api_token='wrong_token')
    assert authorizer.api_token is None


def test_role_property_root(
        api_client: TestClient,  # pylint: disable=unused-argument
        random_api_token_root: str) -> None:
    """Test the roles property of the APITokenAuthorizer class.

    For root users.

    Args:
        api_client: the test client for making API requests. Not used in this
            test but needed to create the database.
        random_api_token_root: a random API token for a root user.
    """
    authorizer = APITokenAuthorizer(api_token=random_api_token_root)
    assert authorizer.is_root
    assert not authorizer.is_normal_user
    assert not authorizer.is_service_user


def test_role_property_wrong_token(
        api_client: TestClient,  # pylint: disable=unused-argument
) -> None:
    """Test the roles property of the APITokenAuthorizer class.

    For wrong tokens.

    Args:
        api_client: the test client for making API requests. Not used in this
            test but needed to create the database.
    """
    authorizer = APITokenAuthorizer(api_token='wrong_token')
    assert not authorizer.is_root
    assert not authorizer.is_normal_user
    assert not authorizer.is_service_user


def test_role_property_normal_user(
        api_client: TestClient,  # pylint: disable=unused-argument
        random_api_token_normal_user: str) -> None:
    """Test the roles property of the APITokenAuthorizer class.

    For normal user.

    Args:
        api_client: the test client for making API requests. Not used in this
            test but needed to create the database.
        random_api_token_normal_user: a random API token for a normal user.
    """
    authorizer = APITokenAuthorizer(
        api_token=random_api_token_normal_user)
    assert not authorizer.is_root
    assert authorizer.is_normal_user
    assert not authorizer.is_service_user


def test_user_property_without_api_token(
        api_client: TestClient,  # pylint: disable=unused-argument
) -> None:
    """Test the `user` property of the APITokenAuthorizer class.

    Args:
        api_client: the test client for making API requests. Not used in this
            test but needed to create the database.
    """
    authorizer = APITokenAuthorizer()
    assert authorizer.user is None


def test_api_token_property_without_api_token(
        api_client: TestClient,  # pylint: disable=unused-argument
) -> None:
    """Test the `api_token` property of the APITokenAuthorizer class.

    Args:
        api_client: the test client for making API requests. Not used in this
            test but needed to create the database.
    """
    authorizer = APITokenAuthorizer()
    assert authorizer.api_token is None


def test_api_is_valid_user_property_without_api_token(
        api_client: TestClient,  # pylint: disable=unused-argument
) -> None:
    """Test the `is_valid_user` property of the APITokenAuthorizer class.

    Args:
        api_client: the test client for making API requests. Not used in this
            test but needed to create the database.
    """
    authorizer = APITokenAuthorizer()
    assert not authorizer.is_valid_user


def test_api_is_valid_user_property(
        api_client: TestClient,  # pylint: disable=unused-argument
        random_api_token_root: str) -> None:
    """Test the `is_valid_user` property of the APITokenAuthorizer class.

    Args:
        api_client: the test client for making API requests. Not used in this
            test but needed to create the database.
        random_api_token_root: a random API token for a root user.
    """
    authorizer = APITokenAuthorizer(random_api_token_root)
    assert authorizer.is_valid_user


def test_api_is_long_lived_token_property(
        api_client: TestClient,  # pylint: disable=unused-argument
        random_api_token_normal_user_long_lived: str) -> None:
    """Test the `is_long_lived_token` property.

    Test with long lived tokens.

    Args:
        api_client: the test client for making API requests. Not used in this
            test but needed to create the database.
        random_api_token_normal_user_long_lived: a random API token for a root
            user.
    """
    authorizer = APITokenAuthorizer(
        api_token=random_api_token_normal_user_long_lived)
    assert authorizer.is_long_lived_token
    assert not authorizer.is_short_lived_token


def test_api_is_short_lived_token_property(
        api_client: TestClient,  # pylint: disable=unused-argument
        random_api_token_root: str) -> None:
    """Test the `is_long_lived_token` property.

    Test with short lived tokens.

    Args:
        api_client: the test client for making API requests. Not used in this
            test but needed to create the database.
        random_api_token_root: a random API token for a root user.
    """
    authorizer = APITokenAuthorizer(api_token=random_api_token_root)
    assert authorizer.is_short_lived_token
    assert not authorizer.is_long_lived_token


def test_api_is_short_lived_token_property_without_api_token(
        api_client: TestClient,  # pylint: disable=unused-argument
) -> None:
    """Test the `is_long_lived_token` property.

    Test without API token.

    Args:
        api_client: the test client for making API requests. Not used in this
            test but needed to create the database.
    """
    authorizer = APITokenAuthorizer()
    assert not authorizer.is_short_lived_token
    assert not authorizer.is_long_lived_token


def test_base_authorizer_class() -> None:
    """Test the base authorizer class.

    Test the basic functions of the Authorizer class. Because we cannot
    instantiate the abstract class, we instantiate the LoggedOffAuthorizer
    class and test it.
    """
    authorizer = LoggedOffAuthorizer(APITokenAuthorizer())
    with pytest.raises(APITokenAuthorizerAlreadySetException):
        authorizer.set_api_token_authorizer(APITokenAuthorizer())
