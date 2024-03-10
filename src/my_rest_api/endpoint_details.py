"""Module with default values for endpoints."""

from typing import Any

from .model import APIError

ResponsesDict = dict[int | str, dict[str, Any]]

# Generic details

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
    },
}

# Authentication

authentication_responses: ResponsesDict = {
    403: {
        'description': (
            'Authentication failed. The given credentials are incorrect.'
        ),
        'model': APIError,
        'content': {
            'application/json': {'example': {'error': 'Authentication failed'}}
        },
    },
    **default_responses,
}
