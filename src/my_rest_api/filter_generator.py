"""Module with filter generators."""

from abc import ABC, abstractmethod
from typing import Type, TypeVar, Generic, Any
from sqlmodel import SQLModel

from sqlalchemy.sql.elements import ColumnElement

from typing import get_args

import re

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
        for filter_name in self._given_filters.keys():
            match = re.match(
                r'^(?P<field_name>\w+)(-(?P<flt>\w+))?$', filter_name)
            pass

            if match:
                field_name = match.group('field_name')
                flt = match.group('flt')
                # TODO: get the filters for this field
        return filters
