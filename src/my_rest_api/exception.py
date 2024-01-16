"""Module for custom exceptions."""


class MyRESTAPIException(Exception):
    """Base class for all exceptions in this module."""


class PermissionDeniedException(MyRESTAPIException):
    """Exception raised when a user has insufficient permissions."""
