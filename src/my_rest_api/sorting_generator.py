"""Module that contains a class to generate sorting details."""


from typing import Generic, TypeVar, Type

from pydantic import BaseModel
from sqlalchemy import ColumnElement

from .exceptions import InvalidSortFieldError

T = TypeVar('T', bound=BaseModel)


class SortingGenerator(Generic[T]):
    """Generates sorting details for a model."""

    def __init__(
        self,
        model: Type[T],
        allowed_sort_fields: list[str],
        sort_value: str | None,
    ):
        """Initialize the SortingGenerator object.

        Args:
            model: the model to sort.
            allowed_sort_fields: a list of fields that are allowed to be sorted
                on.
            sort_value: the value to sort on. This is usually the value that is
                given by the user. Via the REST API for example.
        """
        self.model: Type[T] = model
        self.allowed_sort_fields: list[str] = allowed_sort_fields
        self.sort_value: str | None = sort_value

    @property
    def sort_field(self) -> ColumnElement[T] | None:
        """Return the sort field.

        Returns:
            The field to sort in. This can be given to a retrieval MyData
            function to sort the results.

        Raises:
            InvalidSortFieldError: if the sort field is invalid.
        """
        sort_field: ColumnElement[T] | None = None
        if self.sort_value:
            attribute = getattr(self.model, self.sort_value, None)
            allowed = self.sort_value in self.allowed_sort_fields
            if attribute and allowed:
                sort_field = attribute
            else:
                raise InvalidSortFieldError(
                    f'Invalid sort field: "{self.sort_value}"',
                    self.allowed_sort_fields,
                )
        return sort_field
