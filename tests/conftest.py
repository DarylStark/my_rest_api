"""PyTest configuration file.

Contains globally used fixtures for the unit testing.
"""


from pathlib import Path
from typing import Optional

import pytest
from fastapi.testclient import TestClient
from my_model.user_scoped_models import User
from pyotp import random_base32

from my_rest_api.app import app
from my_rest_api.app_config import AppConfig
from my_rest_api.my_rest_api import MyRESTAPI


@pytest.fixture(scope='session')
def temp_data_dir(tmp_path_factory: pytest.TempPathFactory) -> Path:
    """Create a temporary directory for storing temporary data.

    Args:
        tmp_path_factory: The pytest fixture for creating temporary paths.

    Returns:
        The path to the created temporary directory.
    """
    return tmp_path_factory.mktemp("temp_dir")


@pytest.fixture(scope='session')
def random_second_factor() -> str:
    """Fixture for generating a random second factor.

    Returns:
        str: a randomly generated second factor.
    """
    return random_base32()


@pytest.fixture(scope='session')
def api_client(
        random_second_factor: str,  # pylint: disable=redefined-outer-name
        temp_data_dir: Path  # pylint: disable=redefined-outer-name
) -> TestClient:
    """Return a TestClient instance for the FastAPI application.

    Args:
        random_second_factor: a random second factor.
        temp_data_dir: a temporary data directory.

    Returns:
        TestClient: A TestClient instance for the FastAPI application.
    """
    my_rest_api = MyRESTAPI.get_instance()
    my_rest_api.configure_my_data(
        f'sqlite:///{temp_data_dir}test.sqlite',
        create_tables=True,
        create_init_data=True)

    # Make sure that normal_user_2 has 2FA enabled.
    user: Optional[User] = None
    with my_rest_api.data.get_context_for_service_user(
            username='service.user', password='service_password') as context:
        # Retrieve the user.
        user = context.get_user_account_by_username('normal.user.2')

    if user:
        with my_rest_api.data.get_context(user=user) as context:
            # Enable 2FA for the user.
            user.second_factor = random_second_factor
            context.users.update(user)

    return TestClient(app)
