"""Dependencies for the API endpoints.

These dependencies can be injected into the FastAPI endpoints by adding them
as arguments to the endpoint function. For example:

    @api_router.get('/version')
    def version(version: Version = Depends(version_dependency)) -> Version:
        ...
"""

from my_data.my_data import MyData

from .app_config import AppConfig
from .my_rest_api import MyRESTAPI

global_my_data = MyData()


def my_data_object() -> MyData:
    """Return the MyData object from the global MyRESTAPI object.

    The MyData object is used to communicate with the persistent data store.

    Returns:
        The global My Data object.
    """
    return MyRESTAPI.get_instance().my_data


def app_config_object() -> AppConfig:
    """Return the AppConfig object from the global MyRESTAPI object.

    The AppConfig object is used to configure the application.

    Returns:
        The global AppConfig object.
    """
    return MyRESTAPI.get_instance().config
