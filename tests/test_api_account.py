"""Tests for adding resources using the REST API."""

import pytest
from fastapi.testclient import TestClient


@pytest.mark.parametrize(
    'token, password',
    [
        ('MHxHL4HrmmJHbAR1b0gV4OkpuEsxxmRL', 'root_pw'),
        ('Cbxfv44aNlWRMu4bVqawWu9vofhFWmED', 'root_pw'),
        ('pabq1d533eMucNPr5pHPuDMqxKRw1SE0', 'normal_user'),
    ],
)
def test_retrieving_password_reset_token_valid_token(
    api_client: TestClient, token: str, password: str
) -> None:
    """Test retrieving a password reset token with a valid token.

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
def test_retrieving_password_reset_token_invalid_token(
    api_client: TestClient, token: str
) -> None:
    """Test retrieving a password reset token with a invalid token.

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
