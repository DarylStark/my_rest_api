"""Tests for the Sorting Generation module."""

import pytest
from my_model import User
from my_rest_api.exceptions import InvalidSortFieldError
from my_rest_api.sorting_generator import SortingGenerator


def test_sorting_generator_invalid_field() -> None:
    """Test the sorting field with an invalid field."""
    sorting_generator = SortingGenerator(
        model=User,
        allowed_sort_fields=['id', 'username', 'fullname'],
        sort_value='invalid',
    )
    with pytest.raises(InvalidSortFieldError):
        _ = sorting_generator.sort_field


def test_sorting_generator_non_existing_field() -> None:
    """Test the sorting field with a non existing field."""
    sorting_generator = SortingGenerator(
        model=User,
        allowed_sort_fields=['id', 'username', 'fullname'],
        sort_value='non_existing',
    )
    with pytest.raises(InvalidSortFieldError):
        _ = sorting_generator.sort_field
