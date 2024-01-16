"""Tests for the `MyRESTAPI` class."""

from my_rest_api.my_rest_api import MyRESTAPI


def test_singleton() -> None:
    """Test if the MyRESTAPI class is a singleton."""
    api1 = MyRESTAPI.get_instance()
    api2 = MyRESTAPI.get_instance()
    assert api1 is api2
