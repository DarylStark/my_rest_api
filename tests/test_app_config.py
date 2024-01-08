"""Test the config model.

Needed to make sure the config model is working properly and the application
can be started.
"""

from my_rest_api.app_config import AppConfig


def test_app_config(app_config: AppConfig) -> None:
    """ Test case for AppConfig class.

    This test verifies that the default values of AppConfig are set correctly
    and that the class can be instantiated without errors.
    """
    # Assert that the default values are set correctly
    assert not app_config.debug
    assert app_config.database_str == 'sqlite:///database.sqlite'
    assert app_config.service_user == 'service.user'
    assert app_config.service_password == 'service_password'
