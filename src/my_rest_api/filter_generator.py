"""Module with filter generators."""

import re
from abc import ABC, abstractmethod
from typing import Any, Type, get_args

from sqlalchemy.sql.elements import ColumnElement
from sqlmodel import SQLModel

from my_rest_api.exceptions import InvalidFilter, InvalidFilterField


class TypeFilter(ABC):
    """Abstract class for type filters."""

    def __init__(
        self,
        model: Type[SQLModel],
        field_name: str,
        operator: str,
        value: Any
    ) -> None:
        """Initialize the class.

        Args:
            model: the model to generate the filter for.
            field_name: the name of the field to generate the filter for.
            operator: the operator for the filter.
            value: the value to filter on.
        """
        self._model = model
        self._field_name = field_name
        self._value = value
        self._operator = operator

    @abstractmethod
    def get_filter(self) -> ColumnElement[bool] | None:
        """Generate the filter.

        Returns:
            The generated filter.
        """
        if self._operator == '==':
            return getattr(self._model, self._field_name) == self._value
        if self._operator == '!=':
            return getattr(self._model, self._field_name) != self._value
        return None


class IntFilter(TypeFilter):
    """Class for int filters."""

    def get_filter(self) -> ColumnElement[bool] | None:
        """Generate the filter.

        Returns:
            The generated filter.
        """
        super_filters = super().get_filter()
        if super_filters is not None:
            return super_filters

        if self._operator == '<':
            return getattr(self._model, self._field_name) < self._value
        if self._operator == '<=':
            return getattr(self._model, self._field_name) <= self._value
        if self._operator == '>':
            return getattr(self._model, self._field_name) > self._value
        if self._operator == '>=':
            return getattr(self._model, self._field_name) >= self._value

        return None


class StrFilter(TypeFilter):
    """Class for string filters."""

    def get_filter(self) -> ColumnElement[bool] | None:
        """Generate the filter.

        Returns:
            The generated filter.
        """
        super_filters = super().get_filter()
        if super_filters is not None:
            return super_filters

        if self._operator == '=contains=':
            return getattr(
                self._model,
                self._field_name).like(f'%{self._value}%')
        if self._operator == '=!contains=':
            return getattr(
                self._model,
                self._field_name).notlike(f'%{self._value}%')

        return None


class FilterGenerator:
    """Class to generate filter."""

    registered_type_filters: dict[object, Type[TypeFilter]] = {
        int: IntFilter,
        str: StrFilter,
    }

    def __init__(
        self,
        model: Type[SQLModel],
        given_filters: str | None,
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

    def get_filters(self) -> list[ColumnElement[bool]]:
        """Generate the filter.

        Generates all filters for the given model.

        Returns:
            The generated filter.
        """
        if not self._given_filters:
            return []

        filters: list[ColumnElement[bool]] = []
        given_filters_splitted = self._given_filters.split(',')
        for filter_field in given_filters_splitted:
            match = re.match(
                r'^(?P<field>\w+)(?P<operator>=[!\w]+=|[=<>!]{1,2})(?P<value>.+)$',
                filter_field)

            if not match:
                raise InvalidFilter(
                    f'Filter "{filter_field}" is in invalid format.')

            # Get filter specifics
            field = str(match.group('field'))
            operator = match.group('operator')
            value = match.group('value')
            if (field not in self._model.model_fields or
                    field not in self._included_fields):
                raise InvalidFilterField(
                    f'Field "{field}" is not allowed to be filtered on.')

            # Get the field-type
            object_field = self._model.model_fields[field]
            types = ([t for t in get_args(object_field.annotation) if t]
                     if get_args(object_field.annotation)
                     else [object_field.annotation,])

            # Add the needed filters
            for field_type in types:
                if field_type in self.registered_type_filters:
                    filter_class = self.registered_type_filters[field_type]
                    extra_filter = filter_class(
                        self._model,
                        field,
                        operator,
                        value).get_filter()
                    if extra_filter is not None:
                        filters.append(extra_filter)

        return filters
