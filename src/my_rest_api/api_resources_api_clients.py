"""Module that contains the endpoints for the APIClient resource."""

from typing import Annotated

from fastapi import APIRouter, Header, Path, Query, Request, Response
from my_model import APIClient

from .app_config import AppConfig
from .generic_endpoint_details import default_responses
from .local_endpoint_details import (
    description_api_clients_create,
    description_api_clients_delete,
    description_api_clients_retrieve,
    description_api_clients_update,
)
from .model import (
    APIClientResource,
    APIClientResourceIn,
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
    model=APIClient,
    input_model=APIClientResourceIn,
    output_model=APIClientResource,
    context_attribute='api_clients',
    needed_scopes=AuthorizationDetails(allow_only_short_lived=True),
    filter_fields=['id', 'app_name', 'app_publisher'],
    sort_fields=['id', 'app_name', 'app_publisher'],
)


@api_router.get(
    '/api_clients',
    name='API Clients - Retrieve',
    status_code=200,
    responses=default_responses,
    **description_api_clients_retrieve,
)
def retrieve(
    request: Request,
    response: Response,
    flt: Annotated[str | None, Query(alias='filter')] = None,
    page_size: int = AppConfig().default_page_size,
    page: int = 1,
    sort: str | None = None,
    x_api_token: Annotated[str | None, Header()] = None,
) -> RetrieveResult[APIClientResource]:
    """Get all the API clients.

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
    '/api_clients',
    name='API Clients - Create',
    status_code=201,
    responses=default_responses,
    **description_api_clients_create,
)
def create(
    resources: list[APIClientResourceIn],
    x_api_token: Annotated[str | None, Header()] = None,
) -> list[APIClientResource]:
    """Create new API clients.

    Args:
        resources: the API clients to create.
        x_api_token: the API token.

    Returns:
        A list with the created tags.
    """
    return crud_operations.create(resources, x_api_token)


@api_router.put(
    '/api_clients/{client_id}',
    name='API Clients - Update',
    status_code=200,
    responses=default_responses,
    **description_api_clients_update,
)
def update(
    client_id: Annotated[int, Path()],
    new_client: APIClientResourceIn,
    x_api_token: Annotated[str | None, Header()] = None,
) -> list[APIClientResource]:
    """Update a API client by replacing the object.

    Args:
        client_id: the client ID of the client to replace.
        new_client: the new client object to place.
        x_api_token: the API token.

    Returns:
        The updated client.
    """
    return crud_operations.update(
        updated_model=new_client,
        flt=[APIClient.id == client_id],  # type: ignore
        api_token=x_api_token,
    )


@api_router.delete(
    '/api_clients/{client_id}',
    name='API Clients - Delete',
    status_code=200,
    responses=default_responses,
    **description_api_clients_delete,
)
def delete(
    client_id: Annotated[int, Path()],
    x_api_token: Annotated[str | None, Header()] = None,
) -> DeletionResult:
    """Delete a client.

    Args:
        client_id: the client ID of the client to delete.
        x_api_token: the API token.

    Returns:
        A instance of the DeletionResult class indicating how many items
        were deleted.
    """
    return crud_operations.delete(
        flt=[APIClient.id == client_id],  # type: ignore
        api_token=x_api_token,
    )
