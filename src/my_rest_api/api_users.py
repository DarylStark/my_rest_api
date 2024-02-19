"""Module that contains the endpoints for user management."""

from math import ceil
from typing import Annotated

from fastapi import APIRouter, Depends, Header, Request
from fastapi.exceptions import HTTPException
from my_data.authorizer import APIScopeAuthorizer, APITokenAuthorizer
from my_data.my_data import MyData
from my_model import User

from my_rest_api.app_config import AppConfig
from my_rest_api.filter_generator import FilterGenerator

from .dependencies import my_data_object
from .model import PaginationError, UserWithoutPassword

api_router = APIRouter()


@api_router.get('/users/')
def retrieve(
        request: Request,
        page_size: int = AppConfig().default_page_size,
        page: int = 1,
        x_api_token: Annotated[str | None, Header()] = None,
        my_data: MyData = Depends(my_data_object)
) -> list[UserWithoutPassword]:
    """Retrieve a list of users.

    Returns a list of users that the logged on user is allowed to see.

    Args:
        request: The request object.
        x_api_token: The API token to use for authentication.
        my_data: a global MyData object.

    Returns:
        A list of selected users.
    """
    auth = APITokenAuthorizer(
        my_data_object=my_data,
        api_token=x_api_token,
        authorizer=APIScopeAuthorizer(
            required_scopes=['users.retrieve'],
            allow_short_lived=True))
    auth.authorize()

    # TODO: Sorting

    user_list: list[UserWithoutPassword] = []
    if auth.user:
        # Check the given page size
        if page_size > AppConfig().max_page_size:
            raise HTTPException(400, detail=PaginationError(
                message='Page size too large.'
            ))

        # Parse the given filters
        filter_generator = FilterGenerator(
            model=User,
            given_filters=dict(request.query_params),
            included_fields=['id', 'username', 'fullname', 'email'])
        filters = filter_generator.get_filters()

        with my_data.get_context(user=auth.user) as context:
            # Get the max number of resources
            resource_count = context.users.count(filters)
            page_count = ceil(resource_count / page_size)
            if page > page_count or page < 1:
                raise HTTPException(400, detail=PaginationError(
                    message='Invalid page number.',
                    max_page=page_count))

            # Get the resources for this page
            resources = context.users.retrieve(
                filters, max_items=page_size, start=(page - 1) * page_size)
            user_list = [UserWithoutPassword(**user.model_dump())
                         for user in resources]

            # TODO: Add the `Link` header
            # TODO: Nice error when no resources ar found
    return user_list
