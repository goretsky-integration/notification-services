import asyncio
import itertools

from dodolib import DodoAPIClient, DatabaseClient, AuthClient
from dodolib.models import AuthCookies, CheatedOrders
from dodolib.utils.convert_models import UnitsConverter
from dotenv import load_dotenv

from storage import CheatedPhonesStorage

load_dotenv()

from rabbitmq import add_notification_to_queue

FILTER_NUMBERS = {
    '79680325999.0',
}


async def main():
    async with (
        DatabaseClient() as db_client,
        DodoAPIClient() as api_client,
        AuthClient() as auth_client,
    ):
        units = UnitsConverter(await db_client.get_units())
        tasks = (auth_client.get_cookies(account_name) for account_name in units.account_names)
        accounts_cookies: tuple[AuthCookies, ...] = await asyncio.gather(*tasks)
        account_names_to_unit_ids_and_names = units.account_names_to_unit_ids_and_names
        tasks = (api_client.get_cheated_orders(account_cookies.cookies,
                                               account_names_to_unit_ids_and_names[account_cookies.account_name],
                                               repeated_phones_count_threshold=3)
                 for account_cookies in accounts_cookies)
        all_cheated_orders: tuple[list[CheatedOrders], ...] = await asyncio.gather(*tasks)
        cheated_orders = itertools.chain.from_iterable(all_cheated_orders)
    unit_names_to_ids = units.names_to_ids

    with CheatedPhonesStorage() as storage:
        for cheated_order in cheated_orders:
            if cheated_order.phone_number in FILTER_NUMBERS:
                continue
            if storage.get_count(cheated_order.phone_number) >= len(cheated_order.orders):
                continue
            storage.set_count(cheated_order.phone_number, len(cheated_order.orders))
            add_notification_to_queue({
                'unit_id': unit_names_to_ids[cheated_order.unit_name],
                'type': 'CHEATED_PHONE_NUMBERS',
                'payload': cheated_order.dict()
            })


if __name__ == '__main__':
    asyncio.run(main())
