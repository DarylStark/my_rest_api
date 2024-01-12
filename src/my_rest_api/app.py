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

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from fastapi.exceptions import HTTPException
from pydantic import BaseModel

from .rest_api import api_router as rest_api_router
from .authentication import api_router as auth_api_router
from .app_config import AppConfig

# Get the configuration
config = AppConfig()

# Create the FastAPI application.
app = FastAPI(
    debug=config.debug,
    title='My REST API')


@app.exception_handler(HTTPException)
async def custom_http_exception_handler(
        request: Request, exc: HTTPException):
    """Custom exception handler for HTTP exceptions.

    If the `detail` in `exc` is a Pydantic basemodel, it will be converted to
    a dict using the `model_dump` method. Otherwise, the `detail` will be
    returned as is.

    Args:
        request: The incoming request object.
        exc: The raised HTTP exception.

    Returns:
        JSONResponse: The JSON response with the appropriate status code and
            content.
    """
    # TODO: Move this to a own module.
    content = exc.detail
    if isinstance(exc.detail, BaseModel):
        content = exc.detail.model_dump()

    return JSONResponse(
        status_code=exc.status_code,
        content=content
    )

# Add the REST API endpoints to the application.
app.include_router(rest_api_router, tags=['REST API information'])
app.include_router(auth_api_router, tags=['Authentication'], prefix='/auth')
