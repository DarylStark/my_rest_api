"""Module with exception handlers for the REST API."""
from fastapi import Request
from fastapi.responses import JSONResponse

from .exceptions import MyRESTAPIError


async def myrestapi_error_handler(
    request: Request, exc: MyRESTAPIError
) -> JSONResponse:
    """Exception handler for MyRESTAPIError exceptions.

    Args:
        request: The incoming request object.
        exc: The raised MyRESTAPIError exception.

    Returns:
        JSONResponse: The JSON response with the appropriate status code and
            content.
    """
    return JSONResponse(
        status_code=exc.status_code,
        content={'error': exc.message},
    )


async def authentication_error_handler(
    request: Request, exc: Exception
) -> JSONResponse:
    """Exception handler for authentication exceptions.

    Args:
        request: The incoming request object.
        exc: The raised exception.

    Returns:
        JSONResponse: The JSON response with the appropriate status code and
            content.
    """
    return JSONResponse(
        status_code=403,
        content={'error': 'Authentication failed'},
    )


async def authorization_error_handler(
    request: Request, exc: Exception
) -> JSONResponse:
    """Exception handler for authorization exceptions.

    Args:
        request: The incoming request object.
        exc: The raised exception.

    Returns:
        JSONResponse: The JSON response with the appropriate status code and
            content.
    """
    return JSONResponse(
        status_code=401,
        content={'error': 'Authorization failed'},
    )
