import asyncio

from dodolib import DatabaseClient, AuthClient, DodoAPIClient, models
from dodolib.utils.convert_models import UnitsConverter

from canceled_orders_storage import UUIDStorage
from message_queue import get_message_queue_channel, send_json_message
from settings import get_app_settings


async def main():
    app_settings = get_app_settings()

    async with DatabaseClient(app_settings.database_api_base_url) as db_client:
        units, accounts = await asyncio.gather(db_client.get_units(), db_client.get_accounts())
        units = UnitsConverter(units)

    unit_names_to_ids = units.names_to_ids
    shift_manager_account_names = (account.name for account in accounts if account.name.startswith('shift'))

    async with AuthClient(app_settings.auth_service_base_url) as auth_client:
        tasks = (auth_client.get_cookies(account_name) for account_name in shift_manager_account_names)
        accounts_cookies = await asyncio.gather(*tasks)

    async with DodoAPIClient(app_settings.dodo_api_base_url) as api_client:
        tasks = (api_client.get_canceled_orders(cookies=account.cookies) for account in accounts_cookies)
        all_canceled_orders = await asyncio.gather(*tasks, return_exceptions=True)
        canceled_orders: list[models.OrderByUUID] = [order for unit_canceled_orders in all_canceled_orders
                                                     for order in unit_canceled_orders
                                                     if not isinstance(unit_canceled_orders, Exception)]

    with get_message_queue_channel() as message_queue_channel:
        with UUIDStorage() as storage:
            for canceled_order in canceled_orders:
                if canceled_order.receipt_printed_at is None:
                    continue
                if storage.is_exist(canceled_order.uuid):
                    continue
                message_body = {
                    'type': 'CANCELED_ORDERS',
                    'unit_id': unit_names_to_ids[canceled_order.unit_name],
                    'payload': canceled_order.dict(),
                }
                send_json_message(message_queue_channel, message_body)
                storage.add_uuid(canceled_order.uuid)


if __name__ == '__main__':
    asyncio.run(main())
