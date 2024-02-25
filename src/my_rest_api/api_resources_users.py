"""Module that contains the endpoints for the User resource."""

from typing import Annotated

from fastapi import APIRouter, Header, Query, Request, Response
from my_model import User

from .app_config import AppConfig
from .model import APIUser, APIUserIn
from .resource_crud_operations import ResourceCRUDOperations

api_router = APIRouter()


crud_operations = ResourceCRUDOperations(
    model=User,
    input_model=APIUserIn,
    output_model=APIUser,
    context_attribute='users',
    needed_scopes=('users.create', 'users.retrieve',
                   'users.update', 'users.delete'),
    filter_fields=['id', 'username', 'fullname', 'email'],
    sort_fields=['id', 'username', 'fullname', 'email', 'role', 'created'])


@api_router.get("/users")
def retrieve(
    request: Request,
    response: Response,
    flt: Annotated[str | None, Query(alias='filter')] = None,
    page_size: int = AppConfig().default_page_size,
    page: int = 1,
    sort: str | None = None,
    x_api_token: Annotated[str | None, Header()] = None
) -> list[APIUser]:
    """Get all the users.

    Args:
        request: the request object.
        response: the response object.
        flt: the filter.
        page_size: the page size.
        page: the page.
        sort: the sort.
        x_api_token: the API token.

    Returns:
        A list with the users.
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


@api_router.post("/users")
def create(
    resources: list[APIUserIn],
    x_api_token: Annotated[str | None, Header()] = None
) -> list[APIUser]:
    """Create new users.

    Args:
        resources: the users to create.
        x_api_token: the API token.

    Returns:
        A list with the created users.
    """
    return crud_operations.create(resources, x_api_token)
