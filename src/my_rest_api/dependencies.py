"""Dependencies for the API endpoints.

These dependencies can be injected into the FastAPI endpoints by adding them
as arguments to the endpoint function. For example:

    @api_router.get('/version')
    def version(version: Version = Depends(version_dependency)) -> Version:
        ...
"""

from my_data.my_data import MyData

from .app_config import AppConfig

global_my_data = MyData()


def my_data_object(configure: bool = True) -> MyData:
    """Return the MyData object.

    The MyData object is used to communicate with the persistent data store.

    Args:
        configure: specifies if the engine has to be configured if it is not
            yet configured.

    Returns:
        The global My Data object.
    """
    if not global_my_data.database_engine and configure:
        global_my_data.configure(db_connection_str=AppConfig().database_str)
        global_my_data.create_engine(force=False)
    return global_my_data
