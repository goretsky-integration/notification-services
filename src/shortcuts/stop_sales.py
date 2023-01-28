from typing import TypeVar, Callable, Collection, Iterable

import models
from services.converters import UnitsConverter
from services.external_dodo_api import AuthAPI
from services.period import Period

T = TypeVar('T')
SSV1 = TypeVar('SSV1', bound=models.StopSaleV1)
SSV2 = TypeVar('SSV2', bound=models.StopSaleV2)


def get_stop_sales_v2(
        *,
        dodo_api_method: Callable[..., Collection[T]],
        auth_api: AuthAPI,
        units: UnitsConverter,
        country_code: str,
        period: Period,
) -> list[T]:
    stop_sales = []
    for account_name, grouped_units in units.grouped_by_account_name.items():
        for _ in range(5):
            try:
                account_tokens = auth_api.get_account_tokens(account_name)
                stop_sales += dodo_api_method(
                    country_code=country_code,
                    unit_uuids=grouped_units.uuids,
                    token=account_tokens.access_token,
                    period=period,
                )
            except Exception:
                pass
            else:
                break
    return stop_sales


def get_stop_sales_v1(
        dodo_api_method: Callable[..., Collection[T]],
        auth_api: AuthAPI,
        units: UnitsConverter,
        period: Period,
) -> list[T]:
    stop_sales = []
    for account_name, grouped_units in units.grouped_by_account_name.items():
        for _ in range(5):
            try:
                account_cookies = auth_api.get_account_cookies(account_name)
                stop_sales += dodo_api_method(
                    unit_ids=grouped_units.ids,
                    cookies=account_cookies.cookies,
                    period=period,
                )
            except Exception:
                pass
            else:
                break
    return stop_sales


def filter_not_resumed_stop_sales_v2(stop_sales: Iterable[SSV2]) -> list[SSV2]:
    return [stop_sale for stop_sale in stop_sales if stop_sale.resumed_by_user_id is None]


def filter_not_resumed_stop_sales_v1(stop_sales: Iterable[SSV1]) -> list[SSV1]:
    return [stop_sale for stop_sale in stop_sales if stop_sale.staff_name_who_resumed is None]
