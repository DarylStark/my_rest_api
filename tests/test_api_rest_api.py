"""Test for the REST API endpoints."""

from fastapi.testclient import TestClient
from my_rest_api import __version__ as rest_api_version


def test_version(api_client: TestClient) -> None:
    """Test the version endpoint.

    This function sends a GET request to the '/api/version' endpoint.

    Args:
        api_client: a testclient for the application.
    """
    api_client.headers.pop('X-API-Token', None)
    response = api_client.get('/version')
    contents = response.json()
    assert response.status_code == 200
    assert contents == {'version': rest_api_version}
