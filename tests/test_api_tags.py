"""Test the tag management of the REST API."""
# pylint: disable=too-many-arguments

import pytest
from fastapi.testclient import TestClient

# TODO: test tag retrieval


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
