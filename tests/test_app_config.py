"""Test the config model.

Needed to make sure the config model is working properly and the application can
be started.
"""

from my_rest_api.app_config import AppConfig


def test_app_config() -> None:
    """ Test case for AppConfig class.

    This test verifies that the default values of AppConfig are set correctly
    and that the class can be instantiated without errors.
    """
    # Create an instance of AppConfig
    config = AppConfig()

    # Assert that the default values are set correctly
    assert config.debug == False
    assert config.database_str == 'sqlite:///:memory:/'
    assert config.service_user == 'service.user'
    assert config.service_password == 'service_password'
