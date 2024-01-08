"""Test the dependencies module."""

from my_data.my_data import MyData

from my_rest_api.app_config import AppConfig


def test_my_data(app_config: AppConfig, my_data: MyData) -> None:
    """ Test the `my_data` dependency.

    Args:
        app_config: An instance of the AppConfig class.
        my_data: An instance of the MyData class.
    """
    # pylint: disable=protected-access
    assert my_data._database_str == app_config.database_str
