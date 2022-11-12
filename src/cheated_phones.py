import asyncio

from dodolib import DatabaseClient, AuthClient, DodoAPIClient, models
from dodolib.models import AuthCookies
from dodolib.utils.convert_models import UnitsConverter

from message_queue import send_json_message, get_message_queue_channel
from settings import get_app_settings
from stop_sales.cheated_phones_storage import CheatedPhonesStorage

FILTER_NUMBERS = {
    '79680325999.0',
}


async def main():
    app_settings = get_app_settings()
    repeated_phones_count_threshold = 3

    async with DatabaseClient(app_settings.database_api_base_url) as db_client:
        units = UnitsConverter(await db_client.get_units())

    async with AuthClient(app_settings.auth_service_base_url) as auth_client:
        tasks = (auth_client.get_cookies(account_name) for account_name in units.account_names)
        accounts_cookies: tuple[AuthCookies, ...] = await asyncio.gather(*tasks)

    account_names_to_unit_ids_and_names = units.account_names_to_unit_ids_and_names
    async with DodoAPIClient(app_settings.dodo_api_base_url) as api_client:
        tasks = (api_client.get_cheated_orders(account.cookies,
                                               account_names_to_unit_ids_and_names[account.account_name],
                                               repeated_phones_count_threshold)
                 for account in accounts_cookies)
        cheated_orders: tuple[list[models.CheatedOrders], ...] = await asyncio.gather(*tasks, return_exceptions=True)

        all_cheated_orders = [order for orders in cheated_orders
                              for order in orders
                              if not isinstance(orders, Exception)]

    unit_names_to_ids = units.names_to_ids

    with get_message_queue_channel() as channel:
        with CheatedPhonesStorage() as storage:

            for cheated_order in all_cheated_orders:
                if cheated_order.phone_number in FILTER_NUMBERS:
                    continue
                if storage.get_count(cheated_order.phone_number) >= len(cheated_order.orders):
                    continue

                message_body = {
                    'unit_id': unit_names_to_ids[cheated_order.unit_name],
                    'type': 'CHEATED_PHONE_NUMBERS',
                    'payload': cheated_order.dict()
                }
                send_json_message(channel, message_body)
                storage.set_count(cheated_order.phone_number, len(cheated_order.orders))


if __name__ == '__main__':
    asyncio.run(main())
