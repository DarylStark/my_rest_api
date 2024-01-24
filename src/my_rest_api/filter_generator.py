"""Module with filter generators."""

from abc import ABC, abstractmethod
from typing import Type, TypeVar, Generic, Any
from sqlmodel import SQLModel

from sqlalchemy.sql.elements import ColumnElement

from typing import get_args

import re

T = TypeVar('T', bound=SQLModel)


class TypeFilter(ABC, Generic[T]):
    """Abstract class for type filters."""

    def __init__(
        self,
        model: Type[T],
        field_name: str,
        value: Any,
        flt: str | None = None
    ) -> None:
        """Initialize the class.

        Args:
            model: the model to generate the filter for.
            field_name: the name of the field to generate the filter for.
            value: the value to filter on.
            flt: the filtername.
        """
        self._model = model
        self._field_name = field_name
        self._value = value
        self._flt = flt

    @abstractmethod
    def get_filter(self) -> ColumnElement[T] | None:
        """Generate the filter.

        Returns:
            The generated filter.
        """
        if self._flt is None:
            return getattr(self._model, self._field_name) == self._value
        if self._flt == 'ne':
            return getattr(self._model, self._field_name) != self._value
        return None


class IntFilter(TypeFilter[T]):
    """Class for int filters."""

    def get_filter(self) -> ColumnElement[T] | None:
        """Generate the filter.

        Returns:
            The generated filter.
        """
        super_filters = super().get_filter()
        if super_filters is not None:
            return super_filters

        if self._flt == 'lt':
            return getattr(self._model, self._field_name) < self._value
        if self._flt == 'le':
            return getattr(self._model, self._field_name) <= self._value
        if self._flt == 'gt':
            return getattr(self._model, self._field_name) > self._value
        if self._flt == 'ge':
            return getattr(self._model, self._field_name) >= self._value

        return None


class StrFilter(TypeFilter[T]):
    """Class for string filters."""

    def get_filter(self) -> ColumnElement[T] | None:
        """Generate the filter.

        Returns:
            The generated filter.
        """
        super_filters = super().get_filter()
        if super_filters is not None:
            return super_filters

        if self._flt == 'contains':
            return getattr(
                self._model,
                self._field_name).like(f'%{self._value}%')
        if self._flt == 'notcontains':
            return getattr(
                self._model,
                self._field_name).notlike(f'%{self._value}%')

        return None


class FilterGenerator(Generic[T]):
    """Class to generate filter."""

    registered_type_filters: dict[object, Type[TypeFilter[T]]] = {
        int: IntFilter,
        str: StrFilter,
    }

    def __init__(
        self,
        model: Type[T],
        given_filters: dict[str, Any],
        included_fields: list[str],
    ) -> None:
        """Initialize the class.

        Args:
            model: The model to generate the filter for.
            given_filters: the filters given by the end user.
            included_fields: the fields that are allowed to be filtered on.
        """
        self._model = model
        self._given_filters = given_filters
        self._included_fields = included_fields

    def get_filter(self) -> list[ColumnElement[T]]:
        """Generate the filter.

        Generates all filters for the given model.

        Returns:
            The generated filter.
        """
        filters: list[ColumnElement[T]] = []
        for filter_name, filter_value in self._given_filters.items():
            match = re.match(
                r'^(?P<field_name>\w+)(-(?P<flt>\w+))?$', filter_name)

            if not match:
                continue

            # Get filter specifics
            field_name = match.group('field_name')
            flt = match.group('flt')
            if (field_name not in self._model.model_fields or
                    field_name not in self._included_fields):
                continue

            # Get the field-type
            field = self._model.model_fields[field_name]
            types = ([t for t in get_args(field.annotation) if t]
                     if get_args(field.annotation)
                     else [field.annotation,])

            # Add the needed filters
            for field_type in types:
                if field_type in self.registered_type_filters:
                    filter_class = self.registered_type_filters[field_type]
                    extra_filter = filter_class(
                        self._model,
                        field_name,
                        filter_value,
                        flt).get_filter()
                    if extra_filter is not None:
                        filters.append(extra_filter)

        return filters
