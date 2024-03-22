"""Module with filter generators."""

import logging
import re
from abc import ABC, abstractmethod
from typing import Type, get_args

from sqlalchemy.sql.elements import ColumnElement
from sqlmodel import SQLModel

from my_rest_api.exceptions import (
    InvalidFilterError,
    InvalidFilterFieldError,
    InvalidFilterOperatorError,
    InvalidFilterValueTypeError,
)


class TypeFilter(ABC):
    """Abstract class for type filters."""

    def __init__(
        self,
        model: Type[SQLModel],
        field_name: str,
        operator: str,
        value: str,
        field_type: type,
    ) -> None:
        """Initialize the class.

        Args:
            model: the model to generate the filter for.
            field_name: the name of the field to generate the filter for.
            operator: the operator for the filter.
            value: the value to filter on.
            field_type: the type of the field.
        """
        self._model = model
        self._field_name = field_name
        self._value = value
        self._operator = operator
        self._field_type = field_type

    @abstractmethod
    def get_filter(self) -> ColumnElement[bool] | None:
        """Generate the filter.

        Returns:
            The generated filter.
        """
        if self._value != 'null' and not isinstance(
            self._value, self._field_type
        ):
            try:
                self._value = self._field_type(self._value)
            except ValueError as exc:
                raise InvalidFilterValueTypeError(
                    f'Value "{self._value}" was not convertable to '
                    + f'"{self._field_type}"'
                ) from exc

        if self._operator == '==' and self._value != 'null':
            return getattr(self._model, self._field_name) == self._value
        if self._operator == '!=' and self._value != 'null':
            return getattr(self._model, self._field_name) != self._value
        if self._operator == '==' and self._value == 'null':
            return getattr(self._model, self._field_name) == None  # noqa: E711
        if self._operator == '!=' and self._value == 'null':
            return getattr(self._model, self._field_name) != None  # noqa: E711

        return None


class IntFilter(TypeFilter):
    """Class for int filters."""

    def get_filter(self) -> ColumnElement[bool] | None:
        """Generate the filter.

        Returns:
            The generated filter.

        Raises:
            InvalidFilterOperatorError: If the operator is not allowed for
                integers.
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

        raise InvalidFilterOperatorError(
            f'Operator "{self._operator}" is not allowed for integers.'
        )


class StrFilter(TypeFilter):
    """Class for string filters."""

    def get_filter(self) -> ColumnElement[bool] | None:
        """Generate the filter.

        Returns:
            The generated filter.

        Raises:
            InvalidFilterOperatorError: if the operator is not allowed for
                strings.
        """
        self._value = self._value.replace('%', r'\%')
        super_filters = super().get_filter()
        if super_filters is not None:
            return super_filters

        if self._operator == '=contains=':
            return getattr(self._model, self._field_name).like(
                f'%{self._value}%'
            )
        if self._operator == '=!contains=':
            return getattr(self._model, self._field_name).notlike(
                f'%{self._value}%'
            )

        raise InvalidFilterOperatorError(
            f'Operator "{self._operator}" is not allowed for strings.'
        )


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
        self._logger = logging.getLogger('FilterGenerator')
        self._logger.debug('FilterGenerator initialized:')
        self._logger.debug('- Model: %s', self._model)
        self._logger.debug('- Given filters: %s', self._given_filters)

    def get_filters(self) -> list[ColumnElement[bool]]:
        """Generate the filter.

        Generates all filters for the given model.

        Returns:
            The generated filter.

        Raises:
            InvalidFilterError: if the filter is in invalid format.
            InvalidFilterFieldError: if the field is not allowed to be
                filtered on.
        """
        if not self._given_filters:
            return []

        filters: list[ColumnElement[bool]] = []
        given_filters_splitted = self._given_filters.split(',')
        for filter_field in given_filters_splitted:
            match = re.match(
                r'^(?P<field>\w+)(?P<operator>=[!\w]+=|[=<>!]{1,2})'
                + r'(?P<value>.+)$',
                filter_field,
            )

            if not match:
                raise InvalidFilterError(
                    f'Filter "{filter_field}" is in invalid format.'
                )

            # Get filter specifics
            field = str(match.group('field'))
            operator = match.group('operator')
            value = match.group('value')
            if (
                field not in self._model.model_fields
                or field not in self._included_fields
            ):
                raise InvalidFilterFieldError(
                    f'Field "{field}" is not allowed to be filtered on.'
                )

            # Get the field-type
            object_field = self._model.model_fields[field]
            types = (
                [t for t in get_args(object_field.annotation) if t]
                if get_args(object_field.annotation)
                else [
                    object_field.annotation,
                ]
            )

            # Add the needed filters
            for field_type in types:
                if field_type in self.registered_type_filters:
                    self._logger.debug(
                        'Field type for "%s": "%s"', field, field_type
                    )
                    filter_class = self.registered_type_filters[field_type]
                    extra_filter = filter_class(
                        self._model, field, operator, value, field_type
                    ).get_filter()
                    if extra_filter is not None:
                        filters.append(extra_filter)

        return filters
