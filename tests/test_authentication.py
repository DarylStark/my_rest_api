"""Test the authentication of the REST API."""

import pytest
from fastapi.testclient import TestClient
from pyotp import TOTP


@pytest.mark.parametrize('login_json', [
    {'username': 'normal.user.1', 'password': 'normal_user_1_pw'},
    {'username': 'root', 'password': 'root_pw'}],
    ids=['normal_user_1', 'root'])
def test_login_with_correct_credentials_no_2fa(
        api_client: TestClient,
        login_json: dict[str, str]) -> None:
    """Test logging in with correct credentials and no 2FA.

    Should be succesfull and returning a API key.

    Args:
        api_client: the test client for making API requests.
        login_json: the dict to send to test.
    """
    result = api_client.post(
        '/auth/login',
        json=login_json)
    assert result.status_code == 200


def test_login_with_correct_credentials_needed_2fa(
        api_client: TestClient) -> None:
    """Test logging in with correct credentials for a account that needs 2FA.

    Should result in a response that indicates that 2FA is needed.

    Args:
        api_client: the test client for making API requests.
    """
    result = api_client.post(
        '/auth/login',
        json={
            'username': 'normal.user.2',
            'password': 'normal_user_2_pw'
        })
    response = result.json()
    assert response == {
        'status': 'correct',
        'api_key': None
    }
    assert result.status_code == 412


def test_login_with_correct_credentials_and_2fa(
        api_client: TestClient,
        random_second_factor: str) -> None:
    """Test logging in with correct credentials and 2FA.

    Should be succesfull and returning a API key.

    Args:
        api_client: the test client for making API requests.
        random_second_factor: a random second factor.
    """
    result = api_client.post('/auth/login')
    result = api_client.post(
        '/auth/login',
        json={
            'username': 'normal.user.2',
            'password': 'normal_user_2_pw',
            'second_factor': TOTP(random_second_factor).now()
        })
    response = result.json()
    assert response['status'] == 'correct'
    assert response['api_key'] is not None
    assert result.status_code == 200


@pytest.mark.parametrize('login_json', [
    {'username': 'normal.user.3', 'password': 'normal_user_3_pw'},
    {'username': 'normal.user.4', 'password': 'normal_user_4_pw'},
    {'username': 'normal.user.5', 'password': 'normal_user_5_pw'},
    {'username': 'normal.user.6', 'password': 'normal_user_6_pw'},
    {'username': 'normal.user.7', 'password': 'normal_user_7_pw'}],
    ids=['normal_user_3', 'normal_user_4', 'normal_user_5',
         'normal_user 6', 'normal_user_7'])
def test_login_with_incorrect_username(
        api_client: TestClient, login_json: dict[str, str]) -> None:
    """Test logging in with incorrect username.

    Should give an Access Denied error.

    Args:
        api_client: the test client for making API requests.
        login_json: the dict to send to test.
    """
    result = api_client.post(
        '/auth/login',
        json=login_json)
    response = result.json()
    assert response == {
        'status': 'incorrect',
        'api_key': None
    }
    assert result.status_code == 401


@pytest.mark.parametrize('login_json', [
    {'username': 'normal.user.1', 'password': 'wrong_pw'},
    {'username': 'root', 'password': 'wrong_root_pw'}],
    ids=['normal_user_1', 'root'])
def test_login_with_incorrect_password(
        api_client: TestClient, login_json: dict[str, str]) -> None:
    """Test logging in with incorrect password.

    Should give an Access Denied error.

    Args:
        api_client: the test client for making API requests.
        login_json: the dict to send to test.
    """
    result = api_client.post(
        '/auth/login',
        json=login_json)
    response = result.json()
    assert response == {
        'status': 'incorrect',
        'api_key': None
    }
    assert result.status_code == 401


def test_login_with_incorrect_2fa(api_client: TestClient) -> None:
    """Test logging in with incorrect 2FA.

    Should give an Access Denied error.

    Args:
        api_client: the test client for making API requests.
    """
    result = api_client.post('/auth/login')
    result = api_client.post(
        '/auth/login',
        json={
            'username': 'normal.user.1',
            'password': 'normal_user_2_pw',
            'second_factor': '345123'
        })
    response = result.json()
    assert response == {
        'status': 'incorrect',
        'api_key': None
    }
    assert result.status_code == 401


def test_login_with_service_account(api_client: TestClient) -> None:
    """Test logging in with service account.

    Should fail since it is not allowed to interactively login with a service
    account.

    Args:
        api_client: the test client for making API requests.
    """
    result = api_client.post(
        '/auth/login',
        json={
            'username': 'service.user',
            'password': 'service_password'})
    response = result.json()
    assert response == {
        'status': 'incorrect',
        'api_key': None
    }
    assert result.status_code == 401
