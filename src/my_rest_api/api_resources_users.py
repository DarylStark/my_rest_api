"""Module that contains the endpoints for the User resource."""

from typing import Annotated

from fastapi import APIRouter, Header, Path, Query, Request, Response
from my_model import User

from .app_config import AppConfig
from .model import (
    DeletionResult,
    PaginationResult,
    RetrieveResult,
    UserResource,
    UserResourceIn,
)
from .resource_crud_operations import (
    AuthorizationDetails,
    ResourceCRUDOperations,
)

api_router = APIRouter()


crud_operations = ResourceCRUDOperations(
    model=User,
    input_model=UserResourceIn,
    output_model=UserResource,
    context_attribute='users',
    needed_scopes=AuthorizationDetails(
        create='users.create',
        retrieve='users.retrieve',
        update='users.update',
        delete='users.delete',
    ),
    filter_fields=['id', 'username', 'fullname', 'email'],
    sort_fields=['id', 'username', 'fullname', 'email', 'role', 'created'],
)


@api_router.get('/users', name='Users - Retrieve')
def retrieve(
    request: Request,
    response: Response,
    flt: Annotated[str | None, Query(alias='filter')] = None,
    page_size: int = AppConfig().default_page_size,
    page: int = 1,
    sort: str | None = None,
    x_api_token: Annotated[str | None, Header()] = None,
) -> RetrieveResult[UserResource]:
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


@api_router.post('/users', name='Users - Create')
def create(
    resources: list[UserResourceIn],
    x_api_token: Annotated[str | None, Header()] = None,
) -> list[UserResource]:
    """Create new users.

    Args:
        resources: the users to create.
        x_api_token: the API token.

    Returns:
        A list with the created users.
    """
    return crud_operations.create(resources, x_api_token)


@api_router.put('/users/{user_id}', name='Users - Update')
def update(
    user_id: Annotated[int, Path()],
    new_user: UserResourceIn,
    x_api_token: Annotated[str | None, Header()] = None,
) -> list[UserResource]:
    """Update a user by replacing the object.

    Args:
        user_id: the user ID of the user to replace.
        new_user: the new user object to place.
        x_api_token: the API token.

    Returns:
        The updated user.
    """
    return crud_operations.update(
        updated_model=new_user,
        flt=[User.id == user_id],  # type: ignore
        api_token=x_api_token,
    )


@api_router.delete('/users/{user_id}', name='Users - Delete')
def delete(
    user_id: Annotated[int, Path()],
    x_api_token: Annotated[str | None, Header()] = None,
) -> DeletionResult:
    """Delete a user.

    Args:
        user_id: the tag ID of the user to delete.
        x_api_token: the API token.

    Returns:
        A instance of the DeletionResult class indicating how many items
        were deleted.
    """
    return crud_operations.delete(
        flt=[User.id == user_id],  # type: ignore
        api_token=x_api_token,
    )
