"""Test for the resource_crud_api_router_generator module."""

import pytest
from fastapi.testclient import TestClient
from my_model import Tag
from my_rest_api.exceptions import InvalidContextAttributeError
from my_rest_api.pagination_generator import PaginationGenerator
from my_rest_api.resource_crud_operations import (
    AuthorizationDetails,
    ResourceCRUDOperations,
)


def test_retrieve_invalid_context_attribute(
    api_client: TestClient,  # pylint: disable=unused-argument
) -> None:
    """Test that an invalid context attribute raises an error on retrieval.

    Args:
        api_client: TestClient instance. Only imported to create the db.
    """
    operations = ResourceCRUDOperations(
        model=Tag,
        input_model=Tag,
        output_model=Tag,
        context_attribute='invalid',
        needed_scopes=AuthorizationDetails(
            create='tags.create',
            retrieve='tags.retrieve',
            update='tags.update',
            delete='tags.delete',
        ),
        filter_fields=['title'],
        sort_fields=['title'],
    )
    with pytest.raises(InvalidContextAttributeError):
        operations.retrieve(api_token='pabq1d533eMucNPr5pHPuDMqxKRw1SE0')


def test_get_link_header_string_without_pagination(
    api_client: TestClient,  # pylint: disable=unused-argument
) -> None:
    """Test if we get None when we get link headers without pagination.

    Args:
        api_client: TestClient instance. Only imported to create the db.
    """
    operations = ResourceCRUDOperations(
        model=Tag,
        input_model=Tag,
        output_model=Tag,
        context_attribute='invalid',
        needed_scopes=AuthorizationDetails(
            create='tags.create',
            retrieve='tags.retrieve',
            update='tags.update',
            delete='tags.delete',
        ),
        filter_fields=['title'],
        sort_fields=['title'],
    )
    assert (
        operations.get_link_header_string(
            request_url='http://localhost', pagination=None
        )
        is None
    )


def test_get_link_header_string_with_pagination(
    api_client: TestClient,  # pylint: disable=unused-argument
) -> None:
    """Test if we get None when we get link headers without pagination.

    Args:
        api_client: TestClient instance. Only imported to create the db.
    """
    operations = ResourceCRUDOperations(
        model=Tag,
        input_model=Tag,
        output_model=Tag,
        context_attribute='invalid',
        needed_scopes=AuthorizationDetails(
            create='tags.create',
            retrieve='tags.retrieve',
            update='tags.update',
            delete='tags.delete',
        ),
        filter_fields=['title'],
        sort_fields=['title'],
    )

    pagination = PaginationGenerator(10, 5, 500)

    link_headers = operations.get_link_header_string(
        request_url='http://localhost', pagination=pagination
    )
    assert link_headers is not None
    assert link_headers.startswith('Link: ')
    assert 'rel="first"' in link_headers
    assert 'rel="last"' in link_headers
    assert 'rel="next"' in link_headers
    assert 'rel="prev"' in link_headers
