"""Module that contains the endpoints for the APIToken resource.

In contrary to the other resources, the APIToken resource does not have a
Update and Delete endpoint. This is because the tokens are managed by the
authentication service and not by this server.
"""

from typing import Annotated

from fastapi import APIRouter, Header, Path, Query, Request, Response
from my_model import APIToken

from my_rest_api.exceptions import NoResourcesFoundError

from .app_config import AppConfig
from .generic_endpoint_details import default_responses
from .local_endpoint_details import (
    description_api_tokens_delete,
    description_api_tokens_retrieve,
    description_api_tokens_retrieve_by_id,
)
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
    resource_uri='api_tokens',
)


@api_router.get(
    '/api_tokens',
    name='API Tokens - Retrieve',
    status_code=200,
    responses=default_responses,
    **description_api_tokens_retrieve,
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


@api_router.get(
    '/api_tokens/{id}',
    name='API Tokens - Retrieve by id',
    status_code=200,
    responses=default_responses,
    **description_api_tokens_retrieve_by_id,
)
def retrieve_by_id(
    id: int,
    x_api_token: Annotated[str | None, Header()] = None,
) -> APITokenResource:
    """Get a specific API token.

    Args:
        id: the token ID.
        x_api_token: the API token.

    Returns:
        The given API token.

    Raises:
        NoResourcesFoundError: if the API token is not found.
    """
    _, resources = crud_operations.retrieve(api_token=x_api_token, id=id)
    if len(resources) == 0:
        raise NoResourcesFoundError(message='Item not found')
    return resources[0]


@api_router.delete(
    '/api_tokens/{apitoken_id}',
    name='API Tokens - Delete',
    status_code=200,
    responses=default_responses,
    **description_api_tokens_delete,
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
