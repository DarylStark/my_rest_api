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
        '/resources/users',
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
        '/resources/users',
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
        '/resources/users',
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
        '/resources/users',
        headers={'X-API-Token': 'BynORM5FVkt07BuQSA09lQUIrgCgOqEv'})
    assert result.status_code == 401


@pytest.mark.parametrize('field_name, operator, value, expected_length', [
    ('id', '==', 1, 1),
    ('id', '!=', 1, 3),
    ('id', '<', 4, 3),
    ('id', '>', 1, 3),
    ('id', '<=', 3, 3),
    ('id', '>=', 2, 3),
    ('username', '==', 'root', 1),
    ('username', '=contains=', 'normal', 2),
    ('username', '=!contains=', 'service', 3),
    ('fullname', '==', 'root', 1),
    ('fullname', '=contains=', 'normal', 2),
    ('fullname', '=!contains=', 'service', 3),
    ('email', '==', 'normal_user_1@example.com', 1),
    ('email', '=contains=', 'normal_user', 2),
    ('email', '=!contains=', 'service', 3),
])
def test_retrieve_users_with_filters_as_root(
        api_client: TestClient,
        random_api_token_root: str,
        field_name: str,
        operator: str,
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
    filter_argument = f'{field_name}{operator}{value}'
    result = api_client.get(
        f'/resources/users?filter={filter_argument}',
        headers={'X-API-Token': random_api_token_root})
    response = result.json()
    assert result.status_code == 200
    assert len(response) == expected_length


def test_retrieve_users_with_invalid_filter_as_root(
        api_client: TestClient,
        random_api_token_root: str) -> None:
    """Test retrieving users with invalid filters.

    Should fail.

    Args:
        api_client: the test client for making API requests.
        random_api_token_root: a token for the request.
    """
    result = api_client.get(
        '/resources/users?filter=invalid_filter',
        headers={'X-API-Token': random_api_token_root})
    assert result.status_code == 400
    response = result.json()
    assert response['error'] == 'Filter "invalid_filter" is in invalid format.'


def test_retrieve_users_with_invalid_filter_field_as_root(
        api_client: TestClient,
        random_api_token_root: str) -> None:
    """Test retrieving users with invalid filter field

    Should fail.

    Args:
        api_client: the test client for making API requests.
        random_api_token_root: a token for the request.
    """
    result = api_client.get(
        '/resources/users?filter=password_hash=contains=e',
        headers={'X-API-Token': random_api_token_root})
    assert result.status_code == 400
    response = result.json()
    assert response['error'] == ('Field "password_hash" is not allowed to be '
                                 + 'filtered on.')


def test_retrieving_users_with_sorting_on_username(
        api_client: TestClient,
        random_api_token_root: str) -> None:
    """Test retrieving users with sorting.

    Should be succesfull.

    Args:
        api_client: the test client for making API requests.
        random_api_token_root: a token for the request.
    """
    result = api_client.get(
        '/resources/users?sort=username',
        headers={'X-API-Token': random_api_token_root})
    response = result.json()
    assert result.status_code == 200
    assert len(response) == 4
    assert response[0]['username'] == 'normal.user.1'
    assert response[1]['username'] == 'normal.user.2'
    assert response[2]['username'] == 'root'
    assert response[3]['username'] == 'service.user'


def test_retrieving_users_with_sorting_on_role(
        api_client: TestClient,
        random_api_token_root: str) -> None:
    """Test retrieving users with sorting.

    Should be succesfull.

    Args:
        api_client: the test client for making API requests.
        random_api_token_root: a token for the request.
    """
    result = api_client.get(
        '/resources/users?sort=role',
        headers={'X-API-Token': random_api_token_root})
    response = result.json()
    assert result.status_code == 200
    assert len(response) == 4
    assert response[0]['username'] == 'root'
    assert response[1]['username'] == 'service.user'
    assert response[2]['username'] == 'normal.user.1'
    assert response[3]['username'] == 'normal.user.2'


def test_retrieving_users_invalid_sort_field(
        api_client: TestClient,
        random_api_token_root: str) -> None:
    """Test retrieving users with invalid sorting.

    Should fail.

    Args:
        api_client: the test client for making API requests.
        random_api_token_root: a token for the request.
    """
    result = api_client.get(
        '/resources/users?sort=invalid_field',
        headers={'X-API-Token': random_api_token_root})
    assert result.status_code == 400
    response = result.json()
    assert response['error'] == 'Invalid sort field: "invalid_field"'
    assert response['allowed_sort_fields'] == [
        'id', 'username', 'fullname', 'email', 'role', 'created'
    ]


def test_retrieving_users_with_pagination(
        api_client: TestClient,
        random_api_token_root: str) -> None:
    """Test retrieving users with pagination.

    Should be succesfull.

    Args:
        api_client: the test client for making API requests.
        random_api_token_root: a token for the request.
    """
    result = api_client.get(
        '/resources/users?page_size=2&page=2&sort=username',
        headers={'X-API-Token': random_api_token_root})
    response = result.json()
    assert result.status_code == 200
    assert len(response) == 2
    assert response[0]['username'] == 'root'
    assert response[1]['username'] == 'service.user'


def test_retrieving_users_with_invalid_page_size(
        api_client: TestClient,
        random_api_token_root: str) -> None:
    """Test retrieving users with invalid page size.

    Should fail.

    Args:
        api_client: the test client for making API requests.
        random_api_token_root: a token for the request.
    """
    result = api_client.get(
        '/resources/users?page_size=1000',
        headers={'X-API-Token': random_api_token_root})
    assert result.status_code == 400
    response = result.json()
    assert response['error'] == 'Invalid page size.'
    assert response['max_page'] == 250


@pytest.mark.parametrize('page_number', [0, -1, 10000])
def test_retrieving_users_with_invalid_page_number(
        api_client: TestClient,
        random_api_token_root: str,
        page_number: int) -> None:
    """Test retrieving users with invalid page number.

    Should fail.

    Args:
        api_client: the test client for making API requests.
        random_api_token_root: a token for the request.
        page_number: the page number to test.
    """
    result = api_client.get(
        f'/resources/users?page={page_number}&page_size=2',
        headers={'X-API-Token': random_api_token_root})
    assert result.status_code == 400
    response = result.json()
    assert response['error'] == 'Invalid page number.'
    assert response['max_page'] == 2


@pytest.mark.parametrize(
    'page_number, expected_links',
    [
        (1, ['first', 'last', 'next']),
        (2, ['first', 'last', 'next', 'prev']),
        (3, ['first', 'last', 'next', 'prev']),
        (4, ['first', 'last', 'prev'])
    ]
)
def test_retrieving_users_check_http_links(
        api_client: TestClient,
        random_api_token_root: str,
        page_number: int,
        expected_links: list[str]) -> None:
    """Test retrieving users and check the links in the response.

    Should be succesfull.

    Args:
        api_client: the test client for making API requests.
        random_api_token_root: a token for the request.
        page_number: the page number to test.
        expected_links: the links we expect to find in the response.
    """
    result = api_client.get(
        f'/resources/users?page_size=1&page={page_number}',
        headers={'X-API-Token': random_api_token_root})
    response = result.json()
    assert result.status_code == 200
    assert len(response) == 1
    for expected_link in expected_links:
        assert expected_link in result.links
        assert result.links[expected_link] is not None
