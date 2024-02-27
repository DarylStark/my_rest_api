"""Test the tag management of the REST API."""
# pylint: disable=too-many-arguments

import pytest
from fastapi.testclient import TestClient

# TODO: test tag retrieval


def test_retrieve_tags_as_root(
        api_client: TestClient,
        random_api_token_root: str) -> None:
    """Test retrieving tags as root.

    Should be succesfull.

    Args:
        api_client: the test client for making API requests.
        random_api_token_root: a token for the request.
    """
    result = api_client.get(
        '/resources/tags',
        headers={'X-API-Token': random_api_token_root})
    response = result.json()
    assert result.status_code == 200
    assert len(response) == 3


def test_retrieve_tags_as_normal_user(
        api_client: TestClient,
        random_api_token_normal_user: str) -> None:
    """Test retrieving tags as normal user.

    Should be succesfull.

    Args:
        api_client: the test client for making API requests.
        random_api_token_normal_user: a token for the request.
    """
    result = api_client.get(
        '/resources/tags',
        headers={'X-API-Token': random_api_token_normal_user})
    response = result.json()
    assert result.status_code == 200
    assert len(response) == 3


def test_retrieve_tags_as_normal_user_with_long_lived_token(
        api_client: TestClient) -> None:
    """Test retrieving tags as a normal user with a long lived token.

    Should be succesfull.

    Args:
        api_client: the test client for making API requests.
    """
    result = api_client.get(
        '/resources/tags',
        headers={'X-API-Token': '2e3n4RSr4I6TnRSwXRpjDYhs9XIYNwhv'})
    response = result.json()
    assert result.status_code == 200
    assert len(response) == 3


def test_retrieve_tags_as_normal_user_with_long_lived_token_missing_scope(
        api_client: TestClient) -> None:
    """Test retrieving tags as a normal user token without the correct scope.

    Should fail since the token is not given the correct scope.

    Args:
        api_client: the test client for making API requests.
    """
    result = api_client.get(
        '/resources/tags',
        headers={'X-API-Token': 'BynORM5FVkt07BuQSA09lQUIrgCgOqEv'})
    assert result.status_code == 401


@pytest.mark.parametrize('field_name, operator, value, expected_length', [
    ('id', '==', 1, 1),
    ('id', '!=', 1, 2),
    ('id', '<', 3, 2),
    ('id', '>', 1, 2),
    ('id', '<=', 3, 3),
    ('id', '>=', 2, 2),
    ('title', '==', 'root_tag_1', 1),
    ('title', '=contains=', 'tag_1', 1),
    ('title', '=!contains=', 'tag_1', 2)
])
def test_retrieve_tags_with_filters_as_root(
        api_client: TestClient,
        random_api_token_root: str,
        field_name: str,
        operator: str,
        value: str,
        expected_length: int) -> None:
    """Test retrieving tags with filters.

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
        f'/resources/tags?filter={filter_argument}',
        headers={'X-API-Token': random_api_token_root})
    response = result.json()
    assert result.status_code == 200
    assert len(response) == expected_length


def test_retrieve_tags_with_invalid_filter_as_root(
        api_client: TestClient,
        random_api_token_root: str) -> None:
    """Test retrieving tags with invalid filters.

    Should fail.

    Args:
        api_client: the test client for making API requests.
        random_api_token_root: a token for the request.
    """
    result = api_client.get(
        '/resources/tags?filter=invalid_filter',
        headers={'X-API-Token': random_api_token_root})
    assert result.status_code == 400
    response = result.json()
    assert response['error'] == 'Filter "invalid_filter" is in invalid format.'


def test_retrieve_tags_with_invalid_filter_field_as_root(
        api_client: TestClient,
        random_api_token_root: str) -> None:
    """Test retrieving tags with invalid filter field

    Should fail.

    Args:
        api_client: the test client for making API requests.
        random_api_token_root: a token for the request.
    """
    result = api_client.get(
        '/resources/tags?filter=user_id==1',
        headers={'X-API-Token': random_api_token_root})
    assert result.status_code == 400
    response = result.json()
    assert response['error'] == ('Field "user_id" is not allowed to be '
                                 + 'filtered on.')


def test_retrieving_tags_with_sorting_on_title(
        api_client: TestClient,
        random_api_token_root: str) -> None:
    """Test retrieving tags with sorting.

    Should be succesfull.

    Args:
        api_client: the test client for making API requests.
        random_api_token_root: a token for the request.
    """
    result = api_client.get(
        '/resources/tags?sort=title',
        headers={'X-API-Token': random_api_token_root})
    response = result.json()
    assert result.status_code == 200
    assert len(response) == 3
    assert response[0]['title'] == 'root_tag_1'
    assert response[1]['title'] == 'root_tag_2'
    assert response[2]['title'] == 'root_tag_3'


def test_retrieving_tags_invalid_sort_field(
        api_client: TestClient,
        random_api_token_root: str) -> None:
    """Test retrieving tags with invalid sorting.

    Should fail.

    Args:
        api_client: the test client for making API requests.
        random_api_token_root: a token for the request.
    """
    result = api_client.get(
        '/resources/tags?sort=invalid_field',
        headers={'X-API-Token': random_api_token_root})
    assert result.status_code == 400
    response = result.json()
    assert response['error'] == 'Invalid sort field: "invalid_field"'
    assert response['allowed_sort_fields'] == [
        'id', 'color', 'title'
    ]


def test_retrieving_tags_with_pagination(
        api_client: TestClient,
        random_api_token_root: str) -> None:
    """Test retrieving tags with pagination.

    Should be succesfull.

    Args:
        api_client: the test client for making API requests.
        random_api_token_root: a token for the request.
    """
    result = api_client.get(
        '/resources/tags?page_size=2&page=2&sort=title',
        headers={'X-API-Token': random_api_token_root})
    response = result.json()
    assert result.status_code == 200
    assert len(response) == 1
    assert response[0]['title'] == 'root_tag_3'


def test_retrieving_tags_with_invalid_page_size(
        api_client: TestClient,
        random_api_token_root: str) -> None:
    """Test retrieving tags with invalid page size.

    Should fail.

    Args:
        api_client: the test client for making API requests.
        random_api_token_root: a token for the request.
    """
    result = api_client.get(
        '/resources/tags?page_size=1000',
        headers={'X-API-Token': random_api_token_root})
    assert result.status_code == 400
    response = result.json()
    assert response['error'] == 'Invalid page size.'
    assert response['max_page'] == 250


@pytest.mark.parametrize('page_number', [0, -1, 10000])
def test_retrieving_tags_with_invalid_page_number(
        api_client: TestClient,
        random_api_token_root: str,
        page_number: int) -> None:
    """Test retrieving tags with invalid page number.

    Should fail.

    Args:
        api_client: the test client for making API requests.
        random_api_token_root: a token for the request.
        page_number: the page number to test.
    """
    result = api_client.get(
        f'/resources/tags?page={page_number}&page_size=2',
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
        (3, ['first', 'last', 'prev'])
    ]
)
def test_retrieving_tags_check_http_links(
        api_client: TestClient,
        random_api_token_root: str,
        page_number: int,
        expected_links: list[str]) -> None:
    """Test retrieving tags and check the links in the response.

    Should be succesfull.

    Args:
        api_client: the test client for making API requests.
        random_api_token_root: a token for the request.
        page_number: the page number to test.
        expected_links: the links we expect to find in the response.
    """
    result = api_client.get(
        f'/resources/tags?page_size=1&page={page_number}',
        headers={'X-API-Token': random_api_token_root})
    response = result.json()
    assert result.status_code == 200
    assert len(response) == 1
    for expected_link in expected_links:
        assert expected_link in result.links
        assert result.links[expected_link] is not None


def test_create_tags_as_root(
        api_client: TestClient,
        random_api_token_root: str) -> None:
    """Test creating tags as root.

    Should be succesfull and return a list of new tags with the id filled in.

    Args:
        api_client: the test client for making API requests.
        random_api_token_root: a token for the request.
    """
    result = api_client.post(
        '/resources/tags',
        headers={'X-API-Token': random_api_token_root},
        json=[{
            'title': 'tag1',
            'color': 'ff0000'
        }])
    response = result.json()
    assert result.status_code == 200
    assert len(response) == 1
    assert response[0]['id'] is not None

    # TODO: Remove created resource to make sure tests don't fail

# TODO: more creational tests


def test_update_tags_via_put_as_root(
        api_client: TestClient,
        random_api_token_root: str) -> None:
    """Test updating tags as root with the PUT HTTP method.

    Should update a Tag object with a new object.
    """
    result = api_client.put(
        '/resources/tags/1',
        headers={'X-API-Token': random_api_token_root},
        json={
            'title': 'root_tag_1',
            'color': 'ff0000'
        })
    response = result.json()
    assert result.status_code == 200
    assert len(response) == 1
    assert response[0]['id'] is not None
    assert response[0]['color'] == 'ff0000'

# TODO: More update tests
