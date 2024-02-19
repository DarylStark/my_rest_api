"""Test the user management of the REST API."""
# pylint: disable=too-many-arguments

import pytest
from fastapi.testclient import TestClient


def test_retrieve_users_as_root(
        api_client: TestClient,
        random_api_token_root: str) -> None:
    """Test retrieving users as root.

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
    """Test retrieving users as a normal user.

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


def test_retrieve_users_as_normal_user_with_long_lived_token(
        api_client: TestClient) -> None:
    """Test retrieving users as a normal user with a long lived token.

    Should be succesfull.

    Args:
        api_client: the test client for making API requests.
    """
    result = api_client.get(
        '/users/users',
        headers={'X-API-Token': '2e3n4RSr4I6TnRSwXRpjDYhs9XIYNwhv'})
    response = result.json()
    assert result.status_code == 200
    assert len(response) == 1
    assert response[0]['username'] == 'normal.user.2'


def test_retrieve_users_as_normal_user_with_long_lived_token_missing_scope(
        api_client: TestClient) -> None:
    """Test retrieving users as a normal user token without the correct scope.

    Should fail since the token is not given the correct scope.

    Args:
        api_client: the test client for making API requests.
    """
    result = api_client.get(
        '/users/users',
        headers={'X-API-Token': 'BynORM5FVkt07BuQSA09lQUIrgCgOqEv'})
    assert result.status_code == 401


@pytest.mark.parametrize('field_name, operator, value, expected_length', [
    ('id', None, 1, 1),
    ('id', 'ne', 1, 3),
    ('id', 'lt', 4, 3),
    ('id', 'gt', 1, 3),
    ('id', 'le', 3, 3),
    ('id', 'ge', 2, 3),
    ('username', None, 'root', 1),
    ('username', 'contains', 'normal', 2),
    ('username', 'notcontains', 'service', 3),
    ('fullname', None, 'root', 1),
    ('fullname', 'contains', 'normal', 2),
    ('fullname', 'notcontains', 'service', 3),
    ('email', None, 'normal_user_1@example.com', 1),
    ('email', 'contains', 'normal_user', 2),
    ('email', 'notcontains', 'service', 3),
])
def test_retrieve_users_with_filters_as_root(
        api_client: TestClient,
        random_api_token_root: str,
        field_name: str,
        operator: str | None,
        value: str,
        expected_length: int) -> None:
    """Test retrieving users with filters.

    Should be succesfull.

    Args:
        api_client: the test client for making API requests.
        random_api_token_root: a token for the request.
        field_name: the field name to filter on.
        operator: the operator to use for the filter.
        value: the value to filter on.
        expected_length: the expected length of the result.
    """
    filter_argument = field_name
    if operator:
        filter_argument += f'-{operator}'
    filter_argument += f'={value}'
    result = api_client.get(
        f'/users/users?{filter_argument}',
        headers={'X-API-Token': random_api_token_root})
    response = result.json()
    assert result.status_code == 200
    assert len(response) == expected_length
