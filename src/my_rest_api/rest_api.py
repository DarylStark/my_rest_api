"""Module that contains the endpoints for the REST API information."""
from sys import version_info as py_version_info

from fastapi import APIRouter
from fastapi import __version__ as fastapi_version
from pydantic import __version__ as pydantic_version

from . import __version__ as rest_api_version
from .model import Version
from .config import Settings

api_router = APIRouter()


@api_router.get('/version')
def version() -> Version:
    """Get version information for the REST API.

    Returns:
        Version: An instance of the Version class representing the version
            information.
    """
    return Version(
        version=rest_api_version,
        python_version=(f'{py_version_info.major}.{py_version_info.minor}.' +
                        f'{py_version_info.micro}'),
        external_dependencies={
            'fastapi': fastapi_version,
            'pydantic': pydantic_version
        }
    )


@api_router.get('/config')
def config() -> Settings:
    return Settings()
