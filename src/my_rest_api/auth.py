"""API endpoints for authentication."""
from fastapi import APIRouter, Depends
from my_data.my_data import MyData

from .dependencies import my_data_object
from .model import AuthenticationDetails

api_router = APIRouter()


@api_router.post('/login')
def login(
    authentication: AuthenticationDetails,
    my_data: MyData = Depends(my_data_object)
) -> dict[str, str]:
    """Login to the REST API.

    Args:
        authentication: authentication details.

    Returns:
        A dictionary containing the authentication token.
    """
    raise NotImplementedError
