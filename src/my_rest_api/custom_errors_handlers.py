"""Module with custom error handlers for the REST API."""
from fastapi import Request
from fastapi.exceptions import HTTPException
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from my_data.exceptions import AuthorizationFailed


async def custom_http_exception_handler(
    request: Request,  # pylint: disable=unused-argument
    exc: HTTPException,
) -> JSONResponse:
    """Exception handler for HTTP exceptions.

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
    content = exc.detail
    if isinstance(exc.detail, BaseModel):
        content = exc.detail.model_dump()

    return JSONResponse(status_code=exc.status_code, content=content)


async def custom_authorizationfailed_exception_handler(
    request: Request,  # pylint: disable=unused-argument,
    exc: AuthorizationFailed,  # pylint: disable=unused-argument,
) -> JSONResponse:
    """Exception handler for failed authorization.

    Args:
        request: The incoming request object.
        exc: The raised HTTP exception.

    Returns:
        JSONResponse: The JSON response with the appropriate status code and
            content.
    """
    return JSONResponse(
        status_code=401,
        content={
            'error': 'Not authorized',
        },
    )


async def custom_paginationerror_exception_handler(
    request: Request,  # pylint: disable=unused-argument,
    exc: AuthorizationFailed,  # pylint: disable=unused-argument,
) -> JSONResponse:
    """Exception handler for failed pagination.

    Args:
        request: The incoming request object.
        exc: The raised HTTP exception.

    Returns:
        JSONResponse: The JSON response with the appropriate status code and
            content.
    """
    error = 'Pagination error'
    max_page: int | None = None
    if len(exc.args) == 2:
        error = exc.args[0]
        max_page = exc.args[1]
    return JSONResponse(
        status_code=400, content={'error': error, 'max_page': max_page}
    )


async def custom_sortingerror_exception_handler(
    request: Request,  # pylint: disable=unused-argument,
    exc: AuthorizationFailed,  # pylint: disable=unused-argument,
) -> JSONResponse:
    """Exception handler for failed sorting.

    Args:
        request: The incoming request object.
        exc: The raised HTTP exception.

    Returns:
        JSONResponse: The JSON response with the appropriate status code and
            content.
    """
    error = 'Sorting error'
    allowed_sort_fields: list[str] | None = None
    if len(exc.args) == 2:
        error = exc.args[0]
        allowed_sort_fields = exc.args[1]
    return JSONResponse(
        status_code=400,
        content={'error': error, 'allowed_sort_fields': allowed_sort_fields},
    )


async def custom_filtererror_exception_handler(
    request: Request,  # pylint: disable=unused-argument,
    exc: AuthorizationFailed,  # pylint: disable=unused-argument,
) -> JSONResponse:
    """Exception handler for failed filtering.

    Args:
        request: The incoming request object.
        exc: The raised HTTP exception.

    Returns:
        JSONResponse: The JSON response with the appropriate status code and
            content.
    """
    error = 'Filtering error'
    if len(exc.args) == 1:
        error = exc.args[0]
    return JSONResponse(status_code=400, content={'error': error})


async def custom_noresourcesfounderror_exception_handler(
    request: Request,  # pylint: disable=unused-argument,
    exc: AuthorizationFailed,  # pylint: disable=unused-argument,
) -> JSONResponse:
    """Exception handler for when no resources are found.

    Args:
        request: The incoming request object.
        exc: The raised HTTP exception.

    Returns:
        JSONResponse: The JSON response with the appropriate status code and
            content.
    """
    return JSONResponse(
        status_code=404,
        content={'error': 'No resources found that match the criteria.'},
    )
