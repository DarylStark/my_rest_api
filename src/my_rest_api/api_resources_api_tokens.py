"""Module that contains the endpoints for the APIToken resource.

In contrary to the other resources, the APIToken resource does not have a
Update and Delete endpoint. This is because the tokens are managed by the
authentication service and not by this server.
"""

from typing import Annotated

from fastapi import APIRouter, Header, Path, Query, Request, Response
from my_model import APIToken

from .app_config import AppConfig
from .endpoint_details import default_responses
from .model import (
    APITokenResource,
    DeletionResult,
    PaginationResult,
    RetrieveResult,
)
from .resource_crud_operations import (
    AuthorizationDetails,
    ResourceCRUDOperations,
)

api_router = APIRouter()


crud_operations = ResourceCRUDOperations(
    model=APIToken,
    input_model=APITokenResource,
    output_model=APITokenResource,
    context_attribute='api_tokens',
    needed_scopes=AuthorizationDetails(
        retrieve='api_tokens.retrieve',
        delete='api_tokens.delete',
    ),
    filter_fields=['id', 'title', 'api_client_id'],
    sort_fields=['id', 'title', 'created', 'expires'],
)


@api_router.get(
    '/api_tokens',
    name='API Tokens - Retrieve',
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
) -> RetrieveResult[APITokenResource]:
    """Get all the api tokens.

    Args:
        request: the request object.
        response: the response object.
        flt: the filter.
        page_size: the page size.
        page: the page.
        sort: the sort.
        x_api_token: the API token.

    Returns:
        A list with the APITokens.
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


@api_router.delete(
    '/api_tokens/{apitoken_id}',
    name='API Tokens - Delete',
    status_code=200,
    responses=default_responses,
)
def delete(
    apitoken_id: Annotated[int, Path()],
    x_api_token: Annotated[str | None, Header()] = None,
) -> DeletionResult:
    """Delete a API token.

    Args:
        apitoken_id: the API token ID of the token to delete.
        x_api_token: the API token.

    Returns:
        A instance of the DeletionResult class indicating how many items
        were deleted.
    """
    return crud_operations.delete(
        flt=[APIToken.id == apitoken_id],  # type: ignore
        api_token=x_api_token,
    )
