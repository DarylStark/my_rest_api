"""API endpoints for accounts."""
import datetime
from typing import Annotated

from fastapi import APIRouter, Depends, Header
from my_data.authorizer import APIScopeAuthorizer, APITokenAuthorizer
from my_data.my_data import MyData
from my_model.model import TemporaryToken, TemporaryTokenType

from .dependencies import my_data_object
from .exceptions import PasswordIncorrectError
from .local_endpoint_details import (
    authentication_responses,
    description_login,
)
from .model import (
    PasswordResetToken,
    PasswordResetTokenRequest,
)

api_router = APIRouter()


@api_router.post(
    '/request_password_reset_token',
    status_code=200,
    responses=authentication_responses,
    **description_login,
)
def request_password_reset_token(
    token_request: PasswordResetTokenRequest,
    x_api_token: Annotated[str | None, Header()] = None,
    my_data: MyData = Depends(my_data_object),
) -> PasswordResetToken:
    """Request a token to reset a password.

    Args:
        token_request: the request to reset the password. This includes the
            current password of the user. This password is used to authenticate
            the user and to generate the token.
        x_api_token: The API token to use for authorization. Should be a short
            lived token or a token with the 'account.reset_password' scope.
        my_data: a global MyData object.

    Returns:
        A dictionary containing the reset token.

    Raises:
        PasswordIncorrectError: when the given password is wrong.
    """
    # Authorize the request
    auth = APITokenAuthorizer(
        my_data_object=my_data,
        api_token=x_api_token,
        authorizer=APIScopeAuthorizer(
            required_scopes='account.reset_password',
            allow_short_lived=True,
        ),
    )
    auth.authorize()

    # Check the password for the user
    if auth.user and not auth.user.verify_credentials(
        username=auth.user.username,
        password=token_request.password,
        second_factor=token_request.second_factor,
    ):
        raise PasswordIncorrectError('Invalid password')

    # Generate the token object
    return_token = ''
    if auth.user:
        with my_data.get_context(user=auth.user) as context:
            token_object = TemporaryToken(
                token_type=TemporaryTokenType.PASSWORD_RESET,
                expires=datetime.datetime.now() + datetime.timedelta(hours=1),
            )
            return_token = token_object.set_random_token()
            context.temporary_tokens.create(token_object)

    # Return the generated token
    return PasswordResetToken(token=return_token)
