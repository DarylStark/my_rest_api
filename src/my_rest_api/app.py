"""The `app` object from FastAPI.

This module contains the `app` object from FastAPI. It is used to run the
application. To start the application, you can run the following command:

        uvicorn my_rest_api.app:app

You can add the `--reload` flag to the command to enable auto-reloading of the
application when changes are detected. For example:

        uvicorn my_rest_api.app:app --reload

Every part of the application is imported here. These parts are then added to
the `app` object. This allows the application to be run from a single module.
"""

import logging

from fastapi import FastAPI
from fastapi.exceptions import HTTPException
from my_data.exceptions import AuthorizationFailed

from .api_authentication import api_router as auth_api_router
from .api_resources_api_clients import (
    api_router as api_router_resources_api_clients,
)
from .api_resources_tags import api_router as api_router_resources_tags
from .api_resources_user_settings import (
    api_router as api_router_resources_user_settings,
)
from .api_resources_users import api_router as api_router_resources_users
from .api_rest_api import api_router as rest_api_router
from .app_config import AppConfig
from .custom_errors_handlers import (
    custom_authorizationfailed_exception_handler,
    custom_filtererror_exception_handler,
    custom_http_exception_handler,
    custom_noresourcesfounderror_exception_handler,
    custom_paginationerror_exception_handler,
    custom_sortingerror_exception_handler,
)
from .exceptions import (
    FilterError,
    NoResourcesFoundError,
    PaginationError,
    SortingError,
)

# Configure logging
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
)

# Get the configuration
config = AppConfig()

# Create the FastAPI application.
app = FastAPI(debug=config.debug, title='My REST API')

# Add customer exception handlers
app.exception_handlers[HTTPException] = custom_http_exception_handler
app.exception_handlers[
    AuthorizationFailed
] = custom_authorizationfailed_exception_handler
app.exception_handlers[
    PaginationError
] = custom_paginationerror_exception_handler
app.exception_handlers[SortingError] = custom_sortingerror_exception_handler
app.exception_handlers[FilterError] = custom_filtererror_exception_handler
app.exception_handlers[
    NoResourcesFoundError
] = custom_noresourcesfounderror_exception_handler

# Add the REST API endpoints to the application.
app.include_router(rest_api_router, tags=['REST API information'])
app.include_router(auth_api_router, tags=['Authentication'], prefix='/auth')

# Add the resources endpoints to the application.
app.include_router(
    api_router_resources_tags, tags=['Resources'], prefix='/resources'
)
app.include_router(
    api_router_resources_users, tags=['Resources'], prefix='/resources'
)
app.include_router(
    api_router_resources_user_settings,
    tags=['Resources'],
    prefix='/resources',
)
app.include_router(
    api_router_resources_api_clients, tags=['Resources'], prefix='/resources'
)
