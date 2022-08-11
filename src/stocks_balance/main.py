import asyncio
import collections
from typing import Iterable, TypeAlias

from dodolib import DatabaseClient, AuthClient, DodoAPIClient
from dodolib.models import StockBalance, AuthCookies, StockBalanceStatistics
from dodolib.utils.convert_models import UnitsConverter
from dotenv import load_dotenv

load_dotenv()

from rabbitmq import add_notification_to_queue

UnitIDToStocksBalance: TypeAlias = dict[int, list[StockBalance]]


def group_stocks_balance_by_unit_id(stocks_balance: Iterable[StockBalance]) -> UnitIDToStocksBalance:
    unit_id_to_stocks_balance: UnitIDToStocksBalance = collections.defaultdict(list)
    for stock_balance in stocks_balance:
        stocks_balance_by_unit_id = unit_id_to_stocks_balance[stock_balance.unit_id]
        stocks_balance_by_unit_id.append(stock_balance)
    return unit_id_to_stocks_balance


async def main():
    async with (
        DatabaseClient() as db_client,
        AuthClient() as auth_client,
        DodoAPIClient() as api_client,
    ):
        units = UnitsConverter(await db_client.get_units())
        unit_ids_to_names = units.ids_to_names
        account_names_to_unit_ids = units.account_names_to_unit_ids
        tasks = (auth_client.get_cookies(account_name) for account_name in units.account_names)
        accounts_cookies: tuple[AuthCookies, ...] = await asyncio.gather(*tasks)
        tasks = (
            api_client.get_stocks_balance(
                cookies=account_cookies.cookies,
                unit_ids=account_names_to_unit_ids[account_cookies.account_name],
                days_left_threshold=1,
            ) for account_cookies in accounts_cookies
        )
        all_stocks_balance_statistics: tuple[StockBalanceStatistics, ...] = await asyncio.gather(*tasks)
    for stocks_balance_statistics in all_stocks_balance_statistics:
        for unit_id, stocks_balance in group_stocks_balance_by_unit_id(stocks_balance_statistics.units).items():
            unit_name = unit_ids_to_names[unit_id]
            print(stocks_balance)
            add_notification_to_queue({
                'type': 'STOCKS_BALANCE',
                'unit_id': unit_id,
                'payload': {
                    'unit_name': unit_name,
                    'stocks_balance': [stock_balance.dict() for stock_balance in stocks_balance],
                }
            })


if __name__ == '__main__':
    asyncio.run(main())
