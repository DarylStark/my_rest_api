"""Module that contains the endpoints for the Tag resource."""

from typing import Annotated

from fastapi import APIRouter, Header, Query, Request, Response
from my_model import Tag

from .app_config import AppConfig
from .resource_crud_api_router_generator import ResourceCRUDAPIRouterGenerator

api_router = APIRouter()


endpoint_tags = ResourceCRUDAPIRouterGenerator(
    endpoint='tags',
    model=Tag,
    input_model=Tag,
    output_model=Tag,
    context_attribute='tags',
    needed_scopes=('tags.create', 'tags.retrieve',
                   'tags.update', 'tags.delete'),
    filter_fields=[],
    sort_fields=[])


@api_router.get("/tags")
def retrieve(
    request: Request,
    response: Response,
    flt: Annotated[str | None, Query(alias='filter')] = None,
    page_size: int = AppConfig().default_page_size,
    page: int = 1,
    sort: str | None = None,
    x_api_token: Annotated[str | None, Header()] = None
) -> list[Tag]:
    """Get all the tags."""
    pagination, resources = endpoint_tags.retrieve(
        flt,
        page_size,
        page,
        sort,
        x_api_token)

    # Set the Link header
    if pagination:
        link_headers = pagination.get_link_headers(
            str(request.url))
        response.headers['Link'] = 'Link: ' + \
            ', '.join(link_headers)

    return resources
