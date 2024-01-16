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


def test_version_as_unauthorized_user(api_client: TestClient):
    """Test the version endpoint as an unauthorized user.

    This function sends a GET request to the '/api/version' endpoint
    and asserts that the response status code is 403.

    Args:
        api_client: a testclient for the application.
    """
    api_client.headers.pop('X-API-Key', None)
    response = api_client.get('/version')
    contents = response.json()
    assert response.status_code == 403
    assert contents == {
        'error': 'Not authorized to retrieve version information'}


def test_version_as_unauthenticated_user_different_config(
        api_client: TestClient) -> None:
    """Test the version endpoint as an unauthorized user.

    This function sends a GET request to the '/api/version' endpoint
    and asserts that the response status code is 200, but with no information.

    Args:
        api_client: a testclient for the application.
    """
    MyRESTAPI.get_instance().config.version_unauthorized = True
    api_client.headers.pop('X-API-Key', None)
    response = api_client.get('/version')
    contents = response.json()
    assert response.status_code == 200
    assert contents == {
        'version': None,
        'python_version': None,
        'internal_dependencies': None,
        'external_dependencies': None
    }


def test_version_as_root_user(
        api_client: TestClient,
        random_api_token_root: str) -> None:
    """Test the version endpoint as a root user.

    This function sends a GET request to the '/api/version' endpoint
    and asserts that the response status code is 200.

    Args:
        api_client: a testclient for the application.
        random_api_token_root: API token for a root user.
    """
    api_client.headers.update({'X-API-Key': random_api_token_root})
    response = api_client.get('/version')
    contents = response.json()

    python_version = (f'{py_version_info.major}.{py_version_info.minor}.' +
                      f'{py_version_info.micro}')

    assert response.status_code == 200
    assert contents == {
        'version': api_version,
        'python_version': python_version,
        'internal_dependencies': {
            'ds-my-data': my_data_version,
            'ds-my-model': my_model_version
        },
        'external_dependencies': {
            'fastapi': fastapi_version,
            'pydantic': pydantic_version,
            'pydantic_settings': pydantic_settings_version
        }
    }


def test_version_as_user(
        api_client: TestClient,
        random_api_token_normal_user: str) -> None:
    """Test the version endpoint as a root user.

    This function sends a GET request to the '/api/version' endpoint
    and asserts that the response status code is 200.

    Args:
        api_client: a testclient for the application.
        random_api_token_normal_user: API token for a normal user.
    """
    api_client.headers.update({'X-API-Key': random_api_token_normal_user})
    response = api_client.get('/version')
    contents = response.json()

    assert response.status_code == 200
    assert contents == {
        'version': api_version,
        'python_version': None,
        'internal_dependencies': None,
        'external_dependencies': None
    }


def test_authorized_with_version_hidden(
        api_client: TestClient,
        random_api_token_normal_user: str) -> None:
    """Test the version endpoint as a root user without a version.

    This function sends a GET request to the '/api/version' endpoint
    and asserts that the response status code is 200.

    Args:
        api_client: a testclient for the application.
        random_api_token_normal_user: API token for a root user.
    """
    MyRESTAPI.get_instance().config.version_authorized_show_version = False
    api_client.headers.update({'X-API-Key': random_api_token_normal_user})
    response = api_client.get('/version')
    contents = response.json()

    assert response.status_code == 200
    assert contents == {
        'version': None,
        'python_version': None,
        'internal_dependencies': None,
        'external_dependencies': None
    }
