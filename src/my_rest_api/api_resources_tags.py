"""Module that contains the endpoints for the Tag resource."""

from typing import Annotated

from fastapi import APIRouter, Header, Path, Query, Request, Response
from my_model import Tag

from .app_config import AppConfig
from .endpoint_details import default_responses
from .model import (
    DeletionResult,
    PaginationResult,
    RetrieveResult,
    TagResource,
    TagResourceIn,
)
from .resource_crud_operations import (
    AuthorizationDetails,
    ResourceCRUDOperations,
)

api_router = APIRouter()


crud_operations = ResourceCRUDOperations(
    model=Tag,
    input_model=TagResourceIn,
    output_model=TagResource,
    context_attribute='tags',
    needed_scopes=AuthorizationDetails(
        create='tags.create',
        retrieve='tags.retrieve',
        update='tags.update',
        delete='tags.delete',
    ),
    filter_fields=['id', 'title', 'color'],
    sort_fields=['id', 'color', 'title'],
)


@api_router.get(
    '/tags',
    name='Tags - Retrieve',
    status_code=200,
    responses=default_responses,
)
def retrieve(
    request: Request,
    response: Response,
    flt: Annotated[str | None, Query(alias='filter')] = None,
    page_size: int = AppConfig().default_page_size,
    page: int = 1,
    sort: str | None = None,
    x_api_token: Annotated[str | None, Header()] = None,
) -> RetrieveResult[TagResource]:
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
        flt, page_size, page, sort, x_api_token
    )

    # Add the Link header
    link_header_string = crud_operations.get_link_header_string(
        str(request.url), pagination
    )
    if link_header_string:
        response.headers['Link'] = link_header_string

    return RetrieveResult(
        pagination=PaginationResult(**pagination.__dict__), resources=resources
    )


@api_router.post(
    '/tags',
    name='Tags - Create',
    status_code=201,
    responses=default_responses,
)
def create(
    resources: list[TagResourceIn],
    x_api_token: Annotated[str | None, Header()] = None,
) -> list[TagResource]:
    """Create new tags.

    Args:
        resources: the tags to create.
        x_api_token: the API token.

    Returns:
        A list with the created tags.
    """
    return crud_operations.create(resources, x_api_token)


@api_router.put(
    '/tags/{tag_id}',
    name='Tags - Update',
    status_code=200,
    responses=default_responses,
)
def update(
    tag_id: Annotated[int, Path()],
    new_tag: TagResourceIn,
    x_api_token: Annotated[str | None, Header()] = None,
) -> list[TagResource]:
    """Update a tag by replacing the object.

    Args:
        tag_id: the tag ID of the tag to replace.
        new_tag: the new tag object to place
        x_api_token: the API token.

    Returns:
        The updated tag.
    """
    return crud_operations.update(
        updated_model=new_tag,
        flt=[Tag.id == tag_id],  # type: ignore
        api_token=x_api_token,
    )


@api_router.delete(
    '/tags/{tag_id}',
    name='Tags - Delete',
    status_code=200,
    responses=default_responses,
)
def delete(
    tag_id: Annotated[int, Path()],
    x_api_token: Annotated[str | None, Header()] = None,
) -> DeletionResult:
    """Delete a tag.

    Args:
        tag_id: the tag ID of the tag to delete.
        x_api_token: the API token.

    Returns:
        A instance of the DeletionResult class indicating how many items
        were deleted.
    """
    return crud_operations.delete(
        flt=[Tag.id == tag_id],  # type: ignore
        api_token=x_api_token,
    )
