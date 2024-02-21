"""Module that contains a class to generate pagination details."""

from math import ceil

from my_rest_api.app_config import AppConfig
from .exceptions import InvalidPageError, InvalidPageSizeError


class PaginationGenerator:
    """Class for pagination."""

    def __init__(
            self,
            page_size: int,
            page: int,
            total_items: int) -> None:
        """Initialize the class.

        Args:
            page_size: the number of items on a page.
            page: the page number to retrieve.
            total_items: the total number of items.
        """
        self.page_size = page_size
        self.page = page
        self.total_items = total_items

        # Calculate the total pages
        self.total_pages = ceil(total_items / page_size)

    def validate_page(self) -> None:
        """Validate the page number."""
        if self.page < 1 or self.page > self.total_pages:
            raise InvalidPageError(
                'Invalid page number.', self.total_pages)

    def validate_page_size(self) -> None:
        """Validate the page size."""
        if self.page_size < 1 or self.page_size > AppConfig().max_page_size:
            raise InvalidPageSizeError(
                'Invalid page size.', AppConfig().max_page_size)

    def validate(self) -> None:
        """Validate the page and page size."""
        self.validate_page()
        self.validate_page_size()

    @property
    def offset(self) -> int:
        """Calculate the resource offset."""
        self.validate()
        return (self.page - 1) * self.page_size
