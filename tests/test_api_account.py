"""Tests for adding resources using the REST API."""

import pytest
from fastapi.testclient import TestClient
from pyotp import TOTP


@pytest.mark.parametrize(
    'token, password',
    [
        ('MHxHL4HrmmJHbAR1b0gV4OkpuEsxxmRL', 'root_pw'),
        ('Cbxfv44aNlWRMu4bVqawWu9vofhFWmED', 'root_pw'),
        ('pabq1d533eMucNPr5pHPuDMqxKRw1SE0', 'normal_user'),
    ],
)
def test_password_reset_token_valid_token(
    api_client: TestClient, token: str, password: str
) -> None:
    """Test a password reset token request with a valid token.

    Happy path test; should be a success.

    Args:
        api_client: the test client for the REST API.
        token: the token to use for the test.
        password: the password for the testuser.
    """
    response = api_client.post(
        '/account/request_password_reset_token',
        headers={'X-API-Token': token},
        json={
            'password': password,
        },
    )
    result = response.json()
    assert response.status_code == 200
    assert result['token'] is not None


@pytest.mark.parametrize('token', ['6VZGMOdNUAhCzYhipVJJjHTsYIzwBrlg'])
def test_password_reset_token_invalid_token(
    api_client: TestClient, token: str
) -> None:
    """Test a password reset token request with a invalid auth token.

    Unhappy path test; should fail.

    Args:
        api_client: the test client for the REST API.
        token: the token to use for the test.
    """
    response = api_client.post(
        '/account/request_password_reset_token',
        headers={'X-API-Token': token},
        json={
            'password': 'password',
        },
    )
    assert response.status_code == 401


@pytest.mark.parametrize(
    'token, password',
    [
        ('MHxHL4HrmmJHbAR1b0gV4OkpuEsxxmRL', 'wrong_pw'),
        ('Cbxfv44aNlWRMu4bVqawWu9vofhFWmED', 'wrong_pw'),
        ('pabq1d533eMucNPr5pHPuDMqxKRw1SE0', 'wrong_pw'),
    ],
)
def test_password_reset_token_valid_token_invalid_password(
    api_client: TestClient, token: str, password: str
) -> None:
    """Test a password reset token request with a invalid password.

    Unhappy path test. Should fail.

    Args:
        api_client: the test client for the REST API.
        token: the token to use for the test.
        password: the password for the testuser.
    """
    response = api_client.post(
        '/account/request_password_reset_token',
        headers={'X-API-Token': token},
        json={
            'password': password,
        },
    )
    assert response.status_code == 401


@pytest.mark.parametrize(
    'token, password',
    [
        ('MHxHL4HrmmJHbAR1b0gV4OkpuEsxxmRL', 'root_pw'),
        ('Cbxfv44aNlWRMu4bVqawWu9vofhFWmED', 'root_pw'),
        ('pabq1d533eMucNPr5pHPuDMqxKRw1SE0', 'normal_user'),
    ],
)
def test_resetting_password(
    api_client: TestClient, token: str, password: str
) -> None:
    """Test resetting a password with valid data.

    Happy path test; should be a success.

    Args:
        api_client: the test client for the REST API.
        token: the aithorization token to use for the test.
        password: the password for the testuser.
    """
    # Retrieve the token
    response = api_client.post(
        '/account/request_password_reset_token',
        headers={'X-API-Token': token},
        json={
            'password': password,
        },
    )
    result = response.json()
    assert response.status_code == 200
    assert result['token'] is not None
    reset_token = result['token']

    # Set the new password
    response = api_client.post(
        '/account/password_reset',
        headers={'X-API-Token': token},
        json={'new_password': 'my_new_password', 'reset_token': reset_token},
    )
    assert response.status_code == 200

    # Set the old password again
    response = api_client.post(
        '/account/request_password_reset_token',
        headers={'X-API-Token': token},
        json={
            'password': 'my_new_password',
        },
    )
    result = response.json()
    reset_token = result['token']
    response = api_client.post(
        '/account/password_reset',
        headers={'X-API-Token': token},
        json={'new_password': password, 'reset_token': reset_token},
    )


@pytest.mark.parametrize(
    'token, password',
    [
        ('MHxHL4HrmmJHbAR1b0gV4OkpuEsxxmRL', 'root_pw'),
        ('Cbxfv44aNlWRMu4bVqawWu9vofhFWmED', 'root_pw'),
        ('pabq1d533eMucNPr5pHPuDMqxKRw1SE0', 'normal_user'),
    ],
)
def test_resetting_password_invalid_token(
    api_client: TestClient, token: str, password: str
) -> None:
    """Test resetting a password with a invalid token.

    Unhappy path test; should always fail.

    Args:
        api_client: the test client for the REST API.
        token: the aithorization token to use for the test.
        password: the password for the testuser.
    """
    # Set the new password
    response = api_client.post(
        '/account/password_reset',
        headers={'X-API-Token': token},
        json={'new_password': 'my_new_password', 'reset_token': 'wrong_token'},
    )
    assert response.status_code == 401


@pytest.mark.parametrize(
    'token, password',
    [
        ('MHxHL4HrmmJHbAR1b0gV4OkpuEsxxmRL', 'root_pw'),
        ('Cbxfv44aNlWRMu4bVqawWu9vofhFWmED', 'root_pw'),
        ('pabq1d533eMucNPr5pHPuDMqxKRw1SE0', 'normal_user'),
    ],
)
def test_second_factor_token_valid_token(
    api_client: TestClient, token: str, password: str
) -> None:
    """Test a requesting a token to change second factor settings.

    Happy path test; should be a success.

    Args:
        api_client: the test client for the REST API.
        token: the token to use for the test.
        password: the password for the testuser.
    """
    response = api_client.post(
        '/account/request_change_second_factor_token',
        headers={'X-API-Token': token},
        json={'password': password, 'new_status': True},
    )
    result = response.json()
    assert response.status_code == 200
    assert result['token'] is not None


@pytest.mark.parametrize('token', ['6VZGMOdNUAhCzYhipVJJjHTsYIzwBrlg'])
def test_psecond_factor_token_invalid_token(
    api_client: TestClient, token: str
) -> None:
    """Test a requesting a token to change 2FA setting with invalid auth token.

    Unhappy path test; should fail.

    Args:
        api_client: the test client for the REST API.
        token: the token to use for the test.
    """
    response = api_client.post(
        '/account/request_change_second_factor_token',
        headers={'X-API-Token': token},
        json={'password': 'password', 'new_status': True},
    )
    assert response.status_code == 401


@pytest.mark.parametrize(
    'token, password',
    [
        ('MHxHL4HrmmJHbAR1b0gV4OkpuEsxxmRL', 'wrong_pw'),
        ('Cbxfv44aNlWRMu4bVqawWu9vofhFWmED', 'wrong_pw'),
        ('pabq1d533eMucNPr5pHPuDMqxKRw1SE0', 'wrong_pw'),
    ],
)
def test_second_factor_valid_token_invalid_password(
    api_client: TestClient, token: str, password: str
) -> None:
    """Test a requesting a token to change 2FA setting with invalid password.

    Unhappy path test. Should fail.

    Args:
        api_client: the test client for the REST API.
        token: the token to use for the test.
        password: the password for the testuser.
    """
    response = api_client.post(
        '/account/request_change_second_factor_token',
        headers={'X-API-Token': token},
        json={'password': password, 'new_status': True},
    )
    assert response.status_code == 401


@pytest.mark.parametrize(
    'token, password',
    [
        ('MHxHL4HrmmJHbAR1b0gV4OkpuEsxxmRL', 'root_pw'),
        ('Cbxfv44aNlWRMu4bVqawWu9vofhFWmED', 'root_pw'),
        ('pabq1d533eMucNPr5pHPuDMqxKRw1SE0', 'normal_user'),
    ],
)
def test_second_factor_change(
    api_client: TestClient, token: str, password: str
) -> None:
    """Test setting a second factor setting.

    Happy path test; should be a success.

    Args:
        api_client: the test client for the REST API.
        token: the aithorization token to use for the test.
        password: the password for the testuser.
    """
    # Retrieve the token
    response = api_client.post(
        '/account/request_change_second_factor_token',
        headers={'X-API-Token': token},
        json={'password': password, 'new_status': True},
    )
    result = response.json()
    assert response.status_code == 200
    assert result['token'] is not None
    reset_token = result['token']

    # Set the new 2FA setting
    response = api_client.post(
        '/account/change_second_factor',
        headers={'X-API-Token': token},
        json={'new_status': True, 'reset_token': reset_token},
    )
    result = response.json()
    assert response.status_code == 200
    assert result['status'] == 'success'
    assert result['secret'] is not None
    second_factor_secret = result['secret']

    # Set the old 2FA setting again
    response = api_client.post(
        '/account/request_change_second_factor_token',
        headers={'X-API-Token': token},
        json={
            'password': password,
            'second_factor': TOTP(second_factor_secret).now(),
            'new_status': False,
        },
    )
    result = response.json()
    reset_token = result['token']
    response = api_client.post(
        '/account/change_second_factor',
        headers={'X-API-Token': token},
        json={'new_status': False, 'reset_token': reset_token},
    )


@pytest.mark.parametrize(
    'token, password',
    [
        ('MHxHL4HrmmJHbAR1b0gV4OkpuEsxxmRL', 'root_pw'),
        ('Cbxfv44aNlWRMu4bVqawWu9vofhFWmED', 'root_pw'),
        ('pabq1d533eMucNPr5pHPuDMqxKRw1SE0', 'normal_user'),
    ],
)
def test_second_factor_invalid_token(
    api_client: TestClient, token: str, password: str
) -> None:
    """Test setting a second factor setting with a invalid token.

    Unhappy path test; should always fail.

    Args:
        api_client: the test client for the REST API.
        token: the aithorization token to use for the test.
        password: the password for the testuser.
    """
    # Set the new password
    response = api_client.post(
        '/account/password_reset',
        headers={'X-API-Token': token},
        json={'new_password': 'my_new_password', 'reset_token': 'wrong_token'},
    )
    assert response.status_code == 401


def test_second_factor_change_invalid_type(api_client: TestClient) -> None:
    """Test setting a second factor setting with a invalid token type.

    Unhappy path test; should fail.

    Args:
        api_client: the test client for the REST API.
        token: the aithorization token to use for the test.
        password: the password for the testuser.
    """
    token = 'MHxHL4HrmmJHbAR1b0gV4OkpuEsxxmRL'
    password = 'root_pw'

    # Retrieve the token
    response = api_client.post(
        '/account/request_change_second_factor_token',
        headers={'X-API-Token': token},
        json={'password': password, 'new_status': True},
    )
    result = response.json()
    assert response.status_code == 200
    assert result['token'] is not None
    reset_token = result['token']

    # Set the new 2FA setting
    response = api_client.post(
        '/account/change_second_factor',
        headers={'X-API-Token': token},
        json={'new_status': False, 'reset_token': reset_token},
    )
    result = response.json()
    assert response.status_code == 401


@pytest.mark.parametrize(
    'token, password',
    [
        ('MHxHL4HrmmJHbAR1b0gV4OkpuEsxxmRL', 'root_pw'),
        ('Cbxfv44aNlWRMu4bVqawWu9vofhFWmED', 'root_pw'),
        ('pabq1d533eMucNPr5pHPuDMqxKRw1SE0', 'normal_user'),
    ],
)
def test_second_factor_change_already_set(
    api_client: TestClient, token: str, password: str
) -> None:
    """Test setting a second factor setting when it is already set correctly.

    Unhappy path test; should fail.

    Args:
        api_client: the test client for the REST API.
        token: the aithorization token to use for the test.
        password: the password for the testuser.
    """
    # Retrieve the token
    response = api_client.post(
        '/account/request_change_second_factor_token',
        headers={'X-API-Token': token},
        json={'password': password, 'new_status': False},
    )
    assert response.status_code == 401
