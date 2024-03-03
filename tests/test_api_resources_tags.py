"""Test the tag management of the REST API."""
# pylint: disable=too-many-arguments

from fastapi.testclient import TestClient


def test_update_tags_via_put_as_root(
    api_client: TestClient, random_api_token_root: str
) -> None:
    """Test updating tags as root with the PUT HTTP method.

    Should update a Tag object with a new object.

    Args:
        api_client: the test client for making API requests.
        random_api_token_root: a token for the request.
    """
    result = api_client.put(
        '/resources/tags/1',
        headers={'X-API-Token': random_api_token_root},
        json={'title': 'root_tag_1', 'color': 'ff0000'},
    )
    response = result.json()
    assert result.status_code == 200
    assert len(response) == 1
    assert response[0]['id'] is not None
    assert response[0]['color'] == 'ff0000'


def test_update_non_existing_tags_as_root(
    api_client: TestClient, random_api_token_root: str
) -> None:
    """Test updating non existing tags as root.

    Should raise an error.

    Args:
        api_client: the test client for making API requests.
        random_api_token_root: a token for the request.
    """
    result = api_client.put(
        '/resources/tags/20012022',
        headers={'X-API-Token': random_api_token_root},
        json={'title': 'root_tag_1', 'color': 'ff0000'},
    )
    response = result.json()
    assert result.status_code == 404
    assert response['error'] == 'No resources found that match the criteria.'


# TODO: More update tests


def test_delete_tags_as_root(
    api_client: TestClient, random_api_token_root: str
) -> None:
    """Test delete tags as root.

    Should delete a Tag object.

    Args:
        api_client: the test client for making API requests.
        random_api_token_root: a token for the request.
    """
    # Create a Tag to delete
    result = api_client.post(
        '/resources/tags',
        headers={'X-API-Token': random_api_token_root},
        json=[{'title': 'tag_to_delete', 'color': 'ff0000'}],
    )
    creation_response = result.json()

    # Delete the tag
    result = api_client.delete(
        f'/resources/tags/{creation_response[0]["id"]}',
        headers={'X-API-Token': random_api_token_root},
    )
    response = result.json()
    assert result.status_code == 200
    assert len(response['deleted']) == 1
    assert creation_response[0]['id'] in response['deleted']


def test_delete_non_existing_tags_as_root(
    api_client: TestClient, random_api_token_root: str
) -> None:
    """Test delete non existing tags as root.

    Should raise an error.

    Args:
        api_client: the test client for making API requests.
        random_api_token_root: a token for the request.
    """
    result = api_client.delete(
        '/resources/tags/20012022',
        headers={'X-API-Token': random_api_token_root},
    )
    response = result.json()
    assert result.status_code == 404
    assert response['error'] == 'No resources found that match the criteria.'


# TODO: More deletion tests
