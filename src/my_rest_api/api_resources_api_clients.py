"""Module that contains the endpoints for the APIClient resource."""

from typing import Annotated

from fastapi import APIRouter, Header, Path, Query, Request, Response
from my_model import APIClient

from .app_config import AppConfig
from .model import APIAPIClient, APIAPIClientIn, DeletionResult
from .resource_crud_operations import (
    AuthorizationDetails,
    ResourceCRUDOperations,
)

api_router = APIRouter()


crud_operations = ResourceCRUDOperations(
    model=APIClient,
    input_model=APIAPIClientIn,
    output_model=APIAPIClient,
    context_attribute='api_clients',
    needed_scopes=AuthorizationDetails(allow_only_short_lived=True),
    filter_fields=['id', 'app_name', 'app_publisher'],
    sort_fields=['id', 'app_name', 'app_publisher'],
)


@api_router.get('/api_clients', name='API Clients - Retrieve')
def retrieve(
    request: Request,
    response: Response,
    flt: Annotated[str | None, Query(alias='filter')] = None,
    page_size: int = AppConfig().default_page_size,
    page: int = 1,
    sort: str | None = None,
    x_api_token: Annotated[str | None, Header()] = None,
) -> list[APIAPIClient]:
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

    return resources


@api_router.post('/api_clients', name='API Clients - Create')
def create(
    resources: list[APIAPIClientIn],
    x_api_token: Annotated[str | None, Header()] = None,
) -> list[APIAPIClient]:
    """Create new API clients.

    Args:
        resources: the API clients to create.
        x_api_token: the API token.

    Returns:
        A list with the created tags.
    """
    return crud_operations.create(resources, x_api_token)


@api_router.put('/api_clients/{client_id}', name='API Clients - Update')
def update(
    client_id: Annotated[int, Path()],
    new_client: APIAPIClientIn,
    x_api_token: Annotated[str | None, Header()] = None,
) -> list[APIAPIClient]:
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


@api_router.delete('/api_clients/{client_id}', name='API Clients - Delete')
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
