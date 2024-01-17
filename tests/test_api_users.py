"""Test the user management of the REST API."""

from fastapi.testclient import TestClient


def test_retrieve_users_as_root(
        api_client: TestClient,
        random_api_token_root: str) -> None:
    """Test the authentication status with a valid token.

    Should be succesfull.

    Args:
        api_client: the test client for making API requests.
        random_api_token_root: a token for the request.
    """
    result = api_client.get(
        '/users/users',
        headers={'X-API-Token': random_api_token_root})
    response = result.json()
    assert result.status_code == 200
    assert len(response) == 4


def test_retrieve_users_as_normal_user(
        api_client: TestClient,
        random_api_token_normal_user: str) -> None:
    """Test the authentication status with a valid token.

    Should be succesfull.

    Args:
        api_client: the test client for making API requests.
        random_api_token_normal_user: a token for the request.
    """
    result = api_client.get(
        '/users/users',
        headers={'X-API-Token': random_api_token_normal_user})
    response = result.json()
    assert result.status_code == 200
    assert len(response) == 1
    assert response[0]['username'] == 'normal.user.1'
