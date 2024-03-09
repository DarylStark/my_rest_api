"""Tests for deleting resources using the REST API."""

from typing import Any

import pytest
from fastapi.testclient import TestClient


@pytest.mark.parametrize(
    'endpoint, object',
    (
        (
            'users',
            {
                'fullname': 'test user to delete',
                'username': 'test_user_to_delete',
                'email': 'test_user_to_delete@example.com',
                'role': 3,
            },
        ),
        (
            'tags',
            {
                'title': 'test_tag_1_updated',
            },
        ),
        (
            'tags',
            {
                'title': 'test_tag_2_updated',
                'color': '0000ff',
            },
        ),
        (
            'user_settings',
            {
                'setting': 'test_setting_1_udated',
                'value': 'yes_updated',
            },
        ),
        (
            'api_clients',
            {
                'app_name': 'test_app_1_updated',
                'app_publisher': 'test_app_publisher_1_updated',
            },
        ),
    ),
)
def test_delete_short_lived_root(
    api_client: TestClient, endpoint: str, object: dict[str, Any]
) -> None:
    """Test that the delete endpoints work with a short lived token.

    Happy path test; should always be a success and return some data. We test
    deleting data for all paths that should enable the user to update data. We
    check the return value; if it contains the deleted ID, we assume the
    object is deleted.

    Args:
        api_client: the test client.
        endpoint: the endpoint to test.
        object: the objects to create.
    """
    _token = 'Cbxfv44aNlWRMu4bVqawWu9vofhFWmED'

    # Create the resource
    result = api_client.post(
        f'/resources/{endpoint}',
        headers={'X-API-Token': _token},
        json=[object],
    )
    id = result.json()[0]['id']

    # Do the request
    result = api_client.delete(
        f'/resources/{endpoint}/{id}', headers={'X-API-Token': _token}
    )
    response = result.json()

    # Validate the answer
    assert result.status_code == 200
    assert id in response['deleted']


@pytest.mark.parametrize(
    'endpoint, id',
    (
        ('users', 1),
        ('users', 3),
        ('users', 4),
        ('tags', 1),
        ('tags', 2),
        ('tags', 3),
        ('user_settings', 1),
        ('user_settings', 2),
        ('user_settings', 3),
        ('api_clients', 1),
        ('api_tokens', 1),
        ('api_tokens', 2),
    ),
)
def test_delete_short_lived_normal_user_not_owned(
    api_client: TestClient, endpoint: str, id: int
) -> None:
    """Test that the delete endpoints work with a short lived token.

    Tests with a normal user to delete a resource that it doesn't own. Should
    always fail with a 404.

    Args:
        api_client: the test client.
        endpoint: the endpoint to test.
        id: the id of the object to delete.
    """
    _token = 'pabq1d533eMucNPr5pHPuDMqxKRw1SE0'

    # Do the request
    result = api_client.delete(
        f'/resources/{endpoint}/{id}',
        headers={'X-API-Token': _token},
    )

    # Validate the answer
    assert result.status_code == 404


@pytest.mark.parametrize(
    'endpoint, object',
    (
        (
            'users',
            {
                'fullname': 'test user 1 updated',
                'username': 'test_user_1_updated',
                'email': 'test_user_1_updated@example.com',
                'role': 3,
            },
        ),
        (
            'tags',
            {
                'title': 'test_tag_1_updated',
            },
        ),
        (
            'user_settings',
            {
                'setting': 'test_setting_1_udated',
                'value': 'yes_updated',
            },
        ),
    ),
)
def test_delete_long_lived_root(
    api_client: TestClient, endpoint: str, object: dict[str, Any]
) -> None:
    """Test that the update endpoints work with a long lived token.

    Happy path test; should always be a success and return some data. We test
    updating data for all paths that should enable the user to update data with
    a long lived token.

    We test this with the root user, meaning we can create data for all
    types of resources.

    Args:
        api_client: the test client.
        endpoint: the endpoint to test.
        object: the objects to create.
    """
    _token = 'MHxHL4HrmmJHbAR1b0gV4OkpuEsxxmRL'

    # Create the resource
    result = api_client.post(
        f'/resources/{endpoint}',
        headers={'X-API-Token': _token},
        json=[object],
    )
    id = result.json()[0]['id']

    # Do the request
    result = api_client.delete(
        f'/resources/{endpoint}/{id}', headers={'X-API-Token': _token}
    )
    response = result.json()

    # Validate the answer
    assert result.status_code == 200
    assert id in response['deleted']


@pytest.mark.parametrize(
    'endpoint, id',
    (
        ('api_clients', 1),
        ('api_clients', 2),
    ),
)
def test_delete_long_lived_invalid_enpoint(
    api_client: TestClient, endpoint: str, id: int
) -> None:
    """Test that the update endpoints work with a long lived token.

    Test updating an invalid endpoint. This should always fail with a 401.

    Args:
        api_client: the test client.
        endpoint: the endpoint to test.
        id: the id of the object to delete.
    """
    _token = 'MHxHL4HrmmJHbAR1b0gV4OkpuEsxxmRL'

    # Do the request
    result = api_client.delete(
        f'/resources/{endpoint}/{id}', headers={'X-API-Token': _token}
    )

    # Validate the answer
    assert result.status_code == 401


@pytest.mark.parametrize(
    'endpoint, id',
    (
        ('tags', 4),
        ('tags', 5),
        ('tags', 6),
        ('user_settings', 4),
        ('user_settings', 5),
        ('user_settings', 6),
        ('api_tokens', 3),
        ('api_tokens', 4),
        ('api_tokens', 5),
    ),
)
def test_delete_long_lived_missing_token(
    api_client: TestClient, endpoint: str, id: int
) -> None:
    """Test that the delete endpoints work with a long lived token.

    Test updating an endpoint without a token. This should always fail with a
    401.

    Args:
        api_client: the test client.
        endpoint: the endpoint to test.
        id: the id of the object to delete.
    """
    _token = '6VZGMOdNUAhCzYhipVJJjHTsYIzwBrlg'

    # Do the request
    result = api_client.delete(
        f'/resources/{endpoint}/{id}', headers={'X-API-Token': _token}
    )

    # Validate the answer
    assert result.status_code == 401


@pytest.mark.parametrize(
    'endpoint, id',
    (
        ('users', 1),
        ('users', 2),
        ('users', 3),
        ('tags', 1),
        ('tags', 2),
        ('tags', 3),
        ('tags', 4),
        ('tags', 5),
        ('tags', 6),
        ('user_settings', 1),
        ('user_settings', 2),
        ('user_settings', 3),
        ('user_settings', 4),
        ('user_settings', 5),
        ('user_settings', 6),
        ('api_clients', 1),
        ('api_clients', 2),
        ('api_tokens', 1),
        ('api_tokens', 2),
    ),
)
def test_delete_long_lived_invalid_token(
    api_client: TestClient, endpoint: str, id: int
) -> None:
    """Test that the delete endpoints work with a long lived token.

    Test deleting an endpoint with a invalidtoken. This should always fail with
    a 401.

    Args:
        api_client: the test client.
        endpoint: the endpoint to test.
        id: the id of the object to delete.
    """
    _token = 'invalid_token'

    # Do the request
    result = api_client.delete(
        f'/resources/{endpoint}/{id}', headers={'X-API-Token': _token}
    )

    # Validate the answer
    assert result.status_code == 401


@pytest.mark.parametrize(
    'token',
    ['MHxHL4HrmmJHbAR1b0gV4OkpuEsxxmRL', 'Cbxfv44aNlWRMu4bVqawWu9vofhFWmED'],
)
def test_delete_api_token(api_client: TestClient, token: str) -> None:
    """Test that deletion of API tokens work.

    Happy path test.

    We do this in a seperate test because API tokens have no endpoint to
    create them, so we can't use the same test as the other resources.

    Args:
        api_client: the test client.
        token: the token to use for the test.
    """
    # Log in
    result = api_client.post(
        '/auth/login',
        json={
            'username': 'root',
            'password': 'root_pw',
            'title': 'test_delete_api_token',
        },
    )
    assert result.status_code == 200

    # Find the API token
    result = api_client.get(
        '/resources/api_tokens?filter=title==test_delete_api_token',
        headers={'X-API-Token': token},
    )
    response = result.json()
    assert result.status_code == 200
    assert len(response['resources']) == 1
    _token = response['resources'][0]

    # Do the request
    result = api_client.delete(
        f'/resources/api_tokens/{_token["id"]}', headers={'X-API-Token': token}
    )

    # Validate the answer
    assert result.status_code == 200
    assert result.json() == {'deleted': [_token['id']]}
