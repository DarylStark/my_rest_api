"""Test the authentication of the REST API."""

import pytest
from fastapi.testclient import TestClient
from pyotp import TOTP


def test_login_with_a_valid_api_token_set(
    api_client: TestClient, random_api_token_normal_user: str
) -> None:
    """Test logging in with a API token set.

    Should result in a error response.

    Args:
        api_client: the test client for making API requests.
        random_api_token_normal_user: a token for the request.
    """
    result = api_client.post(
        '/auth/login',
        json={'username': 'normal.user.1', 'password': 'normal_user_1_pw'},
        headers={'X-API-Token': random_api_token_normal_user},
    )
    response = result.json()
    assert response['error'] == 'Not authorized'
    assert result.status_code == 401


def test_login_with_invalid_api_token_set(api_client: TestClient) -> None:
    """Test logging in with a invalid API token set.

    Should not result in a error response.

    Args:
        api_client: the test client for making API requests.
    """
    result = api_client.post(
        '/auth/login',
        json={'username': 'normal.user.1', 'password': 'normal_user_1_pw'},
        headers={'X-API-Token': 'wrong_token'},
    )
    response = result.json()
    assert response['status'] == 'success'
    assert response['api_token'] is not None
    assert result.status_code == 200


@pytest.mark.parametrize(
    'login_json',
    [
        {'username': 'normal.user.1', 'password': 'normal_user_1_pw'},
        {'username': 'root', 'password': 'root_pw'},
    ],
    ids=['normal.user.1', 'root'],
)
def test_login_with_correct_credentials_no_2fa(
    api_client: TestClient, login_json: dict[str, str]
) -> None:
    """Test logging in with correct credentials and no 2FA.

    Should be succesfull and returning a API token.

    Args:
        api_client: the test client for making API requests.
        login_json: the dict to send to test.
    """
    result = api_client.post('/auth/login', json=login_json)
    assert result.status_code == 200


@pytest.mark.parametrize(
    'login_json',
    [{'username': 'normal.user.2', 'password': 'wrong_pw'}],
    ids=['normal.user.2'],
)
def test_login_with_correct_credentials_needed_2fa(
    api_client: TestClient, login_json: dict[str, str]
) -> None:
    """Test logging in with correct credentials for a account that needs 2FA.

    Should result in a error response.

    Args:
        api_client: the test client for making API requests.
        login_json: the dict to send to test.
    """
    result = api_client.post('/auth/login', json=login_json)
    response = result.json()
    assert response == {'status': 'failure', 'api_token': None}
    assert result.status_code == 403


def test_login_with_correct_credentials_and_2fa(
    api_client: TestClient, random_second_factor: str
) -> None:
    """Test logging in with correct credentials and 2FA.

    Should be succesfull and returning a API token.

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
            'second_factor': TOTP(random_second_factor).now(),
        },
    )
    response = result.json()
    assert response['status'] == 'success'
    assert response['api_token'] is not None
    assert result.status_code == 200


@pytest.mark.parametrize(
    'login_json',
    [
        {'username': 'normal.user.3', 'password': 'normal_user_3_pw'},
        {'username': 'normal.user.4', 'password': 'normal_user_4_pw'},
        {'username': 'normal.user.5', 'password': 'normal_user_5_pw'},
        {'username': 'normal.user.6', 'password': 'normal_user_6_pw'},
        {'username': 'normal.user.7', 'password': 'normal_user_7_pw'},
    ],
    ids=[
        'normal_user_3',
        'normal_user_4',
        'normal_user_5',
        'normal_user 6',
        'normal_user_7',
    ],
)
def test_login_with_incorrect_username(
    api_client: TestClient, login_json: dict[str, str]
) -> None:
    """Test logging in with incorrect username.

    Should give an Access Denied error.

    Args:
        api_client: the test client for making API requests.
        login_json: the dict to send to test.
    """
    result = api_client.post('/auth/login', json=login_json)
    response = result.json()
    assert response == {'status': 'failure', 'api_token': None}
    assert result.status_code == 403


@pytest.mark.parametrize(
    'login_json',
    [
        {'username': 'normal.user.1', 'password': 'wrong_pw'},
        {'username': 'normal.user.2', 'password': 'wrong_pw'},
        {'username': 'root', 'password': 'wrong_root_pw'},
    ],
    ids=['normal.user.1', 'normal.user.2', 'root'],
)
def test_login_with_incorrect_password(
    api_client: TestClient, login_json: dict[str, str]
) -> None:
    """Test logging in with incorrect password.

    Should give an Access Denied error.

    Args:
        api_client: the test client for making API requests.
        login_json: the dict to send to test.
    """
    result = api_client.post('/auth/login', json=login_json)
    response = result.json()
    assert response == {'status': 'failure', 'api_token': None}
    assert result.status_code == 403


def test_login_with_incorrect_2fa_format(api_client: TestClient) -> None:
    """Test logging in with a 2FA code when not needed.

    Should give an Access Denied error.

    Args:
        api_client: the test client for making API requests.
    """
    result = api_client.post(
        '/auth/login',
        json={
            'username': 'normal.user.1',
            'password': 'normal_user_1_pw',
            'second_factor': '123456',
        },
    )
    response = result.json()
    assert response == {'status': 'failure', 'api_token': None}
    assert result.status_code == 403


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
            'second_factor': '345123',
        },
    )
    response = result.json()
    assert response == {'status': 'failure', 'api_token': None}
    assert result.status_code == 403


def test_login_with_service_account(api_client: TestClient) -> None:
    """Test logging in with service account.

    Should fail since it is not allowed to interactively login with a service
    account.

    Args:
        api_client: the test client for making API requests.
    """
    result = api_client.post(
        '/auth/login',
        json={'username': 'service.user', 'password': 'service_password'},
    )
    response = result.json()
    assert response == {'status': 'failure', 'api_token': None}
    assert result.status_code == 403


def test_logout_with_valid_token(
    api_client: TestClient, random_api_token_normal_user_logout: str
) -> None:
    """Test logging out with a valid token.

    Should be succesfull.

    Args:
        api_client: the test client for making API requests.
        random_api_token_normal_user_logout: a token for the logout.
    """
    result = api_client.get(
        '/auth/logout',
        headers={'X-API-Token': random_api_token_normal_user_logout},
    )
    response = result.json()
    assert response['status'] == 'success'
    assert result.status_code == 200


def test_logout_with_long_lived_token(
    api_client: TestClient, random_api_token_normal_user_long_lived: str
) -> None:
    """Test logging out with a valid long-lived token.

    Should not be succesfull. A long-lived token cannot be logged out. These
    tokens shuold be deleted by the user.

    Args:
        api_client: the test client for making API requests.
        random_api_token_normal_user_long_lived: a token for the logout.
    """
    result = api_client.get(
        '/auth/logout',
        headers={'X-API-Token': random_api_token_normal_user_long_lived},
    )
    response = result.json()
    assert response['error'] == 'Not authorized'
    assert result.status_code == 401


def test_logout_with_invalid_token(api_client: TestClient) -> None:
    """Test logging out with a invalid token.

    Should fail.

    Args:
        api_client: the test client for making API requests.
    """
    result = api_client.get(
        '/auth/logout', headers={'X-API-Token': 'wrong_token'}
    )
    response = result.json()
    assert response['error'] == 'Not authorized'
    assert result.status_code == 401


def test_authentication_status_not_logged_in(api_client: TestClient) -> None:
    """Test the authentication status when not logged in.

    Should result in a 200 page indicating that nobody is logged in.

    Args:
        api_client: the test client for making API requests.
    """
    result = api_client.get('/auth/status')
    response = result.json()
    assert response['error'] == 'Not authorized'
    assert result.status_code == 401


def test_authentication_status_valid_short_lived_token(
    api_client: TestClient, random_api_token_normal_user: str
) -> None:
    """Test the authentication status with a valid token.

    Should be succesfull.

    Args:
        api_client: the test client for making API requests.
        random_api_token_normal_user: a token for the request.
    """
    result = api_client.get(
        '/auth/status', headers={'X-API-Token': random_api_token_normal_user}
    )
    response = result.json()
    assert response['token_type'] == 'short-lived'
    assert response['title'] == 'test short lived api token'
    assert response['created'] is not None
    assert response['expires'] is not None
    assert result.status_code == 200


def test_authentication_status_valid_long_lived_token(
    api_client: TestClient, random_api_token_normal_user_long_lived: str
) -> None:
    """Test the authentication status with a valid token.

    Should be succesfull.

    Args:
        api_client: the test client for making API requests.
        random_api_token_normal_user_long_lived: a token for the request.
    """
    result = api_client.get(
        '/auth/status',
        headers={'X-API-Token': random_api_token_normal_user_long_lived},
    )
    response = result.json()
    assert response['token_type'] == 'long-lived'
    assert response['title'] == 'test token'
    assert response['created'] is not None
    assert response['expires'] is not None
    assert result.status_code == 200


def test_authentication_status_invalid_token(api_client: TestClient) -> None:
    """Test the authentication status with a invalid token.

    Should result in a 401 error.

    Args:
        api_client: the test client for making API requests.
    """
    result = api_client.get(
        '/auth/status', headers={'X-API-Token': 'wrong_token'}
    )
    response = result.json()
    assert response['error'] == 'Not authorized'
    assert result.status_code == 401
