"""Module with a class that can perform CRUD operations on resources.

The class in this module can be used to perform CRUD operations on resources.
It can be used to create, retrieve, update and delete resources. It can also
be used to retrieve a list of resources, with pagination, filtering and
sorting.
"""

from typing import Generic, Optional, Type, TypeVar

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
InputModel = TypeVar('InputModel', bound=BaseModel)


class ResourceCRUDOperations(Generic[Model, InputModel, OutputModel]):
    """Class to perform CRUD operations on resources."""

    def __init__(
        self,
        model: Type[Model],
        input_model: Type[InputModel],
        output_model: Type[OutputModel],
        context_attribute: str,
        needed_scopes: tuple[str, str, str, str],
        filter_fields: list[str],
        sort_fields: list[str],
    ) -> None:
        """Set the needed values for the CRUD operators.

        Args:
            endpoint: the endpoint for the resource.
            model: the model for the resource.
            input_model: the input model for the resource.
            output_model: the output model for the resource.
            context_attribute: the attribute in the context to use for the
                resource.
            needed_scopes: the needed scopes for the resource. Should be a
                tuple with the create, retrieve, update and delete scopes.
            filter_fields: the fields that can be used for filtering.
            sort_fields: the fields that can be used for sorting.
        """
        self._model: Type[Model] = model
        self._input_model: Type[InputModel] = input_model
        self._output_model: Type[OutputModel] = output_model
        self._context_attribute: str = context_attribute
        self._needed_scopes: tuple[str, str, str, str] = needed_scopes
        self._filter_fields: list[str] = filter_fields
        self._sort_fields: list[str] = sort_fields

        # Set the MyData object
        self._my_data = MyRESTAPI.get_instance().my_data

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

    def create(
        self,
        resources: list[InputModel],
        api_token: str | None = None
    ) -> list[OutputModel]:
        """Create resources.

        Args:
            resources: the resources to create. These are in the InputModel
                format, so we can omit the fields that we don't want to be
                able to set.
            api_token: the API token to use for authorization.

        Returns:
            A list with the created resources in the given OutputModel. This
            way we can omit the fields that we don't want to return, like
            passwords.

        Raises:
            InvalidContextAttributeError: if the context attribute is invalid.
        """
        authorized_user = self._authorize(
            api_token,
            [self._needed_scopes[0]])

        # Createthe resources
        return_resources: list[OutputModel] = []
        if authorized_user:
            resources_model: list[Model] = []
            with self._my_data.get_context(user=authorized_user) as context:
                resource_manager: Optional[ResourceManager[Model]] = \
                    getattr(
                    context,
                    self._context_attribute,
                    None)

                if not resource_manager:
                    raise InvalidContextAttributeError(
                        f'Invalid context attr: "{self._context_attribute}"')

                # Create the resources
                resources_model = resource_manager.create([
                    self._model(**resource.model_dump())
                    for resource in resources
                ])

            # If the output model is not the same as the model, we have to
            # convert the resources to the output model.
            return_resources = [
                self._output_model(**resource.model_dump())
                for resource in resources_model]

        # Return the resources
        return return_resources

    def retrieve(
            self,
            flt: str | None = None,
            page_size: int = AppConfig().default_page_size,
            page: int = 1,
            sort: str | None = None,
            api_token: str | None = None
    ) -> tuple[PaginationGenerator | None, list[OutputModel]]:
        """Retrieve the resources.

        Args:
            flt: the filter to use.
            page_size: the number of items to return in a page.
            page: the page number to return.
            sort: the field to sort on.
            api_token: the API token to use for authorization.

        Returns:
            A list with the retrieved resources in the given OutputModel. This
            way we can omit the fields that we don't want to return, like
            passwords.

        Raises:
            InvalidContextAttributeError: if the context attribute is invalid.
        """
        # Authorize the request
        authorized_user = self._authorize(
            api_token,
            [self._needed_scopes[1]])

        # Get the filters and sort field
        filters = self._get_filters(flt)
        sort_field = self._get_sort_field(sort)

        # Default return values
        resources: list[OutputModel] = []
        pagination: PaginationGenerator | None = None

        # Retrieve the resources
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

        # Return the resources
        return (pagination, resources)
