"""Tests for updating resources using the REST API."""

from typing import Any

import pytest
from fastapi.testclient import TestClient


@pytest.mark.parametrize(
    'endpoint, object',
    (
        (
            'users',
            {
                'id': 2,
                'fullname': 'test user 1 updated',
                'username': 'test_user_1_updated',
                'email': 'test_user_1_updated@example.com',
                'role': 3,
            },
        ),
        (
            'tags',
            {
                'id': 1,
                'title': 'test_tag_1_updated',
            },
        ),
        (
            'tags',
            {
                'id': 1,
                'title': 'test_tag_2_updated',
                'color': '0000ff',
            },
        ),
        (
            'user_settings',
            {
                'id': 1,
                'setting': 'test_setting_1_udated',
                'value': 'yes_updated',
            },
        ),
        (
            'api_clients',
            {
                'id': 1,
                'app_name': 'test_app_1_updated',
                'app_publisher': 'test_app_publisher_1_updated',
            },
        ),
    ),
)
def test_update_short_lived_root(
    api_client: TestClient, endpoint: str, object: dict[str, Any]
) -> None:
    """Test that the update endpoints work with a short lived token.

    Happy path test; should always be a success and return some data. We test
    updating data for all paths that should enable the user to update data. We
    check the return value; if it contains a `id` field, we assume it was
    successful.

    We test this with the root user, meaning we can create data for all
    types of resources.

    Args:
        api_client: the test client.
        endpoint: the endpoint to test.
        object: the objects to create.
    """
    _token = 'Cbxfv44aNlWRMu4bVqawWu9vofhFWmED'

    id = object.pop('id')

    # Get the original data
    result = api_client.get(
        f'/resources/{endpoint}?filter=id=={id}',
        headers={'X-API-Token': _token},
    )
    original_data = result.json()['resources'][0]
    original_data_dict = {
        key: original_data[key] for key in object if key in original_data
    }

    # Do the request
    result = api_client.put(
        f'/resources/{endpoint}/{id}',
        headers={'X-API-Token': _token},
        json=object,
    )
    response = result.json()

    # Validate the answer
    assert result.status_code == 200
    for key, value in object.items():
        assert response[0][key] == value

    # Restore the original data
    result = api_client.put(
        f'/resources/{endpoint}/{id}',
        headers={'X-API-Token': _token},
        json=original_data_dict,
    )


@pytest.mark.parametrize(
    'endpoint, object',
    (
        (
            'users',
            {
                'id': 1,
                'fullname': 'test user 1 updated',
                'username': 'test_user_1_updated',
                'email': 'test_user_1_updated@example.com',
                'role': 3,
            },
        ),
    ),
)
def test_update_short_lived_normal_user_not_self(
    api_client: TestClient, endpoint: str, object: dict[str, Any]
) -> None:
    """Test that the update endpoints work with a short lived token.

    Tests with a normal user to update a user that is not itself. This should
    always fail with a 404 since the object is not found.

    Args:
        api_client: the test client.
        endpoint: the endpoint to test.
        object: the objects to create.
    """
    _token = 'pabq1d533eMucNPr5pHPuDMqxKRw1SE0'

    id = object.pop('id')

    # Do the request
    result = api_client.put(
        f'/resources/{endpoint}/{id}',
        headers={'X-API-Token': _token},
        json=object,
    )

    # Validate the answer
    assert result.status_code == 404


@pytest.mark.parametrize(
    'endpoint, object',
    (
        (
            'users',
            {
                'id': 2,
                'fullname': 'test user 1 updated',
                'username': 'test_user_1_updated',
                'email': 'test_user_1_updated@example.com',
                'role': 3,
            },
        ),
    ),
)
def test_update_short_lived_normal_user_self(
    api_client: TestClient, endpoint: str, object: dict[str, Any]
) -> None:
    """Test that the update endpoints work with a short lived token.

    Tests with a normal user to update itself. Should always be a success.

    Args:
        api_client: the test client.
        endpoint: the endpoint to test.
        object: the objects to create.
    """
    _token = 'pabq1d533eMucNPr5pHPuDMqxKRw1SE0'

    id = object.pop('id')

    # Get the original data
    result = api_client.get(
        f'/resources/{endpoint}?filter=id=={id}',
        headers={'X-API-Token': _token},
    )
    original_data = result.json()['resources'][0]
    original_data_dict = {
        key: original_data[key] for key in object if key in original_data
    }

    # Do the request
    result = api_client.put(
        f'/resources/{endpoint}/{id}',
        headers={'X-API-Token': _token},
        json=object,
    )
    response = result.json()

    # Validate the answer
    assert result.status_code == 200
    for key, value in object.items():
        assert response[0][key] == value

    # Restore the original data
    result = api_client.put(
        f'/resources/{endpoint}/{id}',
        headers={'X-API-Token': _token},
        json=original_data_dict,
    )


@pytest.mark.parametrize(
    'new_role',
    (1, 2),
)
def test_update_short_lived_normal_user_elevate_role(
    api_client: TestClient, new_role: int
) -> None:
    """Test if a user can elevate his own role.

    Tests with a normal user if it can change it's role. It shouldn't be
    allowed to do this.

    Args:
        api_client: the test client.
        new_role: the new role to set.
    """
    _token = 'pabq1d533eMucNPr5pHPuDMqxKRw1SE0'

    # Get the original data
    result = api_client.get(
        '/resources/users',
        headers={'X-API-Token': _token},
    )
    original_data = result.json()['resources'][0]
    original_data_dict = {
        key: original_data[key]
        for key in ['username', 'fullname', 'email', 'role']
    }
    original_data_dict['role'] = new_role

    # Do the request
    result = api_client.put(
        f'/resources/users/{original_data["id"]}',
        headers={'X-API-Token': _token},
        json=original_data_dict,
    )

    # Validate the answer
    assert result.status_code == 401


@pytest.mark.parametrize(
    'endpoint, object',
    (
        (
            'users',
            {
                'id': 2,
                'fullname': 'test user 1 updated',
                'username': 'test_user_1_updated',
                'email': 'test_user_1_updated@example.com',
                'role': 3,
            },
        ),
        (
            'tags',
            {
                'id': 1,
                'title': 'test_tag_1_updated',
            },
        ),
        (
            'tags',
            {
                'id': 1,
                'title': 'test_tag_2_updated',
                'color': '0000ff',
            },
        ),
        (
            'user_settings',
            {
                'id': 1,
                'setting': 'test_setting_1_udated',
                'value': 'yes_updated',
            },
        ),
    ),
)
def test_update_long_lived_root(
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

    id = object.pop('id')

    # Get the original data
    result = api_client.get(
        f'/resources/{endpoint}?filter=id=={id}',
        headers={'X-API-Token': _token},
    )
    original_data = result.json()['resources'][0]
    original_data_dict = {
        key: original_data[key] for key in object if key in original_data
    }

    # Do the request
    result = api_client.put(
        f'/resources/{endpoint}/{id}',
        headers={'X-API-Token': _token},
        json=object,
    )
    response = result.json()

    # Validate the answer
    assert result.status_code == 200
    for key, value in object.items():
        assert response[0][key] == value

    # Restore the original data
    result = api_client.put(
        f'/resources/{endpoint}/{id}',
        headers={'X-API-Token': _token},
        json=original_data_dict,
    )


@pytest.mark.parametrize(
    'endpoint, object',
    (
        (
            'api_clients',
            {
                'id': 1,
                'app_name': 'test_app_1_updated',
                'app_publisher': 'test_app_publisher_1_updated',
            },
        ),
    ),
)
def test_update_long_lived_invalid_enpoint(
    api_client: TestClient, endpoint: str, object: dict[str, Any]
) -> None:
    """Test that the update endpoints work with a long lived token.

    Test updating an invalid endpoint. This should always fail with a 401.

    Args:
        api_client: the test client.
        endpoint: the endpoint to test.
        object: the objects to create.
    """
    _token = 'MHxHL4HrmmJHbAR1b0gV4OkpuEsxxmRL'

    id = object.pop('id')

    # Do the request
    result = api_client.put(
        f'/resources/{endpoint}/{id}',
        headers={'X-API-Token': _token},
        json=object,
    )

    # Validate the answer
    assert result.status_code == 401


@pytest.mark.parametrize(
    'endpoint, object',
    (
        (
            'users',
            {
                'id': 2,
                'fullname': 'test user 1 updated',
                'username': 'test_user_1_updated',
                'email': 'test_user_1_updated@example.com',
                'role': 3,
            },
        ),
        (
            'tags',
            {
                'id': 1,
                'title': 'test_tag_1_updated',
            },
        ),
        (
            'tags',
            {
                'id': 1,
                'title': 'test_tag_2_updated',
                'color': '0000ff',
            },
        ),
        (
            'user_settings',
            {
                'id': 1,
                'setting': 'test_setting_1_udated',
                'value': 'yes_updated',
            },
        ),
    ),
)
def test_update_long_lived_missing_token(
    api_client: TestClient, endpoint: str, object: dict[str, Any]
) -> None:
    """Test that the update endpoints work with a long lived token.

    Test updating an endpoint without a token. This should always fail with a
    401.

    Args:
        api_client: the test client.
        endpoint: the endpoint to test.
        object: the objects to create.
    """
    _token = '6VZGMOdNUAhCzYhipVJJjHTsYIzwBrlg'

    id = object.pop('id')

    # Do the request
    result = api_client.put(
        f'/resources/{endpoint}/{id}',
        headers={'X-API-Token': _token},
        json=object,
    )

    # Validate the answer
    assert result.status_code == 401


@pytest.mark.parametrize(
    'endpoint, object',
    (
        (
            'users',
            {
                'id': 2,
                'fullname': 'test user 1 updated',
                'username': 'test_user_1_updated',
                'email': 'test_user_1_updated@example.com',
                'role': 3,
            },
        ),
        (
            'tags',
            {
                'id': 1,
                'title': 'test_tag_1_updated',
            },
        ),
        (
            'tags',
            {
                'id': 1,
                'title': 'test_tag_2_updated',
                'color': '0000ff',
            },
        ),
        (
            'user_settings',
            {
                'id': 1,
                'setting': 'test_setting_1_udated',
                'value': 'yes_updated',
            },
        ),
        (
            'api_clients',
            {
                'id': 1,
                'app_name': 'test_app_1_updated',
                'app_publisher': 'test_app_publisher_1_updated',
            },
        ),
    ),
)
def test_update_long_lived_invalid_token(
    api_client: TestClient, endpoint: str, object: dict[str, Any]
) -> None:
    """Test that the update endpoints work with a long lived token.

    Test updating an endpoint with a invalidtoken. This should always fail with
    a 401.

    Args:
        api_client: the test client.
        endpoint: the endpoint to test.
        object: the objects to create.
    """
    _token = 'invalid_token'

    id = object.pop('id')

    # Do the request
    result = api_client.put(
        f'/resources/{endpoint}/{id}',
        headers={'X-API-Token': _token},
        json=object,
    )

    # Validate the answer
    assert result.status_code == 401
