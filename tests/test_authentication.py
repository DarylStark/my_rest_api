"""Test the authentication of the REST API."""


import pytest
from fastapi.testclient import TestClient


@pytest.mark.parametrize('login_json', [
    {'username': 'service.user.1', 'password': 'normal_user_1_pw'},
    {'username': 'root', 'password': 'root_pw'}
])
def test_login_with_correct_credentials_no_2fa(
        api_client: TestClient,
        login_json: dict[str, str]) -> None:
    """Test logging in with correct credentials and no 2FA.

    Should be succesfull and returning a API key.

    Args:
        api_client: the test client for making API requests.
        login_json: a 
    """
    result = api_client.post(
        '/auth/login',
        json=login_json)
    assert result.status_code == 200


def test_login_with_correct_credentials_needed_2fa(api_client: TestClient) -> None:
    """Test logging in with correct credentials for a account that needs 2FA.

    Should result in a response that indicates that 2FA is needed.

    Args:
        api_client: the test client for making API requests.
    """
    result = api_client.post('/auth/login')
    assert result.status_code == 200


def test_login_with_correct_credentials_and_2fa(api_client: TestClient) -> None:
    """Test logging in with correct credentials and 2FA.

    Should be succesfull and returning a API key.

    Args:
        api_client: the test client for making API requests.
    """
    result = api_client.post('/auth/login')
    assert result.status_code == 200


def test_login_with_incorrect_username(api_client: TestClient) -> None:
    """Test logging in with incorrect username.

    Should give an Access Denied error.

    Args:
        api_client: the test client for making API requests.
    """
    result = api_client.post('/auth/login')
    assert result.status_code == 200


def test_login_with_incorrect_password(api_client: TestClient) -> None:
    """Test logging in with incorrect password.

    Should give an Access Denied error.

    Args:
        api_client: the test client for making API requests.
    """
    result = api_client.post('/auth/login')
    assert result.status_code == 200


def test_login_with_incorrect_2fa(api_client: TestClient) -> None:
    """Test logging in with incorrect 2FA.

    Should give an Access Denied error.

    Args:
        api_client: the test client for making API requests.
    """
    result = api_client.post('/auth/login')
    assert result.status_code == 200


def test_login_with_service_account(api_client: TestClient) -> None:
    """Test logging in with service account.

    Should fail since it is not allowed to interactively login with a service
    account.

    Args:
        api_client: the test client for making API requests.
    """
    result = api_client.post('/auth/login')
    assert result.status_code == 200
