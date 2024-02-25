"""Module that contains the endpoints for the Tag resource."""

from typing import Annotated

from fastapi import APIRouter, Header, Query, Request, Response
from my_model import Tag

from .app_config import AppConfig
from .model import APITag, APITagIn
from .resource_crud_operations import ResourceCRUDOperations

api_router = APIRouter()


crud_operations = ResourceCRUDOperations(
    model=Tag,
    input_model=APITagIn,
    output_model=APITag,
    context_attribute='tags',
    needed_scopes=('tags.create', 'tags.retrieve',
                   'tags.update', 'tags.delete'),
    filter_fields=['id', 'title', 'color'],
    sort_fields=['id', 'color', 'title'])


@api_router.get("/tags")
def retrieve(
    request: Request,
    response: Response,
    flt: Annotated[str | None, Query(alias='filter')] = None,
    page_size: int = AppConfig().default_page_size,
    page: int = 1,
    sort: str | None = None,
    x_api_token: Annotated[str | None, Header()] = None
) -> list[APITag]:
    """Get all the tags.

    Args:
        request: the request object.
        response: the response object.
        flt: the filter.
        page_size: the page size.
        page: the page.
        sort: the sort.
        x_api_token: the API token.

    Returns:
        A list with the tags.
    """
    pagination, resources = crud_operations.retrieve(
        flt,
        page_size,
        page,
        sort,
        x_api_token)

    # Add the Link header
    if pagination:
        link_headers = pagination.get_link_headers(
            str(request.url))
        response.headers['Link'] = 'Link: ' + \
            ', '.join(link_headers)

    return resources


@api_router.post("/tags")
def create(
    resources: list[APITagIn],
    x_api_token: Annotated[str | None, Header()] = None
) -> list[APITag]:
    """Create new tags.

    Args:
        resources: the tags to create.
        x_api_token: the API token.

    Returns:
        A list with the created tags.
    """
    return crud_operations.create(resources, x_api_token)
