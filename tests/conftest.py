"""PyTest configuration file.

Contains globally used fixtures for the unit testing.
"""


import pytest
from fastapi.testclient import TestClient
from my_data.my_data import MyData

from my_rest_api.app import app
from my_rest_api.app_config import AppConfig
from my_rest_api.dependencies import my_data_object


@pytest.fixture(scope='session')
def app_config() -> AppConfig:
    """Fixture for AppConfig class.

    Returns:
        A instance of the AppConfig class.
    """
    return AppConfig()


@pytest.fixture(scope='session')
def api_client() -> TestClient:
    """Return a TestClient instance for the FastAPI application.

    Returns:
        TestClient: A TestClient instance for the FastAPI application.
    """
    my_data_obj = my_data_object(configure=False)
    my_data_obj.configure('sqlite:///:memory:')
    my_data_obj.create_engine()
    my_data_obj.create_db_tables()
    my_data_obj.create_init_data()
    return TestClient(app)
