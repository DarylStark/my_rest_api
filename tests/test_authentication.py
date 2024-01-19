"""Tests for the APIAuthentication class."""

import pytest

from my_rest_api.authentication import (APIAuthenticator,
                                        CredentialsAuthenticator)
from my_rest_api.exception import APITokenAuthenticatorAlreadySetException


def test_base_authorizer_class() -> None:
    """Test the base authentication class.

    Test the basic functions of the APIAuthentication class. Because we cannot
    instantiate the abstract class, we instantiate the CredentialsAuthenticator
    class and test it.
    """
    authenticator = CredentialsAuthenticator(
        username='', password='', second_factor='')
    _ = APIAuthenticator(authenticator)

    with pytest.raises(APITokenAuthenticatorAlreadySetException):
        authenticator.set_api_authenticator(APIAuthenticator(authenticator))
