"""Module that contains the endpoints for user management."""

from typing import Annotated

from fastapi import APIRouter, Depends, Header, Request, Response
from fastapi.exceptions import HTTPException
from my_data.authorizer import APIScopeAuthorizer, APITokenAuthorizer
from my_data.my_data import MyData
from my_model import User

from my_rest_api.app_config import AppConfig
from my_rest_api.filter_generator import FilterGenerator
from my_rest_api.pagination_generator import PaginationGenerator

from .dependencies import my_data_object
from .model import SortError, UserWithoutPassword

from .sorting_generator import SortingGenerator

api_router = APIRouter()


@api_router.get('/users/')
def retrieve(
        request: Request,
        response: Response,
        page_size: int = AppConfig().default_page_size,
        page: int = 1,
        sort: str | None = None,
        x_api_token: Annotated[str | None, Header()] = None,
        my_data: MyData = Depends(my_data_object)
) -> list[UserWithoutPassword]:
    """Retrieve a list of users.

    Returns a list of users that the logged on user is allowed to see.

    Args:
        request: the request object.
        response: a response object to alter the webservers response.
        page_size: the number of items to return in a page.
        page: the page number to return.
        sort: the field to sort by.
        x_api_token: the API token to use for authentication.
        my_data: a global MyData object.

    Returns:
        A list of selected users.

    Raises:
        HTTPException: if the user gives a invalid sort field.
    """
    auth = APITokenAuthorizer(
        my_data_object=my_data,
        api_token=x_api_token,
        authorizer=APIScopeAuthorizer(
            required_scopes=['users.retrieve'],
            allow_short_lived=True))
    auth.authorize()

    user_list: list[UserWithoutPassword] = []
    if auth.user:
        # Parse the given filters
        filter_generator = FilterGenerator(
            model=User,
            given_filters=dict(request.query_params),
            included_fields=['id', 'username', 'fullname', 'email'])
        filters = filter_generator.get_filters()

        # Parse the given sort field
        sorting_generator = SortingGenerator(
            model=User,
            allowed_sort_fields=[
                'id', 'username',
                'fullname', 'email',
                'role', 'created'],
            sort_value=sort)

        with my_data.get_context(user=auth.user) as context:
            # Get the max number of resources and vlidate pagination
            resource_count = context.users.count(filters)
            pagination = PaginationGenerator(
                page_size=page_size,
                page=page,
                total_items=resource_count)
            pagination.validate()

            # Get the resources for this page
            resources = context.users.retrieve(
                flt=filters,
                max_items=page_size,
                start=pagination.offset,
                sort=sorting_generator.sort_field)
            user_list = [UserWithoutPassword(**user.model_dump())
                         for user in resources]

            # Add the link headers
            link_headers = pagination.get_link_headers(str(request.url))
            response.headers['Link'] = 'Link: ' + ', '.join(link_headers)

    return user_list
