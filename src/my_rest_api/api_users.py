"""Module that contains the endpoints for user management."""

from math import ceil
from typing import Annotated

from fastapi import APIRouter, Depends, Header, Request, Response
from fastapi.exceptions import HTTPException
from my_data.authorizer import APIScopeAuthorizer, APITokenAuthorizer
from my_data.my_data import MyData
from my_model import User

from my_rest_api.app_config import AppConfig
from my_rest_api.filter_generator import FilterGenerator

from .dependencies import my_data_object
from .model import PaginationError, SortError, UserWithoutPassword

from urllib.parse import urljoin, urlencode, urlparse, urlunparse, parse_qs

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
        x_api_token: the API token to use for authentication.
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

    # Set sorting
    # TODO: Create something to make sorting work
    allowed_sort_list = ['id', 'username',
                         'fullname', 'email', 'role', 'created']
    sort_field = None
    if sort:
        if getattr(User, sort, None) and sort in allowed_sort_list:
            sort_field = getattr(User, sort)
        else:
            raise HTTPException(400, detail=SortError(
                message='Invalid sort field',
                allowed_sort_fields=allowed_sort_list
            ))

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

            # TODO: Create something to make the pagination work
            #
            # Code to parse a URL with new arguments
            #
            #   ```python
            #   url_components = urlparse(str(request.url))
            #   params = parse_qs(url_components.query)
            #   params.update({'next_variable': 10})
            #   query_string = urlencode(params, doseq=True)
            #   url_components = url_components._replace(query=query_string)
            #   new_url = urlunparse(url_components)
            #   ```

            # Get the resources for this page
            resources = context.users.retrieve(
                flt=filters,
                max_items=page_size,
                start=(page - 1) * page_size,
                sort=sort_field)
            user_list = [UserWithoutPassword(**user.model_dump())
                         for user in resources]

            # Add the `Link` header
            links: list[str] = [
                f'<{request.url}?page=1>; rel=first',
                f'<{request.url}?page={page_count}>; rel=last'
            ]
            if page_count > page:
                links.append(f'<{request.url}?page={page + 1}>; rel=next')
            if page > 1:
                links.append(f'<{request.url}?page={page - 1}>; rel=prev')

            response.headers['Link'] = 'Link: ' + ', '.join(links)

            # TODO: Nice error when no resources are found
    return user_list
