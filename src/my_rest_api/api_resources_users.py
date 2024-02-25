"""Module that contains the endpoints for the User resource."""

from typing import Annotated

from fastapi import APIRouter, Header, Query, Request, Response
from my_model import User

from .app_config import AppConfig
from .resource_crud_api_router_generator import ResourceCRUDAPIRouterGenerator

from .model import UserWithoutPassword

api_router = APIRouter()


crud_operations = ResourceCRUDAPIRouterGenerator(
    endpoint='users',
    model=User,
    input_model=UserWithoutPassword,
    output_model=UserWithoutPassword,
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
) -> list[UserWithoutPassword]:
    """Get all the users."""
    pagination, resources = crud_operations.retrieve(
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
