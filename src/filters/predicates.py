from typing import Iterable, TypeVar

from dodo_is_api.models import StopSaleBySalesChannel, SalesChannel

import models
from services.storages import PhoneNumbersStorage, ObjectUUIDStorage, UsedPromoCodesStorage

__all__ = (
    'is_stop_sale_v1_stopped',
    'is_stop_sale_v2_stopped',
    'is_ingredient_name_allowed',
    'is_ingredient_name_not_blocked',
    'is_object_uuid_not_in_storage',
    'has_printed_receipt',
    'is_more_orders_than_in_storage',
    'is_orders_count_more_than',
    'has_appointed_courier',
    'has_rejected_by_user_name',
    'is_stop_sales_channel_by',
    'is_promo_code_not_in_storage',
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


def is_object_uuid_not_in_storage(element: T, storage: ObjectUUIDStorage, key: str = 'uuid') -> bool:
    return not storage.is_exist(getattr(element, key))


def has_printed_receipt(canceled_order: models.CanceledOrder) -> bool:
    return canceled_order.receipt_printed_at is not None


def is_more_orders_than_in_storage(
        common_phone_number_orders: models.CommonPhoneNumberOrders,
        storage: PhoneNumbersStorage,
) -> bool:
    count_in_storage = storage.get_phone_number_count(common_phone_number_orders.phone_number)
    return len(common_phone_number_orders.orders) > count_in_storage


def is_orders_count_more_than(
        common_phone_number_orders: models.CommonPhoneNumberOrders,
        count: int,
) -> bool:
    return len(common_phone_number_orders.orders) > count


def has_appointed_courier(canceled_order: models.CanceledOrder) -> bool:
    return canceled_order.courier_name is not None


def has_rejected_by_user_name(canceled_order: models.CanceledOrder) -> bool:
    return canceled_order.rejected_by_user_name is not None


def is_stop_sales_channel_by(
        stop_sale: StopSaleBySalesChannel,
        sales_channel_name: SalesChannel,
) -> bool:
    return stop_sale.sales_channel_name == sales_channel_name


def is_promo_code_not_in_storage(
        used_promo_code: models.UnitUsedPromoCode,
        storage: UsedPromoCodesStorage,
) -> bool:
    return not storage.is_exists(
        unit_id=used_promo_code.unit_id,
        promo_code=used_promo_code.promo_code,
        order_no=used_promo_code.order_no,
    )


def is_canceled_order_sales_channel(
        order: models.CanceledOrder,
        sales_channel_name: str,
) -> bool:
    return order.type == sales_channel_name
