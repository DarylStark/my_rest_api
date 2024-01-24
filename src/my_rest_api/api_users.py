"""Module that contains the endpoints for user management."""

from typing import Annotated

from fastapi import APIRouter, Depends, Header, Request
from my_data.my_data import MyData
from my_model.user_scoped_models import User

from my_rest_api.filter_generator import FilterGenerator

from .authorization import APITokenAuthorizer, LoggedOnAuthorizer
from .dependencies import my_data_object
from .model import UserWithoutPassword

api_router = APIRouter()


@api_router.get('/users/')
def retrieve(
        request: Request,
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
        api_token=x_api_token,
        authorizer=LoggedOnAuthorizer())
    auth.authorize()

    # TODO: Check given scopes
    # TODO: Pagianation
    # TODO: Sorting

    user_list: list[UserWithoutPassword] = []
    if auth.user:
        filter_generator = FilterGenerator[User](
            model=User,
            given_filters=dict(request.query_params),
            included_fields=['username', 'fullname', 'email'])
        filters = filter_generator.get_filters()

        with my_data.get_context(user=auth.user) as context:
            user_list = [UserWithoutPassword(**user.model_dump())
                         for user in context.users.retrieve(filters)]
    return user_list
