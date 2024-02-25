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


class InvalidFilterError(FilterError):
    """Exception for invalid filters."""


class InvalidFilterFieldError(FilterError):
    """Exception for invalid filter fields."""


class InvalidFilterOperatorError(FilterError):
    """Exception for invalid filter operators."""


class ResourceCRUDAPIRouterGeneratorError(MyRESTAPIError):
    """Exception for resource CRUD API router generator errors."""


class InvalidContextAttributeError(ResourceCRUDAPIRouterGeneratorError):
    """Exception for invalid context attributes."""
