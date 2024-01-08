"""PyTest configuration file.

Contains globally used fixtures for the unit testing.
"""

import pytest
from fastapi.testclient import TestClient
from my_data.my_data import MyData

from my_rest_api.app import app
from my_rest_api.dependencies import my_data_object
from my_rest_api.app_config import AppConfig


@pytest.fixture(scope='session')
def api_client() -> TestClient:
    """Return a TestClient instance for the FastAPI application.

    Returns:
        TestClient: A TestClient instance for the FastAPI application.
    """
    return TestClient(app)


@pytest.fixture(scope='session')
def app_config() -> AppConfig:
    """Fixture for AppConfig class.

    Returns:
        A instance of the AppConfig class.
    """
    return AppConfig()


@pytest.fixture(scope='session')
def my_data() -> MyData:
    """Return the MyData object.

    The MyData object is used to communicate with the persistent data store.

    Returns:
        The global My Data object.
    """
    return my_data_object()
