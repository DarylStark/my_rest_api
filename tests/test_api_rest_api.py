"""Test for the REST API endpoints."""

from sys import version_info as py_version_info

from fastapi import __version__ as fastapi_version
from fastapi.testclient import TestClient
from my_data import __version__ as my_data_version
from my_model import __version__ as my_model_version
from pydantic import __version__ as pydantic_version
from pydantic_settings import __version__ as pydantic_settings_version

from my_rest_api import __version__ as api_version

from my_rest_api.my_rest_api import MyRESTAPI

from my_rest_api import __version__ as rest_api_version


def test_version(api_client: TestClient):
    """Test the version endpoint.

    This function sends a GET request to the '/api/version' endpoint.

    Args:
        api_client: a testclient for the application.
    """
    api_client.headers.pop('X-API-Key', None)
    response = api_client.get('/version')
    contents = response.json()
    assert response.status_code == 200
    assert contents == {
        'version': rest_api_version}
