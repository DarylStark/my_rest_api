"""Module that contains the endpoints for user management."""

from typing import Annotated, Optional

from fastapi import APIRouter, Depends, Header
from my_data.my_data import MyData
from my_model.user_scoped_models import User
from sqlalchemy import ColumnElement

from .authorization import APITokenAuthorizer, LoggedOnAuthorizer
from .dependencies import my_data_object
from .model import UserWithoutPassword

api_router = APIRouter()


@api_router.get('/users/')
def retrieve(
        user_id: Optional[int] = None,
        user_id__lt: Optional[int] = None,
        user_id__le: Optional[int] = None,
        user_id__gt: Optional[int] = None,
        user_id__ge: Optional[int] = None,
        username: Optional[str] = None,
        username__contains: Optional[str] = None,
        fullname: Optional[str] = None,
        fullname__contains: Optional[str] = None,
        email: Optional[str] = None,
        email__contains: Optional[str] = None,
        x_api_token: Annotated[str | None, Header()] = None,
        my_data: MyData = Depends(my_data_object)
) -> list[UserWithoutPassword]:
    """Retrieve a list of users.

    Returns a list of users that the logged on user is allowed to see.

    Args:
        user_id: filter on the user_id field.
        user_id__lt: filter on the user_id field, less than.
        user_id__le: filter on the user_id field, less than or equal.
        user_id__gt: filter on the user_id field, greater than.
        user_id__ge: filter on the user_id field, greater than or equal.
        username: filter on the username field.
        username__contains: filter on the username field, using SQL LIKE.
        fullname: filter on the fullname field.
        fullname__contains: filter on the fullname field, using SQL LIKE.
        email: filter on the email field.
        email__contains: filter on the email field, using SQL LIKE.
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

    user_list: list[UserWithoutPassword] = []
    if auth.user:
        flt: list[ColumnElement] = []

        if user_id:
            flt.append(User.id == user_id)
        if user_id__lt:
            flt.append(User.id < user_id__lt)
        if user_id__le:
            flt.append(User.id <= user_id__le)
        if user_id__gt:
            flt.append(User.id > user_id__gt)
        if user_id__ge:
            flt.append(User.id >= user_id__ge)
        if username:
            flt.append(User.username == username)
        if username__contains:
            flt.append(User.username.like(f'%{username__contains}%'))
        if fullname:
            flt.append(User.fullname == fullname)
        if fullname__contains:
            flt.append(User.fullname.like(f'%{fullname__contains}%'))
        if email:
            flt.append(User.email == email)
        if email__contains:
            flt.append(User.email.like(f'%{email__contains}%'))

        with my_data.get_context(user=auth.user) as context:
            user_list = [UserWithoutPassword(**user.model_dump())
                         for user in context.users.retrieve(flt)]

        # TODO: pagiantion

    return user_list
