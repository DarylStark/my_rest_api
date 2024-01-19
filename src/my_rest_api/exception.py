"""Module for custom exceptions."""


class MyRESTAPIException(Exception):
    """Base class for all exceptions in this module."""


class PermissionDeniedException(MyRESTAPIException):
    """Exception raised when a user has insufficient permissions."""


class APITokenAuthorizerAlreadySetException(MyRESTAPIException):
    """Exception raised when the API token authorizer is already set."""


class APITokenAuthenticatorAlreadySetException(MyRESTAPIException):
    """Exception raised when the API token authenticator is already set."""


class APIAuthenticationFailed(MyRESTAPIException):
    """Exception raised when the API authentication fails."""
