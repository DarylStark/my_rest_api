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

from .rest_api import api_router as rest_api_router
from .app_config import AppConfig

# Get the configuration
config = AppConfig()

# Create the FastAPI application.
app = FastAPI(debug=True)

# Add the REST API endpoints to the application.
app.include_router(rest_api_router, tags=['REST API information'])
