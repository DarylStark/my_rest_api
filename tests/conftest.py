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
from my_rest_api.app import app
from my_rest_api.app_config import AppConfig
from my_rest_api.my_rest_api import MyRESTAPI


def test_filename() -> str:
    """Return the filename of the test data file.

    Returns:
        The filename of the test data file.
    """
    return os.path.join(os.path.dirname(__file__), 'test_data.json')


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
