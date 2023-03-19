import collections
from typing import Iterable, TypeVar, Protocol, TypeAlias, Any, DefaultDict
from uuid import UUID

__all__ = (
    'group_by_unit_id',
    'group_by_unit_name',
    'group_by_unit_uuid',
    'map_config_dto',
)

import models

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


def map_config_dto(config: dict) -> models.Config:
    return models.Config(
        country_code=config['country_code'],
        logging=models.LoggingConfig(
            level=config['logging']['level'],
            file_path=config['logging']['file_path'],
        ),
        api=models.APIConfig(
            auth_api_base_url=config['api']['auth_api_url'],
            dodo_api_base_url=config['api']['dodo_api_url'],
            database_api_base_url=config['api']['database_api_url'],
        ),
        partial_ingredients=models.PartialIngredientStopSalesConfig(
            allowed_ingredient_names=set(config['partial_ingredient_stop_sales']['allowed_ingredient_names']),
            disallowed_ingredient_names=set(config['partial_ingredient_stop_sales']['disallowed_ingredient_names']),
        ),
        cheated_orders=models.CheatedOrdersConfig(
            skipped_phone_numbers=set(config['cheated_orders']['skipped_phone_numbers']),
        ),
        message_queue=models.MessageQueueConfig(
            rabbitmq_url=config['message_queue']['rabbitmq_url'],
        ),
    )
