import asyncio
import itertools

from dodolib import DatabaseClient, AuthClient, DodoAPIClient
from dodolib.models import AuthCookies, OrderByUUID
from dodolib.utils.convert_models import UnitsConverter
from dotenv import load_dotenv

load_dotenv()

from rabbitmq import add_notification_to_queue
from storage import UUIDStorage


async def main():
    async with (
        DatabaseClient() as db_client,
        AuthClient() as auth_client,
        DodoAPIClient() as api_client,
    ):
        units = UnitsConverter(await db_client.get_units())
        accounts = await db_client.get_accounts()
        shift_manager_account_names = (account.name for account in accounts if account.name.startswith('shift'))
        tasks = (auth_client.get_cookies(account_name) for account_name in shift_manager_account_names)
        accounts_cookies: tuple[AuthCookies, ...] = await asyncio.gather(*tasks)
        tasks = (api_client.get_canceled_orders(account_cookies.cookies) for account_cookies in
                 accounts_cookies)
        canceled_orders: tuple[OrderByUUID, ...] = await asyncio.gather(*tasks)
        flatten_canceled_orders: itertools.chain[OrderByUUID] = itertools.chain.from_iterable(canceled_orders)

    unit_names_to_ids = units.names_to_ids
    with UUIDStorage() as uuid_storage:

        for order in flatten_canceled_orders:
            if order.receipt_printed_at is None:
                continue
            if uuid_storage.is_exist(order.uuid):
                continue

            add_notification_to_queue({
                'type': 'CANCELED_ORDERS',
                'unit_id': unit_names_to_ids[order.unit_name],
                'payload': order.dict(),
            })
            uuid_storage.add_uuid(order.uuid)


if __name__ == '__main__':
    asyncio.run(main())
