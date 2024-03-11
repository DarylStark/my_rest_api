"""Module with local default values for endpoints and documentation."""

from .generic_endpoint_details import (
    DocumentationDict,
    ResponsesDict,
    default_responses,
)
from .model import APIError

# API Authentication

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

description_login: DocumentationDict = {
    'summary': 'Login to the REST API.',
    'description': (
        'Login to the REST API using user credentials. This endpoint is used '
        + 'to authenticate a user and to get a token for further '
        + 'authorization. Can only be executed without a valid API token.'
    ),
    'response_description': (
        'The authentication token and a indiciation if the authentication was '
        + 'successful. If the authentication was not successful, the response '
        + 'will contain a error message.'
    ),
}

description_logout: DocumentationDict = {
    'summary': 'Logout from the REST API.',
    'description': (
        'Logout from the API when using a short-lived token. This endpoint is '
        + 'used to invalidate a token and to make sure that the token cannot '
        + 'be used for further authorization. This endpoint is only available '
        + 'with a short-lived token.'
    ),
    'response_description': ('Indicates of the logout was a success.'),
}

description_status: DocumentationDict = {
    'summary': 'Get API token information.',
    'description': ('Get information about the used token.'),
    'response_description': (
        'The token type (either "long-lived" or "short-lived"), the title of '
        + 'the token, the creation date and the expiration date.'
    ),
}

description_refresh: DocumentationDict = {
    'summary': 'Renew a short-lived token.',
    'description': (
        'Renews a short-lived token for the current session. This makes sure '
        + 'the token will not expire soon. If the expiration date of the '
        + 'token is already more then the targer expiration date, the token '
        + 'is not renewed. If the `renew_token` argument is set to `true`, a '
        + 'new token is created. This endpoint is only available with a '
        + 'short-lived token.'
    ),
    'response_description': (
        'The title of the token, the new expiration date and optionally a new '
        + 'token.'
    ),
}
