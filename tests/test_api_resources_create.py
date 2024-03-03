"""Tests for adding resources using the REST API."""

from typing import Any

import pytest
from fastapi.testclient import TestClient


@pytest.mark.parametrize(
    'endpoint, objects',
    (
        (
            'users',
            [
                {
                    'fullname': 'test user 1',
                    'username': 'test_user_1',
                    'email': 'pytest@example.com',
                    'role': 3,
                },
            ],
        ),
        (
            'tags',
            [
                {
                    'title': 'test_tag_1',
                },
            ],
        ),
        (
            'tags',
            [
                {
                    'title': 'test_tag_2',
                    'color': '00ff00',
                },
            ],
        ),
        (
            'user_settings',
            [
                {
                    'setting': 'test_setting_1',
                    'value': 'yes',
                },
            ],
        ),
        (
            'api_clients',
            [
                {
                    'app_name': 'test_app_1',
                    'app_publisher': 'test_app_publisher_1',
                },
            ],
        ),
    ),
)
def test_create_resource_short_lived_root(
    api_client: TestClient, endpoint: str, objects: dict[str, Any]
) -> None:
    """Test that the create endpoints work with a short lived token.

    Happy path test; should always be a success and return some data. We test
    creating data for all paths that should enable the user to create data. We
    check the return value; if it contains a `id` field, we assume it was
    successful.

    We test this with the root user, meaning we can create data for all
    types of resources.

    Args:
        api_client: the test client.
        endpoint: the endpoint to test.
        objects: the objects to create.
    """
    _token = 'Cbxfv44aNlWRMu4bVqawWu9vofhFWmED'

    # Do the request
    result = api_client.post(
        f'/resources/{endpoint}', headers={'X-API-Token': _token}, json=objects
    )
    response = result.json()

    # Validate the answer
    assert result.status_code == 200
    assert len(response) == len(objects)

    # Remove the created resources
    for count in range(0, len(objects)):
        resource_id = response[count]['id']
        assert resource_id > 0
        api_client.delete(
            f'/resources/{endpoint}/{resource_id}',
            headers={'X-API-Token': _token},
        )
        pass
