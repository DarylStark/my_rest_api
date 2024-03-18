"""Module with a class that can perform CRUD operations on resources.

The class in this module can be used to perform CRUD operations on resources.
It can be used to create, retrieve, update and delete resources. It can also
be used to retrieve a list of resources, with pagination, filtering and
sorting.
"""

from typing import Generic, Optional, Type, TypeVar

from my_data.authorizer import (
    APIScopeAuthorizer,
    APITokenAuthorizer,
    ShortLivedTokenAuthorizer,
)
from my_data.context import Context
from my_data.resource_manager import ResourceManager
from my_model import Resource, User
from pydantic import BaseModel
from sqlalchemy.sql.elements import ColumnElement

from my_rest_api.exceptions import (
    InvalidContextAttributeError,
    NoResourcesFoundError,
)
from my_rest_api.model import DeletionResult
from my_rest_api.pagination_generator import PaginationGenerator

from .app_config import AppConfig
from .filter_generator import FilterGenerator
from .my_rest_api import MyRESTAPI
from .sorting_generator import SortingGenerator

Model = TypeVar('Model', bound=Resource)
OutputModel = TypeVar('OutputModel', bound=BaseModel)
InputModel = TypeVar('InputModel', bound=BaseModel)


class AuthorizationDetails(BaseModel):
    """Model to store the authorization details.

    Attributes:
        create: the scope needed to create a resource.
        retrieve: the scope needed to retrieve a resource.
        update: the scope needed to update a resource.
        delete: the scope needed to delete a resource.
        allow_short_lived: if short lives scopes are allowed.
        allow_only_short_lived: if only short lived scopes are allowed. This
            basically disables the use of long lived scopes.
    """

    create: str | None = None
    retrieve: str | None = None
    update: str | None = None
    delete: str | None = None
    allow_short_lived: bool = True
    allow_only_short_lived: bool = False


class ResourceCRUDOperations(Generic[Model, InputModel, OutputModel]):
    """Class to perform CRUD operations on resources."""

    def __init__(
        self,
        model: Type[Model],
        input_model: Type[InputModel],
        output_model: Type[OutputModel],
        context_attribute: str,
        needed_scopes: AuthorizationDetails,
        filter_fields: list[str],
        sort_fields: list[str],
    ) -> None:
        """Set the needed values for the CRUD operators.

        Args:
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
        self._needed_scopes: AuthorizationDetails = needed_scopes
        self._filter_fields: list[str] = filter_fields
        self._sort_fields: list[str] = sort_fields

        # Set the MyData object
        self._my_data = MyRESTAPI.get_instance().my_data

    def _authorize(
        self, api_token: str | None, scopes: str | list[str | None]
    ) -> Optional[User]:
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
        if self._needed_scopes.allow_only_short_lived:
            auth = APITokenAuthorizer(
                my_data_object=self._my_data,
                api_token=api_token,
                authorizer=ShortLivedTokenAuthorizer(),
            )
        else:
            converted_scopes: list[str] = [str(scope) for scope in scopes]
            auth = APITokenAuthorizer(
                my_data_object=self._my_data,
                api_token=api_token,
                authorizer=APIScopeAuthorizer(
                    required_scopes=converted_scopes,
                    allow_short_lived=self._needed_scopes.allow_short_lived,
                ),
            )

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
            included_fields=self._filter_fields,
        )
        filters = filter_generator.get_filters()
        return filters

    def _get_sort_field(self, sort: str | None) -> ColumnElement[Model] | None:
        """Parse the given sort string.

        Args:
            sort: the sort string to parse.

        Returns:
            A column to sort on.
        """
        sorting_generator = SortingGenerator(
            model=self._model,
            allowed_sort_fields=self._sort_fields,
            sort_value=sort,
        )
        return sorting_generator.sort_field

    def _get_pagination(
        self, page_size: int, page: int, resource_count: int
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
            page_size=page_size, page=page, total_items=resource_count
        )
        pagination.validate()
        return pagination

    def _get_resource_manager(
        self, context: Context
    ) -> ResourceManager[Model]:
        """Get the resources from the given context for the given attribute.

        Args:
            context: the context to get the attribute from.

        Returns:
            The attribute from the context.

        Raises:
            InvalidContextAttributeError: if the context attribute is invalid.
        """
        resource_manager: Optional[ResourceManager[Model]] = getattr(
            context, self._context_attribute, None
        )

        if not resource_manager:
            raise InvalidContextAttributeError(
                f'Invalid context attr: "{self._context_attribute}"'
            )

        return resource_manager

    def _convert_model_to_output_model(
        self, models: list[Model]
    ) -> list[OutputModel]:
        """Convert the model to the output model.

        The models that are given by the MyData Context can be different from
        what we have to display in the REST API. This method can be used to
        convert the models to the output model.

        It doesn't check if the given list is in the correct format. If it
        isn't, it might raise an Exception when trying to convert it.

        Args:
            models: the models to convert.

        Returns:
            The output model.
        """
        return [
            self._output_model(**resource.model_dump()) for resource in models
        ]

    def get_link_header_string(
        self, request_url: str, pagination: Optional[PaginationGenerator]
    ) -> Optional[str]:
        """Retrieve the Link header string.

        Args:
            request_url: the URL of the request.
            pagination: the pagination object with the correct details to
                create the Link header string. If this is set to None, the
                method will return None.

        Returns:
            The Link header string if pagination is given. Otherwise None.
        """
        if not pagination:
            return None
        link_headers = pagination.get_link_headers(str(request_url))
        return 'Link: ' + ', '.join(link_headers)

    def create(
        self, resources: list[InputModel], api_token: str | None = None
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
        """
        authorized_user = self._authorize(
            api_token, [self._needed_scopes.create]
        )

        # Createthe resources
        return_resources: list[OutputModel] = []
        if authorized_user:
            resources_model: list[Model] = []
            with self._my_data.get_context(user=authorized_user) as context:
                resource_manager = self._get_resource_manager(context)

                # Create the resources
                resources_model = resource_manager.create(
                    [
                        self._model(**resource.model_dump())
                        for resource in resources
                    ]
                )

            # Convert to the output model
            return_resources = self._convert_model_to_output_model(
                resources_model
            )

        # Return the resources
        return return_resources

    def retrieve(
        self,
        flt: str | None = None,
        page_size: int = AppConfig().default_page_size,
        page: int = 1,
        sort: str | None = None,
        api_token: str | None = None,
        id: int | None = None,
    ) -> tuple[PaginationGenerator | None, list[OutputModel]]:
        """Retrieve the resources.

        Args:
            flt: the filter to use.
            page_size: the number of items to return in a page.
            page: the page number to return.
            sort: the field to sort on.
            id: a specific ID for the object to retrieve.
            api_token: the API token to use for authorization.

        Returns:
            A list with the retrieved resources in the given OutputModel. This
            way we can omit the fields that we don't want to return, like
            passwords.
        """
        # Authorize the request
        authorized_user = self._authorize(
            api_token, [self._needed_scopes.retrieve]
        )

        # Get the filters and sort field
        filters = self._get_filters(flt)
        sort_field = self._get_sort_field(sort)

        if id:
            filters.append(self._model.id == id)  # type: ignore

        # Default return values
        resources: list[OutputModel] = []
        pagination: PaginationGenerator | None = None

        # Retrieve the resources
        if authorized_user:
            with self._my_data.get_context(user=authorized_user) as context:
                resource_manager = self._get_resource_manager(context)

                # Create the pagination
                resource_count = resource_manager.count(filters)
                pagination = self._get_pagination(
                    page_size=page_size,
                    page=page,
                    resource_count=resource_count,
                )

                # Get the resources
                resources_model: list[Model] = resource_manager.retrieve(
                    flt=filters,
                    max_items=page_size,
                    start=pagination.offset,
                    sort=sort_field,
                )

                # Convert to the output model
                resources = self._convert_model_to_output_model(
                    resources_model
                )

        # Return the resources
        return (pagination, resources)

    def update(
        self,
        updated_model: InputModel,
        flt: list[ColumnElement[bool]],
        api_token: str | None = None,
    ) -> list[OutputModel]:
        """Update the resource.

        Args:
            updated_model: the updated model to use.
            flt: the filter to select the resources to update.
            api_token: the API token to use for authorization.

        Returns:
            The updated resource in the given OutputModel. This way we can
            omit the fields that we don't want to return, like passwords.

        Raises:
            NoResourcesFoundError: if no resources are found to update.
        """
        authorized_user = self._authorize(
            api_token, [self._needed_scopes.update]
        )

        # Update the resource
        return_models: list[OutputModel] = []
        if authorized_user:
            with self._my_data.get_context(user=authorized_user) as context:
                resource_manager = self._get_resource_manager(context)

                # Get the resources to update
                resources_to_update = resource_manager.retrieve(flt=flt)

                if len(resources_to_update) == 0:
                    raise NoResourcesFoundError('No resources found to update')

                # Update the resources
                for resource in resources_to_update:
                    for field in updated_model.model_fields:
                        setattr(resource, field, getattr(updated_model, field))

                # Update the resource
                updated_models = resource_manager.update(resources_to_update)
                return_models = self._convert_model_to_output_model(
                    updated_models
                )

        # Return the resource
        return return_models

    def delete(
        self,
        flt: list[ColumnElement[bool]],
        api_token: str | None = None,
    ) -> DeletionResult:
        """Delete resources.

        Does not return anything; there is nothing to return. If something
        goed wrong, a Exception will be raised.

        Args:
            flt: the filter to select the resources to delete.
            api_token: the API token to use for authorization.

        Returns:
            A instance of the DeletionResult class indicating how many items
            were deleted.

        Raises:
            NoResourcesFoundError: if no resources are found to delete.
        """
        authorized_user = self._authorize(
            api_token, [self._needed_scopes.delete]
        )

        # Delete the resources
        deletion_result: list[int] = []
        if authorized_user:
            with self._my_data.get_context(user=authorized_user) as context:
                resource_manager = self._get_resource_manager(context)

                # Get the resources to update
                resources_to_delete = resource_manager.retrieve(flt=flt)

                if len(resources_to_delete) == 0:
                    raise NoResourcesFoundError('No resources found to delete')

                deletion_result = [
                    int(resource.id)
                    for resource in resources_to_delete
                    if resource.id
                ]

                # Delete the resources
                resource_manager.delete(resources_to_delete)

        # Return the result
        return DeletionResult(deleted=deletion_result)
