"""Module that contains the endpoints for the Tag resource."""

from typing import Annotated

from fastapi import APIRouter, Header, Query, Request, Response, Path
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
    link_header_string = crud_operations.get_link_header_string(
        str(request.url),
        pagination)
    if link_header_string:
        response.headers['Link'] = link_header_string

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


@api_router.put("/tags/{title}")
def update(
    title: Annotated[str, Path()],
    new_tag: APITagIn,
    x_api_token: Annotated[str | None, Header()] = None
) -> list[APITag]:
    """Update a tag by replacing the object.

    Args:
        title: the title of the tag to update.
        new_tag: the new tag object to place
        x_api_token: the API token.

    Returns:
        The updated tag.
    """
    return crud_operations.update(
        updated_model=new_tag,
        flt=[Tag.title == title],
        api_token=x_api_token)