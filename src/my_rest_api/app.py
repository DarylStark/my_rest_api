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

from fastapi import FastAPI
from fastapi.exceptions import HTTPException

from my_rest_api.exception import PermissionDeniedException

from .api_authentication import api_router as auth_api_router
from .api_rest_api import api_router as rest_api_router
from .custom_errors_handlers import (
    custom_http_exception_handler, custom_permission_denied_exception_handler)
from .my_rest_api import MyRESTAPI

# Get the configuration
config = MyRESTAPI.get_instance().config

# Configure the database
MyRESTAPI.get_instance().configure_my_data(database_str=config.database_str)

# Create the FastAPI application.
app = FastAPI(
    debug=config.debug,
    title='My REST API')

# Add customer exception handlers
app.exception_handlers[HTTPException] = custom_http_exception_handler
app.exception_handlers[PermissionDeniedException] = \
    custom_permission_denied_exception_handler

# Add the REST API endpoints to the application.
app.include_router(rest_api_router, tags=['REST API information'])
app.include_router(auth_api_router, tags=['Authentication'], prefix='/auth')
