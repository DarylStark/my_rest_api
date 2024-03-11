"""Module with generic default values for endpoints."""

from typing import Any

from .model import APIError

ResponsesDict = dict[int | str, dict[str, Any]]

default_responses: ResponsesDict = {
    400: {'description': 'A parameter is invalid.', 'model': APIError},
    401: {
        'description': (
            'Authorization failed. This usually means that the'
            + 'user is not authorized to access the resource, or that the '
            + 'user is not authenticated.'
        ),
        'model': APIError,
        'content': {
            'application/json': {'example': {'error': 'Authorization failed'}}
        },
    },
    404: {
        'description': 'Requested resouces was not found.',
        'model': APIError,
        'content': {
            'application/json': {'example': {'error': 'Resource not found'}}
        },
    },
    500: {
        'description': 'Server error',
        'model': APIError,
        'content': {
            'application/json': {'example': {'error': 'Internal server error'}}
        },
    },
}
