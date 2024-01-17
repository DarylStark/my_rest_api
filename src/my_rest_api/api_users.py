"""Module that contains the endpoints for user management."""

from typing import Annotated

from fastapi import APIRouter, Depends, Header
from my_data.my_data import MyData

from .authentication import APITokenAuthenticator, LoggedOnAuthenticator
from .dependencies import my_data_object
from .model import UserWithoutPassword

api_router = APIRouter()


@api_router.get('/users')
def retrieve(
        x_api_token: Annotated[str | None, Header()] = None,
        my_data: MyData = Depends(my_data_object)
) -> list[UserWithoutPassword]:
    """Retrieve a list of users.

    Returns a list of users that the logged on user is allowed to see.

    Args:
        x_api_token: The API token to use for authentication.
        my_data: a global MyData object.

    Returns:
        A list of selected users.
    """
    auth = APITokenAuthenticator(
        api_token=x_api_token,
        authenticator=LoggedOnAuthenticator)
    auth.authenticate()

    user_list: list[UserWithoutPassword] = []
    if auth.user:
        with my_data.get_context(user=auth.user) as context:
            user_list = [UserWithoutPassword(**user.model_dump())
                         for user in context.users.retrieve()]
    return user_list
