"""Test the authentication of the REST API."""

import pytest
from fastapi.testclient import TestClient
from pyotp import TOTP


def test_login_with_a_valid_api_token_set(api_client: TestClient) -> None:
    """Test logging in with a API token set.

    Should result in a error response.

    Args:
        api_client: the test client for making API requests.
    """
    result = api_client.post(
        '/auth/login',
        json={'username': 'normal.user.1', 'password': 'normal_user_1_pw'},
        headers={'X-API-Token': 'pabq1d533eMucNPr5pHPuDMqxKRw1SE0'},
    )
    assert result.status_code == 401


def test_login_with_invalid_api_token_set(api_client: TestClient) -> None:
    """Test logging in with a invalid API token set.

    Should not result in a error response.

    Args:
        api_client: the test client for making API requests.
    """
    result = api_client.post(
        '/auth/login',
        json={'username': 'normal.user', 'password': 'normal_user'},
        headers={'X-API-Token': 'wrong_token'},
    )
    response = result.json()
    assert response['status'] == 'success'
    assert response['api_token'] is not None
    assert result.status_code == 200


@pytest.mark.parametrize(
    'login_json',
    [
        {'username': 'normal.user', 'password': 'normal_user'},
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

    # Logout again
    result = api_client.get(
        '/auth/logout',
        headers={'X-API-Token': result.json()['api_token']},
    )


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
    result.json()
    assert result.status_code == 403


def test_login_with_correct_credentials_and_2fa(
    api_client: TestClient,
) -> None:
    """Test logging in with correct credentials and 2FA.

    Should be succesfull and returning a API token.

    Args:
        api_client: the test client for making API requests.
    """
    random_second_factor = 'UHAO7AS4BFQV5Y4FHPN5QGV6GADEVHPX'
    result = api_client.post('/auth/login')
    result = api_client.post(
        '/auth/login',
        json={
            'username': 'normal.user.2fa',
            'password': 'normal_user',
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
    result.json()
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
    result.json()
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
    result.json()
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
    result.json()
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
    result.json()
    assert result.status_code == 403


def test_logout_with_valid_token(api_client: TestClient) -> None:
    """Test logging out with a valid token.

    Should be succesfull.

    Args:
        api_client: the test client for making API requests.
    """
    result = api_client.get(
        '/auth/logout',
        headers={'X-API-Token': '0jQW6vv732Flb4j56e92eja0npqyFsPQ'},
    )
    response = result.json()
    assert response['status'] == 'success'
    assert result.status_code == 200


def test_logout_with_long_lived_token(api_client: TestClient) -> None:
    """Test logging out with a valid long-lived token.

    Should not be succesfull. A long-lived token cannot be logged out. These
    tokens shuold be deleted by the user.

    Args:
        api_client: the test client for making API requests.
    """
    result = api_client.get(
        '/auth/logout',
        headers={'X-API-Token': 'MHxHL4HrmmJHbAR1b0gV4OkpuEsxxmRL'},
    )
    result.json()
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
    result.json()
    assert result.status_code == 401


def test_authentication_status_not_logged_in(api_client: TestClient) -> None:
    """Test the authentication status when not logged in.

    Should result in a 200 page indicating that nobody is logged in.

    Args:
        api_client: the test client for making API requests.
    """
    result = api_client.get('/auth/status')
    result.json()
    assert result.status_code == 401


def test_authentication_status_valid_short_lived_token(
    api_client: TestClient,
) -> None:
    """Test the authentication status with a valid token.

    Should be succesfull.

    Args:
        api_client: the test client for making API requests.
    """
    result = api_client.get(
        '/auth/status',
        headers={'X-API-Token': 'pabq1d533eMucNPr5pHPuDMqxKRw1SE0'},
    )
    response = result.json()
    assert response['token_type'] == 'short-lived'
    assert response['title'] == 'normal_user_short_lived_token'
    assert response['created'] is not None
    assert response['expires'] is not None
    assert result.status_code == 200


def test_authentication_status_valid_long_lived_token(
    api_client: TestClient,
) -> None:
    """Test the authentication status with a valid token.

    Should be succesfull.

    Args:
        api_client: the test client for making API requests.
    """
    result = api_client.get(
        '/auth/status',
        headers={'X-API-Token': '6VZGMOdNUAhCzYhipVJJjHTsYIzwBrlg'},
    )
    response = result.json()
    assert response['token_type'] == 'long-lived'
    assert response['title'] == 'normal_user_long_lived_token'
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
    result.json()
    assert result.status_code == 401


def test_refresh_short_lived_token(
    api_client: TestClient,
) -> None:
    """Test refreshing a short lived token.

    Should be succesfull.

    Args:
        api_client: the test client for making API requests.
    """
    api_token = 'SbtMQ81IHb5BdoOEk1cZPCaERCrf646z'
    result = api_client.get(
        '/auth/status',
        headers={'X-API-Token': api_token},
    )
    expiration_date = result.json()['expires']

    result = api_client.get(
        '/auth/refresh?renew_token=false',
        headers={'X-API-Token': api_token},
    )
    response = result.json()
    assert response['expires'] == expiration_date
    assert response['new_token'] is None
    assert result.status_code == 200

    # Now we set a new token
    result = api_client.get(
        '/auth/refresh?renew_token=true',
        headers={'X-API-Token': api_token},
    )
    response = result.json()
    assert response['expires'] == expiration_date
    assert response['new_token'] is not None
    assert result.status_code == 200
