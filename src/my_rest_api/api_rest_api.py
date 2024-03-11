"""Module that contains the endpoints for the REST API information."""

from fastapi import APIRouter

from . import __version__ as rest_api_version
from .local_endpoint_details import description_version
from .model import Version

api_router = APIRouter()


@api_router.get(
    '/version',
    **description_version,
)
def version() -> Version:
    """Get version information for the REST API.

    Can be retrieved without logging in.

    Returns:
        Version: An instance of the Version class representing the version
            information.
    """
    return Version(version=rest_api_version)
