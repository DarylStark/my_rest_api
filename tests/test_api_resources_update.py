"""Tests for adding resources using the REST API."""

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
    original_data = result.json()[0]
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
    pass
