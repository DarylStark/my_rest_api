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

# API Clients

description_api_clients_retrieve: DocumentationDict = {
    'summary': 'Retrieve API clients',
    'description': ('Retrieve all API clients configured by the user.'),
    'response_description': (
        'A list of all API clients configured by the user. Includes the date '
        + 'of creation, the status, the name, published and the callback URL.'
    ),
}

description_api_clients_create: DocumentationDict = {
    'summary': 'Create API clients',
    'description': (
        'Create API clients by giving a list of API clients to create.'
    ),
    'response_description': ('The given API clients that are created.'),
}

description_api_clients_update: DocumentationDict = {
    'summary': 'Update API clients',
    'description': (
        'Update API clients. Specify the unique ID of the client and the new '
        + 'client object.'
    ),
    'response_description': ('The updated API client object.'),
}

description_api_clients_delete: DocumentationDict = {
    'summary': 'Delete API clients',
    'description': (
        'Delete API clients. Specify the unique ID of the client to delete'
    ),
    'response_description': ('A response indicating what IDs are deleted'),
}

# API Tokens

description_api_tokens_retrieve: DocumentationDict = {
    'summary': 'Retrieve API tokens',
    'description': ('Retrieve all API tokens configured by the user.'),
    'response_description': ('A list of all API tokens created by the user'),
}

description_api_tokens_delete: DocumentationDict = {
    'summary': 'Delete API tokens',
    'description': (
        'Delete API tokens. Specify the unique ID of the token to delete'
    ),
    'response_description': ('A response indicating what IDs are deleted'),
}

# Tags

description_tags_retrieve: DocumentationDict = {
    'summary': 'Retrieve tags',
    'description': ('Retrieve all tags configured by the user.'),
    'response_description': (
        'A list of all API tags configured by the user. Includes the title '
        + 'and optionally the color of the tag.'
    ),
}

description_tags_create: DocumentationDict = {
    'summary': 'Create tags',
    'description': ('Create tags by giving a list of tag to create.'),
    'response_description': ('The given tags that are created.'),
}

description_tags_update: DocumentationDict = {
    'summary': 'Update tags',
    'description': (
        'Update tags. Specify the unique ID of the tag and the new '
        + 'tag object.'
    ),
    'response_description': ('The updated tag object.'),
}

description_tags_delete: DocumentationDict = {
    'summary': 'Delete tags',
    'description': ('Delete tags. Specify the unique ID of the tag to delete'),
    'response_description': ('A response indicating what IDs are deleted'),
}


# Users

description_users_retrieve: DocumentationDict = {
    'summary': 'Retrieve users',
    'description': ('Retrieve all users visible for the user.'),
    'response_description': (
        'A list of all API users configured by the user. Includes all the '
        + 'details of the users.'
    ),
}

description_users_create: DocumentationDict = {
    'summary': 'Create users',
    'description': ('Create users by giving a list of users to create.'),
    'response_description': ('The given users that are created.'),
}

description_users_update: DocumentationDict = {
    'summary': 'Update users',
    'description': (
        'Update users. Specify the unique ID of the user and the new '
        + 'user object.'
    ),
    'response_description': ('The updated users object.'),
}

description_users_delete: DocumentationDict = {
    'summary': 'Delete users',
    'description': (
        'Delete users. Specify the unique ID of the user to delete.'
    ),
    'response_description': ('A response indicating what IDs are deleted'),
}
