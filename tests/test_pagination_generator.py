"""Tests for the PaginationGenerator class."""
import pytest

from my_rest_api.exceptions import InvalidPageError, InvalidPageSizeError
from my_rest_api.pagination_generator import PaginationGenerator, Link


def test_pagination_validator_valid_page() -> None:
    """Test the pagination validator.

    Test if the pagination validator works with a valid page number.
    """

    # Test the pagination generator
    generator = PaginationGenerator(
        page_size=10,
        page=1,
        total_items=100)
    assert generator.total_pages == 10
    generator.validate_page()


def test_pagination_validator_invalid_page() -> None:
    """Test the pagination validator.

    Test if the pagination validator works with a invalid page number.
    """
    # Test the pagination generator with an invalid page
    generator = PaginationGenerator(
        page_size=10,
        page=11,
        total_items=100)
    assert generator.total_pages == 10
    with pytest.raises(InvalidPageError):
        generator.validate_page()
    with pytest.raises(InvalidPageError):
        generator.validate()


def test_pagination_validator_valid_page_size() -> None:
    """Test the pagination validator.

    Test if the pagination validator works with a valid page size.
    """
    # Test the pagination generator with a valid page size
    generator = PaginationGenerator(
        page_size=10,
        page=1,
        total_items=100)
    generator.validate_page_size()


def test_pagination_validator_invalid_page_size() -> None:
    """Test the pagination validator.

    Test if the pagination validator works with a invalid page size.
    """
    # Test the pagination generator with an invalid page size
    generator = PaginationGenerator(
        page_size=10000,
        page=1,
        total_items=100)
    with pytest.raises(InvalidPageSizeError):
        generator.validate_page_size()
    with pytest.raises(InvalidPageSizeError):
        generator.validate()


@pytest.mark.parametrize("page_size, page, expected_offset", [
    (10, 1, 0),
    (10, 2, 10),
    (20, 1, 0),
    (20, 2, 20),
    (3, 1, 0),
    (3, 10, 27)
]
)
def test_pagination_validator_offset(
        page_size: int,
        page: int,
        expected_offset: int) -> None:
    """Test the pagination validator.

    Test if the pagination validator works with a valid page size.

    Args:
        page: the page number.
        expected_offset: the expected offset.
    """
    # Test the pagination generator with a valid page size
    generator = PaginationGenerator(
        page_size=page_size,
        page=page,
        total_items=100)
    assert generator.offset == expected_offset


@pytest.mark.parametrize("url, new_var, new_value, expected_url", [
    ("http://test.com/", "page", "2", "http://test.com/?page=2"),
    ("http://test.com/?page=1", "page", "2", "http://test.com/?page=2"),
    ("http://test.com/?page=5", "page", "10", "http://test.com/?page=10"),
]
)
def test_pagination_validator_links(
        url: str,
        new_var: str,
        new_value: str,
        expected_url: str) -> None:
    """Test the pagination validator.

    Test if the pagination validator works with a valid page size.

    Args:
        url: the url to test.
        new_var: the new variable to add.
        new_value: the new value to add.
        expected_url: the expected url.
    """
    # Test the pagination generator with a valid page size
    link = Link(url, 'first')
    link.update_params({new_var: new_value})
    assert expected_url in str(link)
