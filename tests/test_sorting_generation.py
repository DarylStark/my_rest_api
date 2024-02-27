"""Tests for the Sorting Generation module."""

import pytest
from my_model import User
from my_rest_api.exceptions import InvalidSortFieldError
from my_rest_api.sorting_generator import SortingGenerator
from sqlalchemy import ColumnElement


@pytest.mark.parametrize(
    'field, expected_field',
    [
        ('id', User.id),
        ('username', User.username),
        ('fullname', User.fullname),
    ],
)
def test_sorting_generator_field(
    field: str, expected_field: ColumnElement[User]
):
    """Test the sorting field.

    Args:
        field: the field to sort on.
        expected_field: the expected field to sort on.
    """
    sorting_generator = SortingGenerator(
        model=User,
        allowed_sort_fields=['id', 'username', 'fullname'],
        sort_value=field,
    )
    assert sorting_generator.sort_field is expected_field


def test_sorting_generator_invalid_field():
    """Test the sorting field with an invalid field."""
    sorting_generator = SortingGenerator(
        model=User,
        allowed_sort_fields=['id', 'username', 'fullname'],
        sort_value='invalid',
    )
    with pytest.raises(InvalidSortFieldError):
        _ = sorting_generator.sort_field


def test_sorting_generator_non_existing_field():
    """Test the sorting field with a non existing field."""
    sorting_generator = SortingGenerator(
        model=User,
        allowed_sort_fields=['id', 'username', 'fullname'],
        sort_value='non_existing',
    )
    with pytest.raises(InvalidSortFieldError):
        _ = sorting_generator.sort_field
