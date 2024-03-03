"""Test the user management of the REST API."""
# pylint: disable=too-many-arguments

from fastapi.testclient import TestClient


def test_update_users_via_put_as_root(
    api_client: TestClient, random_api_token_root: str
) -> None:
    """Test updating users as root with the PUT HTTP method.

    Should update a User object with a new object.

    Args:
        api_client: the test client for making API requests.
        random_api_token_root: a token for the request.
    """
    result = api_client.put(
        '/resources/users/1',
        headers={'X-API-Token': random_api_token_root},
        json={
            'fullname': 'root new',
            'username': 'root',
            'email': 'root@example.com',
            'role': 1,
        },
    )
    response = result.json()
    assert result.status_code == 200
    assert len(response) == 1
    assert response[0]['id'] is not None
    assert response[0]['fullname'] == 'root new'


def test_update_non_existing_userss_as_root(
    api_client: TestClient, random_api_token_root: str
) -> None:
    """Test updating non existing users as root.

    Should raise an error.

    Args:
        api_client: the test client for making API requests.
        random_api_token_root: a token for the request.
    """
    result = api_client.put(
        '/resources/users/20012022',
        headers={'X-API-Token': random_api_token_root},
        json={
            'fullname': 'root new',
            'username': 'root',
            'email': 'root@example.com',
            'role': 1,
        },
    )
    response = result.json()
    assert result.status_code == 404
    assert response['error'] == 'No resources found that match the criteria.'


# TODO: More update tests


def test_delete_users_as_root(
    api_client: TestClient, random_api_token_root: str
) -> None:
    """Test delete users as root.

    Should delete a User object.

    Args:
        api_client: the test client for making API requests.
        random_api_token_root: a token for the request.
    """
    # Create a user to delete
    result = api_client.post(
        '/resources/users',
        headers={'X-API-Token': random_api_token_root},
        json=[
            {
                'username': 'user.to.delete',
                'fullname': 'user to delete',
                'email': 'delete_me@example.com',
                'role': 3,
            }
        ],
    )
    creation_response = result.json()

    # Delete the user
    result = api_client.delete(
        f'/resources/users/{creation_response[0]["id"]}',
        headers={'X-API-Token': random_api_token_root},
    )
    response = result.json()
    assert result.status_code == 200
    assert len(response['deleted']) == 1
    assert creation_response[0]['id'] in response['deleted']


def test_delete_non_existing_userss_as_root(
    api_client: TestClient, random_api_token_root: str
) -> None:
    """Test delete non existing users as root.

    Should raise an error.

    Args:
        api_client: the test client for making API requests.
        random_api_token_root: a token for the request.
    """
    result = api_client.delete(
        '/resources/users/20012022',
        headers={'X-API-Token': random_api_token_root},
    )
    response = result.json()
    assert result.status_code == 404
    assert response['error'] == 'No resources found that match the criteria.'


# TODO: More deletion tests
