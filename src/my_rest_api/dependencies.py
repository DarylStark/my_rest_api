"""Dependencies for the API endpoints.

These dependencies can be injected into the FastAPI endpoints by adding them
as arguments to the endpoint function. For example:

    @api_router.get('/version')
    def version(version: Version = Depends(version_dependency)) -> Version:
        ...
"""

import logging

from my_data.my_data import MyData

from .my_rest_api import MyRESTAPI

global_my_data = MyData()


def my_data_object() -> MyData:
    """Return the MyData object from the global MyRESTAPI object.

    The MyData object is used to communicate with the persistent data store.

    Returns:
        The global My Data object.
    """
    logger = logging.getLogger('my_data_object')
    logger.debug('Requesting MyData object.')
    return MyRESTAPI.get_instance().my_data
