"""Module with filter generators."""

from abc import ABC, abstractmethod
from typing import Type, TypeVar, Generic, Any
from sqlmodel import SQLModel

from sqlalchemy.sql.elements import ColumnElement

from typing import get_args

T = TypeVar('T')


class BaseFilterGenerator(ABC, Generic[T]):
    """Base filter generator."""

    def __init__(self, model: Type[SQLModel]) -> None:
        """Initialize the class.

        Args:
            model: The model to generate the filter for.
        """
        self._model = model

    @abstractmethod
    def get_filter(
            self,
            field_name: str,
            given_filters: dict[str, Any]) -> list[ColumnElement[T]]:
        """Generate the filter.

        Generates all filters for the given model for specific types.

        Args:
            field_name: the name of the field.
            given_filters: the given filters.

        Returns:
            The generated filters.
        """


class FilterGeneratorInt(BaseFilterGenerator[T]):
    """Filter generator for integers."""

    def get_filter(
            self,
            field_name: str,
            given_filters: dict[str, Any]) -> list[ColumnElement[T]]:
        """Generate the filter.

        Generates all filters for the given model for integers.

        Args:
            field_name: the name of the field.
            given_filters: the given filters.

        Returns:
            The generated filters.
        """
        filters: list[ColumnElement[T]] = []
        possible_filters = {
            field_name:
                getattr(self._model, field_name) ==
                given_filters.get(field_name, 1),
            f'{field_name}__gt':
                getattr(self._model, field_name) >
                given_filters.get(f'{field_name}__gt', 1),
            f'{field_name}__lt':
                getattr(self._model, field_name) <
                given_filters.get(f'{field_name}__lt', 1)
        }

        for flt_name, flt in possible_filters.items():
            if flt_name in given_filters.keys():
                filters.append(flt)

        return filters


class FilterGeneratorStr(BaseFilterGenerator[T]):
    """Filter generator for strings."""

    def get_filter(
            self,
            field_name: str,
            given_filters: dict[str, Any]) -> list[ColumnElement[T]]:
        """Generate the filter.

        Generates all filters for the given model for strings.

        Args:
            field_name: the name of the field.
            given_filters: the given filters.

        Returns:
            The generated filters.
        """
        filters: list[ColumnElement[T]] = []
        possible_filters = {
            field_name:
                getattr(self._model, field_name) ==
                given_filters.get(field_name, ''),
            f'{field_name}__contains':
                getattr(self._model, field_name).like(
                    f'%{given_filters.get(f"{field_name}__contains", "")}%')
        }

        for flt_name, flt in possible_filters.items():
            if flt_name in given_filters.keys():
                filters.append(flt)

        return filters


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
        filter_generators: dict[type, BaseFilterGenerator[T]] = {
            int: FilterGeneratorInt(self._model),
            str: FilterGeneratorStr(self._model)
        }

        for field_name, field in self._model.model_fields.items():
            given_types = get_args(field.annotation) or [field.annotation]
            for given_type in given_types:
                if given_type in filter_generators.keys():
                    filters.extend(
                        filter_generators[given_type].get_filter(
                            field_name, self._given_filters
                        )
                    )
                # if given_type is int:
                #     # Add filters for integers
                #     filters.extend(
                #         FilterGeneratorInt(self._model).get_filter(
                #             field_name, self._given_filters
                #         )
                #     )
                # if given_type is str:
                #     # Add filters for strings
                #     filters.extend(
                #         FilterGeneratorStr(self._model).get_filter(
                #             field_name, self._given_filters
                #         )
                #     )
        return filters
