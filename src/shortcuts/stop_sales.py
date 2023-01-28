import collections
from typing import TypeVar, Callable, Collection, Iterable, DefaultDict

import models
from services.converters import UnitsConverter
from services.external_dodo_api import AuthAPI
from services.period import Period

T = TypeVar('T')


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


def group_stop_sales_by_unit_names(
        stop_sales: Iterable[models.StopSaleV1 | models.StopSaleV2 | T],
) -> DefaultDict[str, list[T]]:
    unit_name_to_stop_sales = collections.defaultdict(list)
    for stop_sale in stop_sales:
        unit_name_to_stop_sales[stop_sale.unit_name].append(stop_sale)
    return unit_name_to_stop_sales
