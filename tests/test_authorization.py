"""Tests for the APITokenAuthorizer class."""

from fastapi.testclient import TestClient
from my_rest_api.auth import APITokenAuthorizer


def test_user_property(
        api_client: TestClient,  # pylint: disable=unused-argument
        random_api_token_root: str) -> None:
    """Test the `user` property of the APITokenAuthorizer class.

    Args:
        api_client: the test client for making API requests. Not used in this
            test but needed to create the database.
        random_api_token_root: a random API token for a root user.
    """
    authorizator = APITokenAuthorizer(api_token=random_api_token_root)
    assert authorizator.user is not None
    assert authorizator.user.username == 'root'


def test_user_property_wrong_token(
        api_client: TestClient,  # pylint: disable=unused-argument
) -> None:
    """Test the `user` property of the APITokenAuthenticator class.

    Args:
        api_client: the test client for making API requests. Not used in this
            test but needed to create the database.
    """
    authorizator = APITokenAuthorizer(api_token='wrong_token')
    assert authorizator.user is None


def test_api_token_property(
        api_client: TestClient,  # pylint: disable=unused-argument
        random_api_token_root: str) -> None:
    """Test the `api_token` property of the APITokenAuthorizer class.

    Args:
        api_client: the test client for making API requests. Not used in this
            test but needed to create the database.
        random_api_token_root: a random API token for a root user.
    """
    authorizator = APITokenAuthorizer(api_token=random_api_token_root)
    assert authorizator.api_token is not None
    assert authorizator.api_token.token == random_api_token_root


def test_token_property_wrong_token(
        api_client: TestClient,  # pylint: disable=unused-argument
) -> None:
    """Test the `api_token` property of the APITokenAuthorizer class.

    Args:
        api_client: the test client for making API requests. Not used in this
            test but needed to create the database.
    """
    authorizator = APITokenAuthorizer(api_token='wrong_token')
    assert authorizator.api_token is None


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
    authorizator = APITokenAuthorizer(api_token=random_api_token_root)
    assert authorizator.is_root
    assert not authorizator.is_normal_user
    assert not authorizator.is_service_user


def test_role_property_wrong_token(
        api_client: TestClient,  # pylint: disable=unused-argument
) -> None:
    """Test the roles property of the APITokenAuthorizer class.

    For wrong tokens.

    Args:
        api_client: the test client for making API requests. Not used in this
            test but needed to create the database.
    """
    authorizator = APITokenAuthorizer(api_token='wrong_token')
    assert not authorizator.is_root
    assert not authorizator.is_normal_user
    assert not authorizator.is_service_user


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
    authorizator = APITokenAuthorizer(
        api_token=random_api_token_normal_user)
    assert not authorizator.is_root
    assert authorizator.is_normal_user
    assert not authorizator.is_service_user


def test_user_property_without_api_token(
        api_client: TestClient,  # pylint: disable=unused-argument
) -> None:
    """Test the `user` property of the APITokenAuthorizer class.

    Args:
        api_client: the test client for making API requests. Not used in this
            test but needed to create the database.
    """
    authorizator = APITokenAuthorizer()
    assert authorizator.user is None


def test_api_token_property_without_api_token(
        api_client: TestClient,  # pylint: disable=unused-argument
) -> None:
    """Test the `api_token` property of the APITokenAuthorizer class.

    Args:
        api_client: the test client for making API requests. Not used in this
            test but needed to create the database.
    """
    authorizator = APITokenAuthorizer()
    assert authorizator.api_token is None


def test_api_is_valid_user_property_without_api_token(
        api_client: TestClient,  # pylint: disable=unused-argument
) -> None:
    """Test the `is_valid_user` property of the APITokenAuthorizer class.

    Args:
        api_client: the test client for making API requests. Not used in this
            test but needed to create the database.
    """
    authorizator = APITokenAuthorizer()
    assert not authorizator.is_valid_user


def test_api_is_valid_user_property(
        api_client: TestClient,  # pylint: disable=unused-argument
        random_api_token_root: str) -> None:
    """Test the `is_valid_user` property of the APITokenAuthorizer class.

    Args:
        api_client: the test client for making API requests. Not used in this
            test but needed to create the database.
        random_api_token_root: a random API token for a root user.
    """
    authorizator = APITokenAuthorizer(random_api_token_root)
    assert authorizator.is_valid_user


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
    authorizator = APITokenAuthorizer(
        api_token=random_api_token_normal_user_long_lived)
    assert authorizator.is_long_lived_token
    assert not authorizator.is_short_lived_token


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
    authorizator = APITokenAuthorizer(api_token=random_api_token_root)
    assert authorizator.is_short_lived_token
    assert not authorizator.is_long_lived_token


def test_api_is_short_lived_token_property_without_api_token(
        api_client: TestClient,  # pylint: disable=unused-argument
) -> None:
    """Test the `is_long_lived_token` property.

    Test without API token.

    Args:
        api_client: the test client for making API requests. Not used in this
            test but needed to create the database.
    """
    authorizator = APITokenAuthorizer()
    assert not authorizator.is_short_lived_token
    assert not authorizator.is_long_lived_token
