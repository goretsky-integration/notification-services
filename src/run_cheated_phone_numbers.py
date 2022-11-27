import asyncio
import pathlib

from dodolib import DatabaseClient, AuthClient, DodoAPIClient, models
from dodolib.utils.convert_models import UnitsConverter

from message_queue import send_json_message, get_message_queue_channel
from settings import get_app_settings
from storages import CheatedPhonesCountStorage

FILTER_NUMBERS = {
    '79680325999.0',
}


async def main():
    app_settings = get_app_settings()
    storage_path = pathlib.Path.joinpath(pathlib.Path(__file__).parent.parent, 'local_storage', 'cheated_phones.json')

    async with DatabaseClient(app_settings.database_api_base_url) as db_client:
        units = UnitsConverter(await db_client.get_units())

    async with AuthClient(app_settings.auth_service_base_url) as auth_client:
        tasks = (auth_client.get_cookies(account_name) for account_name in units.account_names)
        accounts_cookies = await asyncio.gather(*tasks)

    account_names_to_unit_id_and_name = units.account_names_to_unit_ids_and_names
    cheated_orders: list[models.CheatedOrders] = []
    async with DodoAPIClient(app_settings.dodo_api_base_url) as api_client:
        for account_cookies in accounts_cookies:
            cheated_orders += await api_client.get_cheated_orders(
                account_cookies.cookies,
                account_names_to_unit_id_and_name[account_cookies.account_name],
                repeated_phones_count_threshold=3,
            )

    unit_name_to_id = units.names_to_ids
    with get_message_queue_channel() as message_queue_channel:
        with CheatedPhonesCountStorage(storage_path) as storage:
            for cheated_order in cheated_orders:
                if cheated_order.phone_number in FILTER_NUMBERS:
                    continue

                phone_numbers_in_storage_count = storage.get(cheated_order.phone_number)
                orders_with_same_phone_numbers_count = len(cheated_order.orders)
                if phone_numbers_in_storage_count >= orders_with_same_phone_numbers_count:
                    continue

                message_body = {
                    'unit_id': unit_name_to_id[cheated_order.unit_name],
                    'type': 'CHEATED_PHONE_NUMBERS',
                    'payload': cheated_order.dict(),
                }
                send_json_message(message_queue_channel, message_body)
                storage.set(cheated_order.phone_number, orders_with_same_phone_numbers_count)


if __name__ == '__main__':
    asyncio.run(main())
