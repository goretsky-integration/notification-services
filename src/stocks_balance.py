import collections
import pathlib
from typing import Iterable, DefaultDict

import httpx

import models
from config import load_config
from message_queue_events import StocksBalanceEvent
from services import message_queue
from services.converters import UnitsConverter
from services.external_dodo_api import DatabaseAPI, DodoAPI, AuthAPI


def group_stocks_balance_by_unit_id(
        stocks_balance: Iterable[models.UnitStocksBalance],
) -> DefaultDict[int, list[models.UnitStocksBalance]]:
    unit_id_to_stocks_balance = collections.defaultdict(list)
    for stock_balance in stocks_balance:
        unit_id_to_stocks_balance[stock_balance.unit_id].append(stock_balance)
    return unit_id_to_stocks_balance


def main():
    config_file_path = pathlib.Path(__file__).parent.parent / 'config.toml'
    config = load_config(config_file_path)

    with httpx.Client(base_url=config.api.database_api_base_url) as database_client:
        units = DatabaseAPI(database_client).get_units()
    units = UnitsConverter(units)

    stocks_balance: list[models.UnitStocksBalance] = []
    with httpx.Client(base_url=config.api.auth_api_base_url) as auth_client:
        with httpx.Client(base_url=config.api.dodo_api_base_url, timeout=60) as dodo_api_client:
            auth_api = AuthAPI(auth_client)
            dodo_api = DodoAPI(dodo_api_client)
            for account_name, grouped_units in units.grouped_by_account_name.items():
                account_cookies = auth_api.get_account_cookies(account_name)
                stocks_balance += dodo_api.get_stocks_balance(
                    unit_ids=grouped_units.ids,
                    cookies=account_cookies.cookies,
                    days_left_threshold=1,
                ).units

    with message_queue.get_message_queue_channel(config.message_queue.rabbitmq_url) as message_queue_channel:
        for unit_id, unit_stocks_balance in group_stocks_balance_by_unit_id(stocks_balance).items():
            event = StocksBalanceEvent(
                unit_id=unit_id,
                unit_name=units.unit_id_to_name[unit_id],
                units_stocks_balance=unit_stocks_balance,
            )
            message_queue.send_json_message(message_queue_channel, event)


if __name__ == '__main__':
    main()
