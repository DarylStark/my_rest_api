from fastapi import Request
from fastapi.exceptions import HTTPException
from fastapi.responses import JSONResponse
from pydantic import BaseModel


async def custom_http_exception_handler(
        request: Request,  # pylint: disable=unused-argument
        exc: HTTPException) -> JSONResponse:
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
    content = exc.detail
    if isinstance(exc.detail, BaseModel):
        content = exc.detail.model_dump()

    return JSONResponse(
        status_code=exc.status_code,
        content=content
    )
