"""Tests for the filter_generator module."""

import pytest
from my_model.user_scoped_models import User
from my_rest_api.filter_generator import FilterGenerator


def test_filter_generator_invalid_field():
    """Test the filter generator for fields that are not included."""
    filter_generator = FilterGenerator(
        model=User,
        given_filters={
            'username': 'root'
        },
        included_fields=['id'])
    filters = filter_generator.get_filters()
    assert len(filters) == 0


def test_filter_generator_non_existing_field():
    """Test the filter generator for fields that are not in the model."""
    filter_generator = FilterGenerator(
        model=User,
        given_filters={
            'username_wrong': 'root'
        },
        included_fields=['username_wrong'])
    filters = filter_generator.get_filters()
    assert len(filters) == 0


def test_filter_generator_int_equals():
    """Test the filter generator for integers."""
    filter_generator = FilterGenerator(
        model=User,
        given_filters={
            'id': 1
        },
        included_fields=['id'])
    filters = filter_generator.get_filters()
    assert len(filters) == 1


@pytest.mark.parametrize('filter_name', [
    'id-invaild', '-id'
])
def test_filter_generator_int_invalid_filters(filter_name: str):
    """Test the filter generator for invalid filters for integers.

    Args:
        filter_name: the name of the filter to test.
    """
    filter_generator = FilterGenerator(
        model=User,
        given_filters={
            filter_name: 1
        },
        included_fields=['id'])
    filters = filter_generator.get_filters()
    assert len(filters) == 0


@pytest.mark.parametrize('filter_name', [
    'lt', 'le', 'gt', 'ge', 'ne'
])
def test_filter_generator_int_operators(filter_name: str):
    """Test the filter generator for integers with specific operators.

    Args:
        filter_name: the name of the filter to test.
    """
    filter_generator = FilterGenerator(
        model=User,
        given_filters={
            f'id-{filter_name}': 1
        },
        included_fields=['id'])
    filters = filter_generator.get_filters()
    assert len(filters) == 1


def test_filter_generator_str_equals():
    """Test the filter generator for strings."""
    filter_generator = FilterGenerator(
        model=User,
        given_filters={
            'username': 'root'
        },
        included_fields=['username'])
    filters = filter_generator.get_filters()
    assert len(filters) == 1


@pytest.mark.parametrize('filter_name', [
    'username-invaild', '-username'
])
def test_filter_generator_str_invalid_filters(filter_name: str):
    """Test the filter generator for invalid filters for string.

    Args:
        filter_name: the name of the filter to test.
    """
    filter_generator = FilterGenerator(
        model=User,
        given_filters={
            filter_name: 1
        },
        included_fields=['username'])
    filters = filter_generator.get_filters()
    assert len(filters) == 0


@pytest.mark.parametrize('filter_name', [
    'contains', 'notcontains'
])
def test_filter_generator_str_operators(filter_name: str):
    """Test the filter generator for strings with specific operators.

    Args:
        filter_name: the name of the filter to test.
    """
    filter_generator = FilterGenerator(
        model=User,
        given_filters={
            f'username-{filter_name}': 'root'
        },
        included_fields=['username'])
    filters = filter_generator.get_filters()
    assert len(filters) == 1
