"""Module with a endpoint generator for the CRUD endpoints for resources.

The classes in this module make sure that we can automatically generate the
endpoints for the CRUD operations for a resource. This is done by creating a
class that can generate the endpoints for a resource. This class can then be
used to generate the endpoints for a resource.

By doing this, we can make sure that the endpoints for the CRUD operations are
consistent and that we can easily add new resources to the API.
"""

from typing import Annotated, Generic, Optional, Tuple, Type, TypeVar

from fastapi import APIRouter, Header, Query, Request, Response
from my_data.authorizer import APIScopeAuthorizer, APITokenAuthorizer
from my_data.resource_manager import ResourceManager
from my_model import MyModel, User
from pydantic import BaseModel
from sqlalchemy.sql.elements import ColumnElement

from my_rest_api.exceptions import InvalidContextAttributeError
from my_rest_api.pagination_generator import PaginationGenerator

from .app_config import AppConfig
from .filter_generator import FilterGenerator
from .my_rest_api import MyRESTAPI
from .sorting_generator import SortingGenerator

Model = TypeVar('Model', bound=MyModel)
OutputModel = TypeVar('OutputModel', bound=BaseModel)


class ResourceCRUDAPIRouterGenerator(Generic[Model, OutputModel]):
    """Base class for Endpoint generators."""

    def __init__(
        self,
        endpoint: str,
        model: Type[Model],
        output_model: Type[OutputModel],
        context_attribute: str,
        needed_scopes: Tuple[str, str, str, str],
        filter_fields: list[str],
        sort_fields: list[str],
    ) -> None:
        """Set the needed values for the endpoints.

        Args:
            endpoint: the endpoint for the resource.
            model: the model for the resource.
            output_model: the output model for the resource.
            context_attribute: the attribute in the context to use for the
                resource.
            needed_scopes: the needed scopes for the resource. Should be a
                tuple with the create, retrieve, update and delete scopes.
            filter_fields: the fields that can be used for filtering.
            sort_fields: the fields that can be used for sorting.
        """
        self._endpoint: str = endpoint
        self._model: Type[Model] = model
        self._output_model: Type[OutputModel] = output_model
        self._context_attribute: str = context_attribute
        self._needed_scopes: Tuple[str, str, str, str] = needed_scopes
        self._filter_fields: list[str] = filter_fields
        self._sort_fields: list[str] = sort_fields

        # Set the MyData object
        self._my_data = MyRESTAPI.get_instance().my_data

    def get_api_router(self) -> APIRouter:
        """Return the API router for the resource.

        This method generates a FastAPI APIRouter for the resource. This router
        contains the endpoints for the CRUD operations for the resource. The
        router can be added to the main FastAPI application to make the
        endpoints available, using the `include_router` method:

        ```python
        app.include_router(api_router)
        ```

        Returns:
            The APIRouter for the resource.
        """
        api_router = APIRouter()

        # Add the CRUD operations

        # Create

        # Retrieve
        api_router.add_api_route(
            f'/{self._endpoint}',
            endpoint=self.retrieve,
            methods=['GET'],
            response_model=list[OutputModel])

        # Update

        # Delete

        # Return the created API router
        return api_router

    def _authorize(
            self,
            api_token: str | None,
            scopes: str | list[str]) -> Optional[User]:
        """Authorize the request.

        This authorize method uses the APITokenAuthorizer to authorize the
        request. It uses the given API token and the given scope to authorize
        the request. If the request is not authorized, an exception is raised.

        Args:
            api_token: the API token to use for authorization.
            scopes: the scope to authorize.

        Returns:
            The authorized user, if any.
        """
        auth = APITokenAuthorizer(
            my_data_object=self._my_data,
            api_token=api_token,
            authorizer=APIScopeAuthorizer(
                required_scopes=scopes,
                allow_short_lived=True))
        auth.authorize()
        return auth.user

    def _get_filters(self, flt: str | None) -> list[ColumnElement[bool]]:
        """Parse the given filter string.

        This method parses the given filter string and returns a list with
        the parsed filters. If the given filter string is None, an empty
        list is returned.

        Args:
            flt: the filter string to parse.

        Returns:
            A dictionary with the parsed filters.
        """
        filter_generator = FilterGenerator(
            model=self._model,
            given_filters=flt,
            included_fields=self._filter_fields)
        filters = filter_generator.get_filters()
        return filters

    def _get_sort_field(
            self,
            sort: str | None) -> ColumnElement[Model] | None:
        """Parse the given sort string.

        Args:
            sort: the sort string to parse.

        Returns:
            A column to sort on.
        """
        sorting_generator = SortingGenerator(
            model=self._model,
            allowed_sort_fields=self._sort_fields,
            sort_value=sort)
        return sorting_generator.sort_field

    def _get_pagination(
        self,
        page_size: int,
        page: int,
        resource_count: int
    ) -> PaginationGenerator:
        """Get the pagination generator.

        Returns a pagination generator for the given values. Will also validate
        if the given page and page_size are valid.

        Args:
            page_size: the number of items to return in a page.
            page: the page number to return.
            resource_count: the total number of items.

        Returns:
            A pagination generator for the given values.
        """
        pagination = PaginationGenerator(
            page_size=page_size,
            page=page,
            total_items=resource_count)
        pagination.validate()
        return pagination

    def retrieve(
            self,
            request: Request,
            response: Response,
            flt: Annotated[str | None, Query(alias='filter')] = None,
            page_size: int = AppConfig().default_page_size,
            page: int = 1,
            sort: str | None = None,
            x_api_token: Annotated[str | None, Header()] = None
    ) -> list[OutputModel]:
        """Retrieve the resources.

        Args:
            request: the request object.
            response: the response object.
            flt: the filter to use.
            page_size: the number of items to return in a page.
            page: the page number to return.
            sort: the field to sort on.
            x_api_token: the API token to use for authorization.

        Returns:
            A list with the retrieved resources.

        Raises:
            InvalidContextAttributeError: if the context attribute is invalid.
        """
        authorized_user = self._authorize(
            x_api_token,
            [self._needed_scopes[1]])
        filters = self._get_filters(flt)
        sort_field = self._get_sort_field(sort)

        # Retrieve the resources
        resources: list[OutputModel] = []
        if authorized_user:
            with self._my_data.get_context(user=authorized_user) as context:
                resource_manager: Optional[ResourceManager[Model]] = \
                    getattr(
                    context,
                    self._context_attribute,
                    None)

                if not resource_manager:
                    raise InvalidContextAttributeError(
                        f'Invalid context attr: "{self._context_attribute}"')

                resource_count = resource_manager.count(filters)
                pagination = self._get_pagination(
                    page_size=page_size,
                    page=page,
                    resource_count=resource_count)

                # Get the resources
                resources_model: list[Model] = resource_manager.retrieve(
                    flt=filters,
                    max_items=page_size,
                    start=pagination.offset,
                    sort=sort_field)

                # If the output model is not the same as the model, we have to
                # convert the resources to the output model.
                resources = [
                    self._output_model(**resource.model_dump())
                    for resource in resources_model]

                # Add the link headers
                if request and response:
                    link_headers = pagination.get_link_headers(
                        str(request.url))
                    response.headers['Link'] = 'Link: ' + \
                        ', '.join(link_headers)

        # Return the resources
        return resources
