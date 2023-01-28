from typing import TypeVar, Callable, Collection

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
