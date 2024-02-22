"""Module that contains a class to generate pagination details."""

from math import ceil
from urllib.parse import parse_qs, urlencode, urlparse, urlunparse

from my_rest_api.app_config import AppConfig
from .exceptions import InvalidPageError, InvalidPageSizeError


class Link:
    """Class for generating link headers."""

    def __init__(self, url: str, rel: str) -> None:
        """Initialize the class.

        Args:
            url: the URL for the link.
            rel: the relation of the link.
        """
        self.url = url
        self.rel = rel

    def __str__(self) -> str:
        """Return the string representation of the link header.

        Returns:
            The URL in string format.
        """
        return f'<{self.url}>; rel="{self.rel}"'

    def update_params(self, params: dict[str, list[str]]) -> 'Link':
        """Set the URL from a string.

        Args:
            params: the parameters to update.

        Returns:
            The updated link. We return the link itself so you can chain this
            command.
        """
        url_components = urlparse(self.url)
        current_params = parse_qs(url_components.query)
        current_params.update(params)
        new_query_string = urlencode(current_params, doseq=True)
        url_components = url_components._replace(query=new_query_string)
        new_url = urlunparse(url_components)
        self.url = new_url
        return self


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
        """Validate the page number.

        Raises:
            InvalidPageError: if the page number is invalid.
        """
        if self.page < 1 or self.page > self.total_pages:
            raise InvalidPageError(
                'Invalid page number.', self.total_pages)

    def validate_page_size(self) -> None:
        """Validate the page size.

        Raises:
            InvalidPageSizeError: if the page size is invalid.
        """
        if self.page_size < 1 or self.page_size > AppConfig().max_page_size:
            raise InvalidPageSizeError(
                'Invalid page size.', AppConfig().max_page_size)

    def validate(self) -> None:
        """Validate the page and page size."""
        self.validate_page()
        self.validate_page_size()

    @property
    def offset(self) -> int:
        """Calculate the resource offset.

        Returns:
            The offset for the given pagination.
        """
        self.validate()
        return (self.page - 1) * self.page_size

    def get_link_headers(self, request_url: str) -> list[str]:
        """Generate the link headers.

        Args:
            request_url: the URL of the request.

        Returns:
            A list of link headers.
        """
        self.validate()

        links: list[str] = [
            str(Link(request_url, 'first').update_params(
                {'page': ['1']})),
            str(Link(request_url, 'last').update_params(
                {'page': [str(self.total_pages)]}))
        ]
        if self.page > 1:
            links.append(str(Link(request_url, 'prev').update_params(
                {'page': [str(self.page - 1)]})))
        if self.total_pages > self.page:
            links.append(str(Link(request_url, 'next').update_params(
                {'page': [str(self.page + 1)]})))

        return links
