"""Module with exceptions for My REST API."""


class MyRESTAPIError(Exception):
    """Base class for exceptions in this module."""


class PaginationError(MyRESTAPIError):
    """Exception for pagination errors."""


class InvalidPageError(PaginationError):
    """Exception for invalid page numbers."""


class InvalidPageSizeError(PaginationError):
    """Exception for invalid page numbers."""
