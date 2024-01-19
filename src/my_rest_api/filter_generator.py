"""Module with filter generators."""

from typing import Type, TypeVar, Generic, Any
from sqlmodel import SQLModel

from sqlalchemy.sql.elements import ColumnElement

from typing import get_args

T = TypeVar('T')


class FilterGenerator(Generic[T]):
    """Class to generate filter."""

    def __init__(
        self,
        model: Type[SQLModel],
        given_filters: dict[str, Any]
    ) -> None:
        """Initialize the class.

        Args:
            model: The model to generate the filter for.
        """
        self._model = model
        self._given_filters = given_filters

    def get_filter(self) -> list[ColumnElement[T]]:
        """Generate the filter.

        Generates all filters for the given model.

        Returns:
            The generated filter.
        """
        filters: list[ColumnElement[T]] = []

        for field_name, field in self._model.model_fields.items():
            given_types = get_args(field.annotation)
            for given_type in given_types:
                if given_type is int:
                    # Add filters for integer
                    if f'{field_name}__gt' in self._given_filters:
                        filters.append(
                            getattr(self._model, field_name) >
                            self._given_filters[f'{field_name}__gt']
                        )
                    if f'{field_name}__lt' in self._given_filters:
                        filters.append(
                            getattr(self._model, field_name) <
                            self._given_filters[f'{field_name}__lt']
                        )
        return filters
