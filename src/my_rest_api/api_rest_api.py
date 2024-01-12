"""Module that contains the endpoints for the REST API information."""
from sys import version_info as py_version_info
from typing import Annotated

from fastapi import APIRouter, Header, HTTPException
from fastapi import __version__ as fastapi_version
from my_data import __version__ as my_data_version
from my_model import __version__ as my_model_version
from my_model.user_scoped_models import UserRole
from pydantic import __version__ as pydantic_version
from pydantic_settings import __version__ as pydantic_settings_version

from my_rest_api.app_config import AppConfig

from . import __version__ as rest_api_version
from .authentication import get_user_for_api_key
from .model import ErrorModel, Version

api_router = APIRouter()


@api_router.get('/version', responses={403: {'model': ErrorModel}})
def version(x_api_key: Annotated[str | None, Header()] = None) -> Version:
    """Get version information for the REST API.

    Args:
        x_api_key: The API key to use for authentication.

    Returns:
        Version: An instance of the Version class representing the version
            information.

    Raises:
        HTTPException: when the user has no access to the version information.
    """
    version_object = Version(
        version=rest_api_version,
        python_version=(f'{py_version_info.major}.{py_version_info.minor}.' +
                        f'{py_version_info.micro}'),
        internal_dependencies={
            'ds-my-data': my_data_version,
            'ds-my-model': my_model_version
        },
        external_dependencies={
            'fastapi': fastapi_version,
            'pydantic': pydantic_version,
            'pydantic_settings': pydantic_settings_version
        }
    )

    # Get the requesting user
    user = get_user_for_api_key(api_key=x_api_key)

    app_config = AppConfig()
    if user is None:
        # Unauthorized
        if not app_config.version_unauthorized:
            raise HTTPException(
                status_code=403,
                detail=ErrorModel(
                    error='Not authorized to retrieve version information'))

        if not app_config.version_unauthorized_show_version:
            version_object.version = None
        if not app_config.version_unauthorized_show_python_version:
            version_object.python_version = None
        if not app_config.version_unauthorized_show_internal_libraries:
            version_object.internal_dependencies = None
        if not app_config.version_unauthorized_show_external_libraries:
            version_object.external_dependencies = None
    if user and user.role == UserRole.USER:
        # Normal user
        if not app_config.version_authorized_show_version:
            version_object.version = None
        if not app_config.version_authorized_show_python_version:
            version_object.python_version = None
        if not app_config.version_authorized_show_internal_libraries:
            version_object.internal_dependencies = None
        if not app_config.version_authorized_show_external_libraries:
            version_object.external_dependencies = None

    return version_object
