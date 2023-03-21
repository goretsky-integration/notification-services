import logging

import models
from services.converters import UnitsConverter
from services.external_dodo_api import DodoAPI, AuthAPI

__all__ = ('get_stocks_balance',)


def get_stocks_balance(
        *,
        dodo_api: DodoAPI,
        auth_api: AuthAPI,
        units: UnitsConverter,
        country_code: str,
) -> list[models.UnitStocksBalance]:
    stocks_balance: list[models.UnitStocksBalance] = []
    for account_name, grouped_units in units.grouped_by_office_manager_account_name.items():
        for _ in range(5):
            try:
                account_cookies = auth_api.get_account_cookies(account_name)
                stocks_balance += dodo_api.get_stocks_balance(
                    unit_ids=grouped_units.ids,
                    cookies=account_cookies.cookies,
                    days_left_threshold=1,
                    country_code=country_code,
                ).units
            except Exception:
                logging.warning(
                    f'Could not get stocks balance for units {grouped_units.ids}. Trying again')
            else:
                logging.info(
                    f'Got stocks balance for units {grouped_units.ids}')
                break
        else:
            logging.error(
                f'Could not get stocks balance for units {grouped_units.ids}')
    return stocks_balance
