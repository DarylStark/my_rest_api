"""Test for the resource_crud_api_router_generator module."""

from fastapi.testclient import TestClient
from my_model import Tag

from my_rest_api.resource_crud_api_router_generator import \
    ResourceCRUDAPIRouterGenerator
from my_rest_api.exceptions import InvalidContextAttributeError

import pytest


def test_invalid_context_attribute(
        api_client: TestClient,  # noqa: F811
        random_api_token_normal_user: str) -> None:
    """Test that an invalid context attribute raises an error.

    Args:
        api_client: TestClient instance.
        random_api_token_normal_user: str. A random API token for a normal user.
    """
    generator = ResourceCRUDAPIRouterGenerator(
        endpoint='tags',
        model=Tag,
        output_model=Tag,
        context_attribute='invalid',
        needed_scopes=('tags.create', 'tags.retrieve',
                       'tags.update', 'tags.delete'),
        filter_fields=['title'],
        sort_fields=['title'],
    )
    with pytest.raises(InvalidContextAttributeError):
        generator.retrieve(
            None, None, x_api_token=random_api_token_normal_user)
