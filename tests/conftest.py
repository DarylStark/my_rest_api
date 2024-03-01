"""PyTest configuration file.

Contains globally used fixtures for the unit testing.
"""
# pylint: disable=redefined-outer-name
# pylint: disable=too-many-arguments
import os
from contextlib import suppress
from pathlib import Path
from typing import Generator

import pytest
from fastapi.testclient import TestClient
from my_data.data_loader import DataLoader, JSONDataSource
from my_data.my_data_table_creator import MyDataTableCreator
from my_model import TokenModel
from my_rest_api.app import app
from my_rest_api.app_config import AppConfig
from my_rest_api.my_rest_api import MyRESTAPI
from pyotp import random_base32


def test_filename() -> str:
    """Return the filename of the test data file.

    Returns:
        The filename of the test data file.
    """
    return os.path.join(os.path.dirname(__file__), 'test_data.json')


@pytest.fixture(scope='session')
def random_second_factor() -> str:
    """Fixture for generating a random second factor.

    Returns:
        str: a randomly generated second factor.
    """
    return random_base32()


@pytest.fixture(scope='session')
def random_api_token_root() -> str:
    """Fixture to return a API token for a root user.

    Returns:
        str: a random generated API token.
    """
    temp_model = TokenModel()
    return temp_model.set_random_token()


@pytest.fixture(scope='session')
def random_api_token_normal_user() -> str:
    """Fixture to return a API token for a normal user.

    Returns:
        str: a random generated API token.
    """
    temp_model = TokenModel()
    return temp_model.set_random_token()


@pytest.fixture(scope='session')
def random_api_token_normal_user_logout() -> str:
    """Fixture to return a API token for a normal user.

    This fixture is only used by the `logout` test to see if we can logout. We
    use a different token for this test to make sure that the logout is not
    impacting other tests.

    Returns:
        str: a random generated API token.
    """
    temp_model = TokenModel()
    return temp_model.set_random_token()


@pytest.fixture(scope='session')
def random_api_token_normal_user_long_lived() -> str:
    """Fixture to return a long lived API token for a normal user.

    Returns:
        str: a random generated API token.
    """
    temp_model = TokenModel()
    return temp_model.set_random_token()


@pytest.fixture(scope='session')
def cleanup() -> Generator[None, None, None]:
    """Cleanup the environment after the tests are done.

    This fixture is used to cleanup the environment after the tests are done.

    Yields:
        None
    """
    db_str = AppConfig().database_str
    db_path = Path(db_str.replace('sqlite:///', ''))
    with suppress(FileNotFoundError):
        os.remove(db_path)

    yield
    os.remove(db_path)


@pytest.fixture(scope='session')
def api_client(
    cleanup: None,  # pylint: disable=unused-argument
    random_second_factor: str,
) -> TestClient:
    """Return a TestClient instance for the FastAPI application.

    Args:
        cleanup: a cleanup fixture.
        random_second_factor: a random second factor.

    Returns:
        TestClient: A TestClient instance for the FastAPI application.
    """
    my_rest_api = MyRESTAPI.get_instance()

    # Create the tables for the database
    MyDataTableCreator(my_rest_api.my_data).create_db_tables()

    # Import data from the data JSON
    DataLoader(
        my_data_object=my_rest_api.my_data,
        data_source=JSONDataSource(test_filename()),
    ).load()

    return TestClient(app)
