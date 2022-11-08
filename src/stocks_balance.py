import asyncio
import collections
from typing import Iterable

from dodolib import DatabaseClient, AuthClient, DodoAPIClient
from dodolib.models import StockBalance, StockBalanceStatistics
from dodolib.utils.convert_models import UnitsConverter

from message_queue import get_message_queue_channel, send_json_message
from settings import get_app_settings


def group_stocks_balance_by_unit_id(stocks_balance: Iterable[StockBalance]) -> dict[int, list[StockBalance]]:
    unit_id_to_stocks_balance = collections.defaultdict(list)
    for stock_balance in stocks_balance:
        unit_id_to_stocks_balance[stock_balance.unit_id].append(stock_balance)
    return unit_id_to_stocks_balance


async def main():
    app_settings = get_app_settings()

    async with DatabaseClient(app_settings.database_api_base_url) as db_client:
        units = UnitsConverter(await db_client.get_units())

    async with AuthClient(app_settings.auth_service_base_url) as auth_client:
        tasks = (auth_client.get_cookies(account_name) for account_name in units.account_names)
        accounts_cookies = await asyncio.gather(*tasks)

    account_names_to_unit_ids = units.account_names_to_unit_ids

    async with DodoAPIClient(app_settings.dodo_api_base_url) as api_client:
        tasks = (
            api_client.get_stocks_balance(
                cookies=account_cookies.cookies,
                unit_ids=account_names_to_unit_ids[account_cookies.account_name],
                days_left_threshold=1,
            ) for account_cookies in accounts_cookies
        )
        all_stocks_balance_statistics: tuple[StockBalanceStatistics, ...] = await asyncio.gather(*tasks,
                                                                                                 return_exceptions=True)
        stocks_balance_statistics = [j for i in all_stocks_balance_statistics
                                     for j in i.units
                                     if not isinstance(i, Exception)]
        error_unit_ids = [
            j for i in all_stocks_balance_statistics
            for j in i.error_unit_ids
            if not isinstance(i, Exception)
        ]
    grouped_stocks_balance = group_stocks_balance_by_unit_id(stocks_balance_statistics)

    unit_ids_to_names = units.ids_to_names
    with get_message_queue_channel() as message_queue_channel:
        for unit_id, unit_stocks_balance in grouped_stocks_balance.items():
            unit_name = unit_ids_to_names[unit_id]
            message_body = {
                'type': 'STOCKS_BALANCE',
                'unit_id': unit_id,
                'payload': {
                    'unit_name': unit_name,
                    'stocks_balance': [stock_balance.dict() for stock_balance in unit_stocks_balance]
                }
            }
            send_json_message(message_queue_channel, message_body)


if __name__ == '__main__':
    asyncio.run(main())
