"""API endpoints for authentication."""
from fastapi import APIRouter

from .model import AuthenticationDetails

api_router = APIRouter()


@api_router.post('/login')
def login(authentication: AuthenticationDetails) -> dict[str, str]:
    """Login to the REST API.

    Args:
        authentication: authentication details.

    Returns:
        A dictionary containing the authentication token.
    """
    return {}
