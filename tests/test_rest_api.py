"""Test for the REST API endpoints."""

from fastapi.testclient import TestClient
from my_rest_api import __version__ as api_version
from my_rest_api.config import Settings


def test_version(api_client: TestClient):
    """Test the version endpoint.

    This function sends a GET request to the '/api/version' endpoint
    and asserts that the response status code is 200.

    Args:
        api_client: a testclient for the application.
    """
    response = api_client.get('/version')
    contents = response.json()
    assert response.status_code == 200
    assert contents['version'] == api_version
