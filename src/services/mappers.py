import collections
from typing import Iterable, TypeVar, Protocol, TypeAlias, Any, DefaultDict
from uuid import UUID

__all__ = (
    'group_by_unit_id',
    'group_by_unit_name',
    'group_by_unit_uuid',
)

UnitId: TypeAlias = int
UnitName: TypeAlias = str
UnitUuid: TypeAlias = UUID


class HasUnitId(Protocol):
    unit_id: UnitId


class HasUnitName(Protocol):
    unit_name: UnitName


class HasUnitUuid(Protocol):
    unit_uuid: UnitUuid


T = TypeVar('T')
ItemWithUnitUuidT = TypeVar('ItemWithUnitUuidT', bound=HasUnitUuid)
ItemWithUnitIdT = TypeVar('ItemWithUnitIdT', bound=HasUnitId)
ItemWithUnitNameT = TypeVar('ItemWithUnitNameT', bound=HasUnitName)


def group_items_by_attribute(items: Iterable[T], attribute_name: str) -> dict[Any, list[T]]:
    attribute_to_items: DefaultDict[Any, list[T]] = collections.defaultdict(list)
    for item in items:
        attribute_to_items[getattr(item, attribute_name)].append(item)
    return dict(attribute_to_items)


def group_by_unit_id(items: Iterable[ItemWithUnitIdT]) -> dict[UnitId, list[ItemWithUnitIdT]]:
    return group_items_by_attribute(items, attribute_name='unit_id')


def group_by_unit_name(items: Iterable[ItemWithUnitNameT]) -> dict[UnitName, list[ItemWithUnitNameT]]:
    return group_items_by_attribute(items, attribute_name='unit_name')


def group_by_unit_uuid(items: Iterable[ItemWithUnitUuidT]) -> dict[UnitUuid, list[ItemWithUnitUuidT]]:
    return group_items_by_attribute(items, attribute_name='unit_uuid')
