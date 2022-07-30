import collections
from typing import Iterable, TypeAlias

from config import get_stocks_balance_settings
from core import models, rabbitmq
from core.repositories import get_auth_client, get_dodo_api_client, get_db_client
from core.utils import exceptions
from core.utils.convert_models import UnitsConverter

UnitIDToStocksBalance: TypeAlias = dict[int, list[models.StockBalance]]


def group_stocks_balance_by_unit_id(stocks_balance: Iterable[models.StockBalance]) -> UnitIDToStocksBalance:
    unit_id_to_stocks_balance: UnitIDToStocksBalance = collections.defaultdict(list)
    for stock_balance in stocks_balance:
        stocks_balance_by_unit_id = unit_id_to_stocks_balance[stock_balance.unit_id]
        stocks_balance_by_unit_id.append(stock_balance)
    return unit_id_to_stocks_balance


def main():
    stocks_balance_settings = get_stocks_balance_settings()
    with (
        get_db_client() as db_client,
        get_dodo_api_client() as dodo_api_client,
        get_auth_client() as auth_client,
    ):
        units = UnitsConverter(db_client.get_units())
        unit_ids_to_names = units.ids_to_names
        for account_name, unit_ids in units.account_names_to_unit_ids.items():
            cookies = auth_client.get_cookies(account_name)
            try:
                stocks_balance_statistics = dodo_api_client.get_stocks_balance(
                    cookies=cookies.cookies,
                    unit_ids=unit_ids,
                    days_left_threshold=stocks_balance_settings.days_left_threshold,
                )
            except exceptions.DodoAPIError:
                continue
            for unit_id, stocks_balance in group_stocks_balance_by_unit_id(stocks_balance_statistics.units).items():
                unit_name = unit_ids_to_names[unit_id]
                rabbitmq.add_notification_to_queue({
                    'type': 'STOCKS_BALANCE',
                    'unit_id': unit_id,
                    'payload': {
                        'unit_name': unit_name,
                        'stocks_balance': [stock_balance.dict() for stock_balance in stocks_balance],
                    }
                })


if __name__ == '__main__':
    main()
