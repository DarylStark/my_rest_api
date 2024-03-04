"""Tests for the filter_generator module."""

import pytest
from my_model import User
from my_rest_api.exceptions import (
    InvalidFilterFieldError,
    InvalidFilterOperatorError,
)
from my_rest_api.filter_generator import FilterGenerator


def test_filter_generator_invalid_field() -> None:
    """Test the filter generator for fields that are not included."""
    filter_generator = FilterGenerator(
        model=User, given_filters='username==root', included_fields=['id']
    )
    with pytest.raises(InvalidFilterFieldError):
        _ = filter_generator.get_filters()


def test_filter_generator_non_existing_field() -> None:
    """Test the filter generator for fields that are not in the model."""
    filter_generator = FilterGenerator(
        model=User,
        given_filters='username_wrong==root',
        included_fields=['username_wrong'],
    )
    with pytest.raises(InvalidFilterFieldError):
        _ = filter_generator.get_filters()


def test_filter_generator_int_equals() -> None:
    """Test the filter generator for integers."""
    filter_generator = FilterGenerator(
        model=User, given_filters='id==1', included_fields=['id']
    )
    filters = filter_generator.get_filters()
    assert len(filters) == 1


@pytest.mark.parametrize('filter_name', ['invalid_field', 'invalid_id'])
def test_filter_generator_int_invalid_filters(filter_name: str) -> None:
    """Test the filter generator for invalid filters for integers.

    Args:
        filter_name: the name of the filter to test.
    """
    filter_generator = FilterGenerator(
        model=User, given_filters=f'{filter_name}==1', included_fields=['id']
    )
    with pytest.raises(InvalidFilterFieldError):
        _ = filter_generator.get_filters()


@pytest.mark.parametrize('operator', ['<', '<=', '>', '>=', '!='])
def test_filter_generator_int_operators(operator: str) -> None:
    """Test the filter generator for integers with specific operators.

    Args:
        operator: the name of the operator to test.
    """
    filter_generator = FilterGenerator(
        model=User, given_filters=f'id{operator}1', included_fields=['id']
    )
    filters = filter_generator.get_filters()
    assert len(filters) == 1


def test_filter_generator_str_equals() -> None:
    """Test the filter generator for strings."""
    filter_generator = FilterGenerator(
        model=User,
        given_filters='username==root',
        included_fields=['username'],
    )
    filters = filter_generator.get_filters()
    assert len(filters) == 1


@pytest.mark.parametrize('operator', ['=contains=', '=!contains='])
def test_filter_generator_str_operators(operator: str) -> None:
    """Test the filter generator for strings with specific operators.

    Args:
        operator: the operator to test.
    """
    filter_generator = FilterGenerator(
        model=User,
        given_filters=f'username{operator}root',
        included_fields=['username'],
    )
    filters = filter_generator.get_filters()
    assert len(filters) == 1


@pytest.mark.parametrize(
    'operator',
    [
        '=',
        '=is=',
    ],
)
def test_filter_generator_str_wrong_operator(operator: str) -> None:
    """Test a wrong filter operator for strings.

    Should fail.

    Args:
        operator: the operator to test.
    """
    filter_generator = FilterGenerator(
        model=User,
        given_filters=f'username{operator}root',
        included_fields=['username'],
    )
    with pytest.raises(InvalidFilterOperatorError):
        _ = filter_generator.get_filters()


@pytest.mark.parametrize(
    'operator',
    [
        '=',
        '<>',
    ],
)
def test_filter_generator_int_wrong_operator(operator: str) -> None:
    """Test a wrong filter operator for integers.

    Should fail.

    Args:
        operator: the operator to test.
    """
    filter_generator = FilterGenerator(
        model=User, given_filters=f'id{operator}1', included_fields=['id']
    )
    with pytest.raises(InvalidFilterOperatorError):
        _ = filter_generator.get_filters()
