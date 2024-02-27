"""Test for the resource_crud_api_router_generator module."""

import pytest
from fastapi.testclient import TestClient
from my_model import Tag

from my_rest_api.exceptions import InvalidContextAttributeError
from my_rest_api.resource_crud_operations import \
    ResourceCRUDOperations


def test_retrieve_invalid_context_attribute(
        api_client: TestClient,  # pylint: disable=unused-argument
        random_api_token_normal_user: str) -> None:
    """Test that an invalid context attribute raises an error on retrieval.

    Args:
        api_client: TestClient instance. Only imported to create the db.
        random_api_token_normal_user: str. A random API token for a normal
            user.
    """
    operations = ResourceCRUDOperations(
        model=Tag,
        input_model=Tag,
        output_model=Tag,
        context_attribute='invalid',
        needed_scopes=('tags.create', 'tags.retrieve',
                       'tags.update', 'tags.delete'),
        filter_fields=['title'],
        sort_fields=['title'],
    )
    with pytest.raises(InvalidContextAttributeError):
        operations.retrieve(api_token=random_api_token_normal_user)