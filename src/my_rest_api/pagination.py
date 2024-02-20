"""Module that contains a class for pagination."""

from math import ceil


class Pagination:
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
        self.total_pages = ceil(total_items / page_size)

    def get_links(
            self,
            base_url: str,
            query_params: dict[str, str]) -> dict[str, str]:
        """Get the links for the pagination.

        Args:
            base_url: the base URL to use for the links.
            query_params: the query parameters to use for the links.

        Returns:
            A dictionary with the links.
        """
        links: dict[str, str] = {}
        return links
