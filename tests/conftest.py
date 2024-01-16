"""PyTest configuration file.

Contains globally used fixtures for the unit testing.
"""

from datetime import datetime, timedelta
from pathlib import Path
from typing import Optional

import pytest
from fastapi.testclient import TestClient
from my_model.user_scoped_models import APIToken, TokenModel, User
from pyotp import random_base32

from my_rest_api.app import app
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
def random_api_token_root() -> str:
    """Fixture to return a API token for a root user.

    Returns:
        str: a random generated API token.
    """
    temp_model = TokenModel()
    return temp_model.set_random_token()


@pytest.fixture(scope='session')
def random_api_token_normal_user() -> str:
    """Fixture to return a API token for a onrmal user.

    Returns:
        str: a random generated API token.
    """
    temp_model = TokenModel()
    return temp_model.set_random_token()


@pytest.fixture(scope='session')
def api_client(
        random_second_factor: str,  # pylint: disable=redefined-outer-name
        temp_data_dir: Path,  # pylint: disable=redefined-outer-name
        random_api_token_root: str,  # pylint: disable=redefined-outer-name
        random_api_token_normal_user: str  # pylint: disable=redefined-outer-name
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

    # Make sure that the root user has a short lived API token
    root_user: Optional[User] = None
    with my_rest_api.my_data.get_context_for_service_user(
            username='service.user', password='service_password') as context:
        # Retrieve the user.
        root_user = context.get_user_account_by_username('root')

    if root_user:
        with my_rest_api.my_data.get_context(user=root_user) as context:
            # Set a API token for the user.
            api_token = APIToken(
                api_client=None,
                user=root_user,
                title='test short lived api token',
                expires=datetime.now() + timedelta(seconds=3600))
            api_token.token = random_api_token_root
            context.api_tokens.create(api_token)

    # Make sure that the normal.user.1 user has a short lived API token
    normal_user_1: Optional[User] = None
    with my_rest_api.my_data.get_context_for_service_user(
            username='service.user', password='service_password') as context:
        # Retrieve the user.
        normal_user_1 = context.get_user_account_by_username('normal.user.1')

    if normal_user_1:
        with my_rest_api.my_data.get_context(user=normal_user_1) as context:
            # Set a API token for the user.
            api_token = APIToken(
                api_client=None,
                user=normal_user_1,
                title='test short lived api token',
                expires=datetime.now() + timedelta(seconds=3600))
            api_token.token = random_api_token_normal_user
            context.api_tokens.create(api_token)

    # Make sure that normal_user_2 has 2FA enabled.
    normal_user_2: Optional[User] = None
    with my_rest_api.my_data.get_context_for_service_user(
            username='service.user', password='service_password') as context:
        # Retrieve the user.
        normal_user_2 = context.get_user_account_by_username('normal.user.2')

    if normal_user_2:
        with my_rest_api.my_data.get_context(user=normal_user_2) as context:
            # Enable 2FA for the user.
            normal_user_2.second_factor = random_second_factor
            context.users.update(normal_user_2)

    return TestClient(app)
