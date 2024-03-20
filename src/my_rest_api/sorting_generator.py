"""Module that contains a class to generate sorting details."""


from typing import Generic, Type, TypeVar

from pydantic import BaseModel
from sqlalchemy import ColumnElement
from sqlmodel.sql.expression import asc, desc

from .exceptions import InvalidSortFieldError

T = TypeVar('T', bound=BaseModel)


class SortingGenerator(Generic[T]):
    """Generates sorting details for a model."""

    def __init__(
        self,
        model: Type[T],
        allowed_sort_fields: list[str],
        sort_value: str | None,
    ) -> None:
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
    def sort_field(self) -> list[ColumnElement[T]] | None:
        """Return the sort field.

        Returns:
            The field to sort in. This can be given to a retrieval MyData
            function to sort the results.

        Raises:
            InvalidSortFieldError: if the sort field is invalid.
        """
        sort_fields: list[ColumnElement[T]] = []
        if self.sort_value:
            for field in self.sort_value.split(','):
                sort_function = asc
                field_name = field
                if field.startswith('^'):
                    field_name = field[1:]
                    sort_function = desc

                attribute = getattr(self.model, field_name, None)
                allowed = field_name in self.allowed_sort_fields
                if attribute and allowed:
                    sort_fields.append(sort_function(attribute))
                else:
                    raise InvalidSortFieldError(
                        f'Invalid sort field: "{field_name}"'
                    )
        return sort_fields if len(sort_fields) else None
