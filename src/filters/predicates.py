from typing import Iterable, TypeVar, Sized

import models
from services.storages import DailyIngredientStopSalesStorage, PhoneNumbersStorage

__all__ = (
    'is_stop_sale_v1_stopped',
    'is_stop_sale_v2_stopped',
    'is_ingredient_name_allowed',
    'is_ingredient_name_not_blocked',
    'is_object_uuid_not_in_storage',
    'has_printed_receipt',
    'is_more_orders_than_in_storage',
)

T = TypeVar('T')


def is_stop_sale_v1_stopped(stop_sale: models.StopSaleV1) -> bool:
    return stop_sale.staff_name_who_resumed is None


def is_stop_sale_v2_stopped(stop_sale: models.StopSaleV2) -> bool:
    return stop_sale.resumed_by_user_id is None


def is_ingredient_name_allowed(
        stop_sale: models.StopSaleByIngredient,
        allowed_ingredient_names: Iterable[str],
) -> bool:
    return any((allowed_name.lower() in stop_sale.ingredient_name.lower()
                for allowed_name in allowed_ingredient_names))


def is_ingredient_name_not_blocked(
        stop_sale: models.StopSaleByIngredient,
        disallowed_ingredient_names: Iterable[str],
) -> bool:
    return all((disallowed_name.lower() not in stop_sale.ingredient_name.lower()
                for disallowed_name in disallowed_ingredient_names))


def is_object_uuid_not_in_storage(element: T, storage: DailyIngredientStopSalesStorage) -> bool:
    return not storage.is_exist(element.uuid)


def has_printed_receipt(canceled_order: models.CanceledOrder) -> bool:
    return canceled_order.receipt_printed_at is not None


def is_more_orders_than_in_storage(
        common_phone_number_orders: models.CommonPhoneNumberOrders,
        storage: PhoneNumbersStorage,
) -> bool:
    count_in_storage = storage.get_phone_number_count(common_phone_number_orders.phone_number)
    return len(common_phone_number_orders.orders) > count_in_storage
