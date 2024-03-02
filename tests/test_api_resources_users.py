"""Test the user management of the REST API."""
# pylint: disable=too-many-arguments

from fastapi.testclient import TestClient


def test_retrieve_users_as_normal_user(
    api_client: TestClient, random_api_token_normal_user: str
) -> None:
    """Test retrieving users as a normal user.

    Should be succesfull.

    Args:
        api_client: the test client for making API requests.
        random_api_token_normal_user: a token for the request.
    """
    result = api_client.get(
        '/resources/users',
        headers={'X-API-Token': random_api_token_normal_user},
    )
    response = result.json()
    assert result.status_code == 200
    assert len(response) == 1
    assert response[0]['username'] == 'normal.user.1'


def test_retrieve_users_as_normal_user_with_long_lived_token(
    api_client: TestClient,
) -> None:
    """Test retrieving users as a normal user with a long lived token.

    Should be succesfull.

    Args:
        api_client: the test client for making API requests.
    """
    result = api_client.get(
        '/resources/users',
        headers={'X-API-Token': '2e3n4RSr4I6TnRSwXRpjDYhs9XIYNwhv'},
    )
    response = result.json()
    assert result.status_code == 200
    assert len(response) == 1
    assert response[0]['username'] == 'normal.user.2'


def test_retrieve_users_as_normal_user_with_long_lived_token_missing_scope(
    api_client: TestClient,
) -> None:
    """Test retrieving users as a normal user token without the correct scope.

    Should fail since the token is not given the correct scope.

    Args:
        api_client: the test client for making API requests.
    """
    result = api_client.get(
        '/resources/users',
        headers={'X-API-Token': 'BynORM5FVkt07BuQSA09lQUIrgCgOqEv'},
    )
    assert result.status_code == 401


def test_create_users_as_root(
    api_client: TestClient, random_api_token_root: str
) -> None:
    """Test creating users as root.

    Should be succesfull and return a list of new users with the id filled in.

    Args:
        api_client: the test client for making API requests.
        random_api_token_root: a token for the request.
    """
    result = api_client.post(
        '/resources/users',
        headers={'X-API-Token': random_api_token_root},
        json=[
            {
                'username': 'new_user_1',
                'fullname': 'New User 1',
                'email': 'new_user@test.com',
                'role': 3,
            }
        ],
    )
    response = result.json()
    assert result.status_code == 200
    assert len(response) == 1
    assert response[0]['id'] is not None

    # TODO: Remove created resource to make sure tests don't fail


# TODO: More creational tests


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
