from abc import ABC, abstractmethod
from collections.abc import Iterable
from typing import TypeVar, Any

T = TypeVar('T')


class FilterSpecification(ABC):

    @abstractmethod
    def is_satisfied(self, item: Any) -> bool:
        pass

    def __and__(self, other):
        return AndSpecification(self, other)

    def __or__(self, other):
        return OrSpecification(self, other)

    def __invert__(self):
        return NotSpecification(self)


class AndSpecification(FilterSpecification):
    __slots__ = ('__specifications',)

    def __init__(self, *specifications: FilterSpecification):
        self.__specifications = specifications

    def is_satisfied(self, item: Any) -> bool:
        return all((specification.is_satisfied(item)
                    for specification in self.__specifications))


class OrSpecification(FilterSpecification):
    __slots__ = ('__specifications',)

    def __init__(self, *specifications: FilterSpecification):
        self.__specifications = specifications

    def is_satisfied(self, item: Any) -> bool:
        return any((specification.is_satisfied(item)
                    for specification in self.__specifications))


class NotSpecification(FilterSpecification):
    __slots__ = ('__specification',)

    def __init__(self, specification: FilterSpecification):
        self.__specification = specification

    def is_satisfied(self, item: Any) -> bool:
        return not self.__specification.is_satisfied(item)


def filter_by_specification(
        *,
        specification: FilterSpecification,
        items: Iterable[T],
) -> list[T]:
    return [item for item in items if specification.is_satisfied(item)]
