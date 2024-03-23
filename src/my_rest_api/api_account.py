"""API endpoints for accounts."""
import datetime
from typing import Annotated

from fastapi import APIRouter, Depends, Header
from my_data.authorizer import APIScopeAuthorizer, APITokenAuthorizer
from my_data.my_data import MyData
from my_model.model import TemporaryToken, TemporaryTokenType

from .dependencies import my_data_object
from .exceptions import (
    PasswordIncorrectError,
    SecondFactorAlreadyOnSetValueError,
    TokenIncorrectError,
)
from .generic_endpoint_details import default_responses
from .local_endpoint_details import (
    description_password_reset,
    description_request_change_second_factor_token,
    description_request_password_reset_token,
)
from .model import (
    PasswordResetRequest,
    PasswordResetResult,
    PasswordResetStatus,
    PasswordResetToken,
    PasswordResetTokenRequest,
    SecondFactorChangeRequest,
    SecondFactorChangeRequestResult,
    SecondFactorChangeRequestStatus,
    SecondFactorChangeToken,
    SecondFactorChangeTokenRequest,
)

api_router = APIRouter()


@api_router.post(
    '/request_password_reset_token',
    status_code=200,
    responses=default_responses,
    **description_request_password_reset_token,
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


@api_router.post(
    '/password_reset',
    status_code=200,
    responses=default_responses,
    **description_password_reset,
)
def password_reset(
    password_reset: PasswordResetRequest,
    x_api_token: Annotated[str | None, Header()] = None,
    my_data: MyData = Depends(my_data_object),
) -> PasswordResetResult:
    """Set a new password for the user.

    Args:
        password_reset: the request to reset the password. This includes the
            token and the new password.
        x_api_token: The API token to use for authorization. Should be a short
            lived token or a token with the 'account.reset_password' scope.
        my_data: a global MyData object.

    Returns:
        A dictionary with the reset status.

    Raises:
        TokenIncorrectError: when the given token is wrong.
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

    if auth.user:
        with my_data.get_context(user=auth.user) as context:
            # Check the given token
            token_object = context.temporary_tokens.retrieve(
                flt=[
                    TemporaryToken.token == password_reset.reset_token,  # type: ignore
                    TemporaryToken.token_type  # type: ignore
                    == TemporaryTokenType.PASSWORD_RESET,
                ],
            )
            if (
                not token_object
                or token_object[0].expires < datetime.datetime.now()
            ):
                raise TokenIncorrectError('Invalid token')

            # Set the new password
            auth.user.set_password(password_reset.new_password)

            # Add it to the database
            context.users.update(auth.user)

            # Remove the temporary token object
            context.temporary_tokens.delete(token_object[0])

    # Return the generated token
    return PasswordResetResult(status=PasswordResetStatus.SUCCESS)


@api_router.post(
    '/request_change_second_factor_token',
    status_code=200,
    responses=default_responses,
    **description_request_change_second_factor_token,
)
def request_change_second_factor_token(
    token_request: SecondFactorChangeTokenRequest,
    x_api_token: Annotated[str | None, Header()] = None,
    my_data: MyData = Depends(my_data_object),
) -> SecondFactorChangeToken:
    """Request a token to change the second factor settings.

    Args:
        token_request: the request to change the settings. This includes the
            password of the user.
        x_api_token: The API token to use for authorization. Should be a short
            lived token or a token with the 'account.update_second_factor'
            scope.
        my_data: a global MyData object.

    Returns:
        A dictionary containing the change token.

    Raises:
        PasswordIncorrectError: when the given password is wrong.
    """
    # Authorize the request
    auth = APITokenAuthorizer(
        my_data_object=my_data,
        api_token=x_api_token,
        authorizer=APIScopeAuthorizer(
            required_scopes='account.update_second_factor',
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

    if auth.user and (
        not ((auth.user.second_factor is None) == token_request.new_status)
    ):
        raise SecondFactorAlreadyOnSetValueError(
            'Invalid second factor status'
        )

    # Generate the token object
    return_token = ''
    needed_type = (
        TemporaryTokenType.ENABLE_2FA
        if token_request.new_status
        else TemporaryTokenType.DISABLE_2FA
    )
    if auth.user:
        with my_data.get_context(user=auth.user) as context:
            token_object = TemporaryToken(
                token_type=needed_type,
                expires=datetime.datetime.now() + datetime.timedelta(hours=1),
            )
            return_token = token_object.set_random_token()
            context.temporary_tokens.create(token_object)

    # Return the generated token
    return SecondFactorChangeToken(token=return_token)


@api_router.post(
    '/change_second_factor',
    status_code=200,
    responses=default_responses,
    **description_request_change_second_factor_token,
)
def change_second_factor(
    token_request: SecondFactorChangeRequest,
    x_api_token: Annotated[str | None, Header()] = None,
    my_data: MyData = Depends(my_data_object),
) -> SecondFactorChangeRequestResult:
    """Change the second factor settings for a user.

    Args:
        token_request: the request with a valid token to change the settings.
        x_api_token: The API token to use for authorization. Should be ashort
            lived token or a token with the 'account.update_second_factor'
            scope.
        my_data: a global MyData object.

    Returns:
        A dictionary with the change status.

    Raises:
        TokenIncorrectError: when the given token is wrong.
    """
    # Authorize the request
    auth = APITokenAuthorizer(
        my_data_object=my_data,
        api_token=x_api_token,
        authorizer=APIScopeAuthorizer(
            required_scopes='account.update_second_factor',
            allow_short_lived=True,
        ),
    )
    auth.authorize()

    secret: str | None = None
    if auth.user:
        needed_type = (
            TemporaryTokenType.ENABLE_2FA
            if token_request.new_status
            else TemporaryTokenType.DISABLE_2FA
        )
        with my_data.get_context(user=auth.user) as context:
            token_object = context.temporary_tokens.retrieve(
                flt=[
                    TemporaryToken.token == token_request.reset_token,  # type: ignore
                    TemporaryToken.token_type == needed_type,  # type: ignore
                ],
            )
            if (
                not token_object
                or token_object[0].expires < datetime.datetime.now()
            ):
                raise TokenIncorrectError('Invalid token')

            # Set the new status
            if token_request.new_status:
                secret = auth.user.set_random_second_factor()
            else:
                auth.user.disable_second_factor()

            # Add it to the database
            context.users.update(auth.user)

            # Remove the temporary token object
            context.temporary_tokens.delete(token_object[0])

    # Return the generated token
    return SecondFactorChangeRequestResult(
        status=SecondFactorChangeRequestStatus.SUCCESS,
        secret=secret,
    )
