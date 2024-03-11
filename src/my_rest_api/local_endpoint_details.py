"""Module with local default values for endpoints."""

from .generic_endpoint_details import ResponsesDict, default_responses
from .model import APIError

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
