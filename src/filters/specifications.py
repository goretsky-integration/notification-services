import datetime
from abc import ABC, abstractmethod
from collections.abc import Iterable
from typing import Protocol, TypeVar, Any

T = TypeVar('T')


class HasRejectedByUserNameField(Protocol):
    rejected_by_user_name: str | None


class HasCourierNameField(Protocol):
    courier_name: str | None


class HasOrderTypeField(Protocol):
    type: str | None


class HasReceiptPrintedAtField(Protocol):
    receipt_printed_at: datetime.datetime | None


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


class CanceledOrderBySalesChannelSpecification(FilterSpecification):

    __slots__ = ('__sales_channel_name',)

    def __init__(self, sales_channel_name: str):
        self.__sales_channel_name = sales_channel_name

    def is_satisfied(self, item: HasOrderTypeField) -> bool:
        return item.type == self.__sales_channel_name


class CanceledOrderHasAppointedCourierSpecification(FilterSpecification):

    def is_satisfied(self, item: HasCourierNameField) -> bool:
        return item.courier_name is not None


class CanceledOrderRejectedByUserNameSpecification(FilterSpecification):
    """
    Check if an order was rejected either by a shift manager
    or call center staff.
    """

    def is_satisfied(self, item: HasRejectedByUserNameField) -> bool:
        return item.rejected_by_user_name is not None


class CanceledOrderHasPrintedReceiptSpecification(FilterSpecification):

    def is_satisfied(self, item: HasReceiptPrintedAtField) -> bool:
        return item.receipt_printed_at is not None


def filter_by_specification(
        *,
        specification: FilterSpecification,
        items: Iterable[T],
) -> list[T]:
    return [item for item in items if specification.is_satisfied(item)]
