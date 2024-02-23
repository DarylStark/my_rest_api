"""Module with exceptions for My REST API."""


class MyRESTAPIError(Exception):
    """Base class for exceptions in this module."""


class PaginationError(MyRESTAPIError):
    """Exception for pagination errors."""


class InvalidPageError(PaginationError):
    """Exception for invalid page numbers."""


class InvalidPageSizeError(PaginationError):
    """Exception for invalid page numbers."""


class SortingError(MyRESTAPIError):
    """Exception for sorting errors."""


class InvalidSortFieldError(SortingError):
    """Exception for invalid sort fields."""


class FilterError(MyRESTAPIError):
    """Exception for filter errors."""


class InvalidFilter(FilterError):
    """Exception for invalid filters."""


class InvalidFilterField(FilterError):
    """Exception for invalid filter fields."""
