import logging
from typing import TypeVar, Callable, Collection

from services.converters import UnitsConverter
from services.external_dodo_api import AuthAPI
from services.period import Period

T = TypeVar('T')


def get_stop_sales_v1(
        dodo_api_method: Callable[..., Collection[T]],
        auth_api: AuthAPI,
        units: UnitsConverter,
        period: Period,
        country_code: str,
) -> list[T]:
    stop_sales = []
    for account_name, grouped_units in units.grouped_by_office_manager_account_name.items():
        for _ in range(5):
            try:
                account_cookies = auth_api.get_account_cookies(account_name)
                stop_sales += dodo_api_method(
                    unit_ids=grouped_units.ids,
                    cookies=account_cookies.cookies,
                    period=period,
                    country_code=country_code,
                )
            except Exception:
                logging.warning(
                    f'Could not get stop sales for units {grouped_units.ids}. Trying again')
            else:
                logging.info(f'Got stop sales for units {grouped_units.ids}')
                break
        else:
            logging.error(
                f'Could not get stop sales for units {grouped_units.ids}')
    return stop_sales
