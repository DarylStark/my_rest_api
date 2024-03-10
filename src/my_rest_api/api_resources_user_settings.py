"""Module that contains the endpoints for the UserSetting resource."""

from typing import Annotated

from fastapi import APIRouter, Header, Path, Query, Request, Response
from my_model import UserSetting

from .app_config import AppConfig
from .model import (
    DeletionResult,
    PaginationResult,
    RetrieveResult,
    UserSettingResource,
    UserSettingResourceIn,
)
from .resource_crud_operations import (
    AuthorizationDetails,
    ResourceCRUDOperations,
)

api_router = APIRouter()


crud_operations = ResourceCRUDOperations(
    model=UserSetting,
    input_model=UserSettingResourceIn,
    output_model=UserSettingResource,
    context_attribute='user_settings',
    needed_scopes=AuthorizationDetails(
        create='user_settings.create',
        retrieve='user_settings.retrieve',
        update='user_settings.update',
        delete='user_settings.delete',
    ),
    filter_fields=['id', 'setting', 'value'],
    sort_fields=['id', 'setting', 'value'],
)


@api_router.get('/user_settings', name='User Settings - Retrieve')
def retrieve(
    request: Request,
    response: Response,
    flt: Annotated[str | None, Query(alias='filter')] = None,
    page_size: int = AppConfig().default_page_size,
    page: int = 1,
    sort: str | None = None,
    x_api_token: Annotated[str | None, Header()] = None,
) -> RetrieveResult[UserSettingResource]:
    """Get all the user setings.

    Args:
        request: the request object.
        response: the response object.
        flt: the filter.
        page_size: the page size.
        page: the page.
        sort: the sort.
        x_api_token: the API token.

    Returns:
        A list with the user settings.
    """
    pagination, resources = crud_operations.retrieve(
        flt, page_size, page, sort, x_api_token
    )

    # Add the Link header
    link_header_string = crud_operations.get_link_header_string(
        str(request.url), pagination
    )
    if link_header_string:
        response.headers['Link'] = link_header_string

    return RetrieveResult(
        pagination=PaginationResult(**pagination.__dict__), resources=resources
    )


@api_router.post('/user_settings', name='User Settings - Create')
def create(
    resources: list[UserSettingResourceIn],
    x_api_token: Annotated[str | None, Header()] = None,
) -> list[UserSettingResource]:
    """Create new user settings.

    Args:
        resources: the user settings to create.
        x_api_token: the API token.

    Returns:
        A list with the created user settings.
    """
    return crud_operations.create(resources, x_api_token)


@api_router.put(
    '/user_settings/{user_setting_id}', name='User Settings - Update'
)
def update(
    user_setting_id: Annotated[int, Path()],
    net_user_setting: UserSettingResourceIn,
    x_api_token: Annotated[str | None, Header()] = None,
) -> list[UserSettingResource]:
    """Update a user setting by replacing the object.

    Args:
        user_setting_id: the user setting ID of the user setting to delete.
        net_user_setting: the new user setting object to place
        x_api_token: the API token.

    Returns:
        The updated user setting.
    """
    return crud_operations.update(
        updated_model=net_user_setting,
        flt=[UserSetting.id == user_setting_id],  # type: ignore
        api_token=x_api_token,
    )


@api_router.delete(
    '/user_settings/{user_setting_id}', name='User Settings - Delete'
)
def delete(
    user_setting_id: Annotated[int, Path()],
    x_api_token: Annotated[str | None, Header()] = None,
) -> DeletionResult:
    """Delete a user setting.

    Args:
        user_setting_id: the user setting ID of the user setting to delete.
        x_api_token: the API token.

    Returns:
        A instance of the DeletionResult class indicating how many items
        were deleted.
    """
    return crud_operations.delete(
        flt=[UserSetting.id == user_setting_id],  # type: ignore
        api_token=x_api_token,
    )
