"""Module with exceptions for My REST API."""

from typing import Any


class MyRESTAPIError(Exception):
    """Base class for exceptions in this module."""

    __error_code__: int = 500

    def __init__(
        self,
        message: str,
        *args: list[Any],
        **kwargs: dict[Any, Any],
    ) -> None:
        """Initialize the exception.

        Set the status code to the class attribute __error_code__ and the
        message to the provided message. The class attribute can be overwritten
        in subclasses to get more specific status codes.
        """
        self.status_code = self.__error_code__
        self.message = message
        super().__init__(*args, **kwargs)


class PaginationError(MyRESTAPIError):
    """Exception for pagination errors."""

    __error_code__: int = 400


class InvalidPageError(PaginationError):
    """Exception for invalid page numbers."""


class InvalidPageSizeError(PaginationError):
    """Exception for invalid page numbers."""


class SortingError(MyRESTAPIError):
    """Exception for sorting errors."""

    __error_code__: int = 400


class InvalidSortFieldError(SortingError):
    """Exception for invalid sort fields."""


class FilterError(MyRESTAPIError):
    """Exception for filter errors."""

    __error_code__: int = 400


class InvalidFilterError(FilterError):
    """Exception for invalid filters."""


class InvalidFilterFieldError(FilterError):
    """Exception for invalid filter fields."""


class InvalidFilterOperatorError(FilterError):
    """Exception for invalid filter operators."""


class InvalidFilterValueTypeError(FilterError):
    """Exception for invalid value types."""


class ResourceCRUDOperationsError(MyRESTAPIError):
    """Exception for resource CRUD API router generator errors."""

    __error_code__: int = 500


class InvalidContextAttributeError(ResourceCRUDOperationsError):
    """Exception for invalid context attributes."""


class NoResourcesFoundError(MyRESTAPIError):
    """Exception for no resources found."""

    __error_code__: int = 404


class PasswordIncorrectError(MyRESTAPIError):
    """Exception for incorrect password."""

    __error_code__: int = 422
