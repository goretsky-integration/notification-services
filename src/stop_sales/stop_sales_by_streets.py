import asyncio
import itertools

from dodolib import DodoAPIClient, AuthClient, DatabaseClient
from dodolib.utils.convert_models import UnitsConverter
from dodolib.models import AuthCookies, StopSaleByStreets
from dotenv import load_dotenv

load_dotenv()

from rabbitmq import add_notification_to_queue


def to_payload(stop_sale: StopSaleByStreets) -> dict:
    return {
        'unit_name': stop_sale.unit_name,
        'started_at': stop_sale.started_at,
        'street_name': stop_sale.street,
    }


async def main():
    async with (
        DatabaseClient() as db_client,
        AuthClient() as auth_client,
        DodoAPIClient() as api_client,
    ):
        units = UnitsConverter(await db_client.get_units())
        unit_names_to_ids = units.names_to_ids
        account_names_to_unit_ids = units.account_names_to_unit_ids
        tasks = (auth_client.get_cookies(account_name) for account_name in units.account_names)
        accounts_cookies: tuple[AuthCookies, ...] = await asyncio.gather(*tasks)
        tasks = (api_client.get_stop_sales_by_streets(account_cookies.cookies,
                                                      account_names_to_unit_ids[account_cookies.account_name])
                 for account_cookies in accounts_cookies)
        all_stop_sales_by_streets: tuple[list[StopSaleByStreets], ...] = await asyncio.gather(*tasks)
        stop_sales_by_streets = itertools.chain.from_iterable(all_stop_sales_by_streets)

    for stop_sale in stop_sales_by_streets:
        if stop_sale.staff_name_who_resumed is not None:
            continue
        body = {
            'unit_id': unit_names_to_ids[stop_sale.unit_name],
            'type': 'STREET_STOP_SALES',
            'payload': to_payload(stop_sale),
        }
        add_notification_to_queue(body)


if __name__ == '__main__':
    asyncio.run(main())
