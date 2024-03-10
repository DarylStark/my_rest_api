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
                    'email': 'test_user_1@example.com',
                    'role': 3,
                },
            ],
        ),
        (
            'users',
            [
                {
                    'fullname': 'test user 1',
                    'username': 'test_user_1',
                    'email': 'test_user_1@example.com',
                    'role': 3,
                },
                {
                    'fullname': 'test user 2',
                    'username': 'test_user_2',
                    'email': 'test_user_2@example.com',
                    'role': 3,
                },
                {
                    'fullname': 'test user 3',
                    'username': 'test_user_3',
                    'email': 'test_user_3@example.com',
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
                    'title': 'test_tag_1',
                    'color': '00ff00',
                },
            ],
        ),
        (
            'tags',
            [
                {
                    'title': 'test_tag_1',
                    'color': '0000ff',
                },
                {
                    'title': 'test_tag_2',
                    'color': '00ff00',
                },
                {
                    'title': 'test_tag_3',
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
            'user_settings',
            [
                {
                    'setting': 'test_setting_1',
                    'value': 'yes',
                },
                {
                    'setting': 'test_setting_2',
                    'value': 'no',
                },
                {
                    'setting': 'test_setting_3',
                    'value': 'maybe',
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
        (
            'api_clients',
            [
                {
                    'app_name': 'test_app_1',
                    'app_publisher': 'test_app_publisher_1',
                },
                {
                    'app_name': 'test_app_2',
                    'app_publisher': 'test_app_publisher_2',
                },
                {
                    'app_name': 'test_app_3',
                    'app_publisher': 'test_app_publisher_3',
                },
            ],
        ),
    ),
)
def test_create_short_lived_root(
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
    assert result.status_code == 201
    assert len(response) == len(objects)

    # Remove the created resources
    for count in range(0, len(objects)):
        resource_id = response[count]['id']
        assert resource_id > 0
        api_client.delete(
            f'/resources/{endpoint}/{resource_id}',
            headers={'X-API-Token': _token},
        )


@pytest.mark.parametrize(
    'endpoint, objects',
    (
        (
            'users',
            [
                {
                    'fullname': 'test user 1',
                    'username': 'test_user_1',
                    'email': 'test_user_1@example.com',
                    'role': 3,
                },
            ],
        ),
    ),
)
def test_create_short_lived_normal_user(
    api_client: TestClient, endpoint: str, objects: dict[str, Any]
) -> None:
    """Test that the create endpoints work with a short lived token.

    Tests with a normal user.

    Unhappy path test; should always fail since we only tests endpoints that
    are only available to the root user.

    Args:
        api_client: the test client.
        endpoint: the endpoint to test.
        objects: the objects to create.
    """
    _token = 'pabq1d533eMucNPr5pHPuDMqxKRw1SE0'

    # Do the request
    result = api_client.post(
        f'/resources/{endpoint}', headers={'X-API-Token': _token}, json=objects
    )

    # Validate the answer
    assert result.status_code == 401


@pytest.mark.parametrize(
    'endpoint, objects',
    (
        (
            'users',
            [
                {
                    'fullname': 'test user 1',
                    'username': 'test_user_1',
                    'email': 'test_user_1@example.com',
                    'role': 3,
                },
            ],
        ),
        (
            'users',
            [
                {
                    'fullname': 'test user 1',
                    'username': 'test_user_1',
                    'email': 'test_user_1@example.com',
                    'role': 3,
                },
                {
                    'fullname': 'test user 2',
                    'username': 'test_user_2',
                    'email': 'test_user_2@example.com',
                    'role': 3,
                },
                {
                    'fullname': 'test user 3',
                    'username': 'test_user_3',
                    'email': 'test_user_3@example.com',
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
                    'title': 'test_tag_1',
                    'color': '00ff00',
                },
            ],
        ),
        (
            'tags',
            [
                {
                    'title': 'test_tag_1',
                    'color': '0000ff',
                },
                {
                    'title': 'test_tag_2',
                    'color': '00ff00',
                },
                {
                    'title': 'test_tag_3',
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
            'user_settings',
            [
                {
                    'setting': 'test_setting_1',
                    'value': 'yes',
                },
                {
                    'setting': 'test_setting_2',
                    'value': 'no',
                },
                {
                    'setting': 'test_setting_3',
                    'value': 'maybe',
                },
            ],
        ),
    ),
)
def test_create_long_lived(
    api_client: TestClient, endpoint: str, objects: dict[str, Any]
) -> None:
    """Test that the create endpoints work with a long lived token.

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
    _token = 'MHxHL4HrmmJHbAR1b0gV4OkpuEsxxmRL'

    # Do the request
    result = api_client.post(
        f'/resources/{endpoint}', headers={'X-API-Token': _token}, json=objects
    )
    response = result.json()

    # Validate the answer
    assert result.status_code == 201
    assert len(response) == len(objects)

    # Remove the created resources
    for count in range(0, len(objects)):
        resource_id = response[count]['id']
        assert resource_id > 0
        api_client.delete(
            f'/resources/{endpoint}/{resource_id}',
            headers={'X-API-Token': _token},
        )


@pytest.mark.parametrize(
    'endpoint, objects',
    (
        (
            'api_clients',
            [
                {
                    'app_name': 'test_app_1',
                    'app_publisher': 'test_app_publisher_1',
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
                {
                    'app_name': 'test_app_2',
                    'app_publisher': 'test_app_publisher_2',
                },
                {
                    'app_name': 'test_app_3',
                    'app_publisher': 'test_app_publisher_3',
                },
            ],
        ),
    ),
)
def test_create_long_lived_invalid_endpoint(
    api_client: TestClient,
    endpoint: str,
    objects: dict[str, Any],
) -> None:
    """Test that the create endpoints work with a long lived token.

    Unhappy path test; we test if endpoints that require a short lived token
    fail when given a long lived token.

    We test this with the root user, meaning we can create data for all
    types of resources.

    Args:
        api_client: the test client.
        endpoint: the endpoint to test.
        objects: the objects to create.
    """
    _token = 'MHxHL4HrmmJHbAR1b0gV4OkpuEsxxmRL'

    # Do the request
    result = api_client.post(
        f'/resources/{endpoint}',
        headers={'X-API-Token': _token},
        json=objects,
    )

    # Validate the answer
    assert result.status_code == 401


@pytest.mark.parametrize(
    'endpoint, objects',
    (
        (
            'users',
            [
                {
                    'fullname': 'test user 1',
                    'username': 'test_user_1',
                    'email': 'test_user_1@example.com',
                    'role': 3,
                },
            ],
        ),
        (
            'users',
            [
                {
                    'fullname': 'test user 1',
                    'username': 'test_user_1',
                    'email': 'test_user_1@example.com',
                    'role': 3,
                },
                {
                    'fullname': 'test user 2',
                    'username': 'test_user_2',
                    'email': 'test_user_2@example.com',
                    'role': 3,
                },
                {
                    'fullname': 'test user 3',
                    'username': 'test_user_3',
                    'email': 'test_user_3@example.com',
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
                    'title': 'test_tag_1',
                    'color': '00ff00',
                },
            ],
        ),
        (
            'tags',
            [
                {
                    'title': 'test_tag_1',
                    'color': '0000ff',
                },
                {
                    'title': 'test_tag_2',
                    'color': '00ff00',
                },
                {
                    'title': 'test_tag_3',
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
            'user_settings',
            [
                {
                    'setting': 'test_setting_1',
                    'value': 'yes',
                },
                {
                    'setting': 'test_setting_2',
                    'value': 'no',
                },
                {
                    'setting': 'test_setting_3',
                    'value': 'maybe',
                },
            ],
        ),
    ),
)
def test_create_long_lived_missing_scope(
    api_client: TestClient, endpoint: str, objects: dict[str, Any]
) -> None:
    """Test that the create endpoints work with a long lived token.

    Unhappy path test; we test if endpoints that can work with a long lived
    token fail when the needed scope is missing.

    Args:
        api_client: the test client.
        endpoint: the endpoint to test.
        objects: the objects to create.
    """
    _token = '6VZGMOdNUAhCzYhipVJJjHTsYIzwBrlg'

    # Do the request
    result = api_client.post(
        f'/resources/{endpoint}', headers={'X-API-Token': _token}, json=objects
    )

    # Validate the answer
    assert result.status_code == 401


@pytest.mark.parametrize(
    'endpoint, objects',
    (
        (
            'users',
            [
                {
                    'fullname': 'test user 1',
                    'username': 'test_user_1',
                    'email': 'test_user_1@example.com',
                    'role': 3,
                },
            ],
        ),
        (
            'users',
            [
                {
                    'fullname': 'test user 1',
                    'username': 'test_user_1',
                    'email': 'test_user_1@example.com',
                    'role': 3,
                },
                {
                    'fullname': 'test user 2',
                    'username': 'test_user_2',
                    'email': 'test_user_2@example.com',
                    'role': 3,
                },
                {
                    'fullname': 'test user 3',
                    'username': 'test_user_3',
                    'email': 'test_user_3@example.com',
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
                    'title': 'test_tag_1',
                    'color': '00ff00',
                },
            ],
        ),
        (
            'tags',
            [
                {
                    'title': 'test_tag_1',
                    'color': '0000ff',
                },
                {
                    'title': 'test_tag_2',
                    'color': '00ff00',
                },
                {
                    'title': 'test_tag_3',
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
            'user_settings',
            [
                {
                    'setting': 'test_setting_1',
                    'value': 'yes',
                },
                {
                    'setting': 'test_setting_2',
                    'value': 'no',
                },
                {
                    'setting': 'test_setting_3',
                    'value': 'maybe',
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
        (
            'api_clients',
            [
                {
                    'app_name': 'test_app_1',
                    'app_publisher': 'test_app_publisher_1',
                },
                {
                    'app_name': 'test_app_2',
                    'app_publisher': 'test_app_publisher_2',
                },
                {
                    'app_name': 'test_app_3',
                    'app_publisher': 'test_app_publisher_3',
                },
            ],
        ),
    ),
)
def test_create_missing_token(
    api_client: TestClient, endpoint: str, objects: dict[str, Any]
) -> None:
    """Test that the create endpoints work with a long lived token.

    Unhappy path test; we test if endpoints that can work with a long lived
    token fail when the token is missing.

    Args:
        api_client: the test client.
        endpoint: the endpoint to test.
        objects: the objects to create.
    """
    # Do the request
    result = api_client.post(f'/resources/{endpoint}', json=objects)

    # Validate the answer
    assert result.status_code == 401


@pytest.mark.parametrize(
    'endpoint, objects',
    (
        (
            'users',
            [
                {
                    'fullname': 'test user 1',
                    'username': 'test_user_1',
                    'email': 'test_user_1@example.com',
                    'role': 3,
                },
            ],
        ),
        (
            'users',
            [
                {
                    'fullname': 'test user 1',
                    'username': 'test_user_1',
                    'email': 'test_user_1@example.com',
                    'role': 3,
                },
                {
                    'fullname': 'test user 2',
                    'username': 'test_user_2',
                    'email': 'test_user_2@example.com',
                    'role': 3,
                },
                {
                    'fullname': 'test user 3',
                    'username': 'test_user_3',
                    'email': 'test_user_3@example.com',
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
                    'title': 'test_tag_1',
                    'color': '00ff00',
                },
            ],
        ),
        (
            'tags',
            [
                {
                    'title': 'test_tag_1',
                    'color': '0000ff',
                },
                {
                    'title': 'test_tag_2',
                    'color': '00ff00',
                },
                {
                    'title': 'test_tag_3',
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
            'user_settings',
            [
                {
                    'setting': 'test_setting_1',
                    'value': 'yes',
                },
                {
                    'setting': 'test_setting_2',
                    'value': 'no',
                },
                {
                    'setting': 'test_setting_3',
                    'value': 'maybe',
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
        (
            'api_clients',
            [
                {
                    'app_name': 'test_app_1',
                    'app_publisher': 'test_app_publisher_1',
                },
                {
                    'app_name': 'test_app_2',
                    'app_publisher': 'test_app_publisher_2',
                },
                {
                    'app_name': 'test_app_3',
                    'app_publisher': 'test_app_publisher_3',
                },
            ],
        ),
    ),
)
def test_create_invalid_token(
    api_client: TestClient, endpoint: str, objects: dict[str, Any]
) -> None:
    """Test that the create endpoints work with a long lived token.

    Unhappy path test; we test if endpoints that can work with a long lived
    token fail when the token is invalid.

    Args:
        api_client: the test client.
        endpoint: the endpoint to test.
        objects: the objects to create.
    """
    _token = 'invalid_token'

    # Do the request
    result = api_client.post(
        f'/resources/{endpoint}', headers={'X-API-Token': _token}, json=objects
    )

    # Validate the answer
    assert result.status_code == 401
