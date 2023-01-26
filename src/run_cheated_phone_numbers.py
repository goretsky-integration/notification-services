import pathlib

import httpx

import models
from config import load_config
from message_queue_events import CheatedPhoneNumberEvent
from services import message_queue
from services.converters import UnitsConverter
from services.external_dodo_api import DatabaseAPI, DodoAPI, AuthAPI
from services.storages import PhoneNumbersStorage


def main():
    storage_file_path = pathlib.Path.joinpath(pathlib.Path(__file__).parent.parent, 'local_storage', 'phone_numbers.db')
    config_file_path = pathlib.Path(__file__).parent.parent / 'config.toml'
    config = load_config(config_file_path)

    with httpx.Client(base_url=config.api.database_api_base_url) as database_client:
        units = DatabaseAPI(database_client).get_units()
    units = UnitsConverter(units)

    cheated_orders: list[models.CommonPhoneNumberOrders] = []
    with httpx.Client(base_url=config.api.auth_api_base_url) as auth_client:
        with httpx.Client(base_url=config.api.dodo_api_base_url, timeout=60) as dodo_api_client:
            auth_api = AuthAPI(auth_client)
            dodo_api = DodoAPI(dodo_api_client)
            for account_name, grouped_units in units.grouped_by_account_name.items():
                account_cookies = auth_api.get_account_cookies(account_name)
                cheated_orders += dodo_api.get_cheated_orders(
                    unit_ids_and_names=grouped_units.ids_and_names,
                    cookies=account_cookies.cookies,
                    repeated_phone_number_count_threshold=3,
                )

    with PhoneNumbersStorage(storage_file_path) as storage:
        with message_queue.get_message_queue_channel(config.message_queue.rabbitmq_url) as message_queue_channel:
            for cheated_order in cheated_orders:
                if len(cheated_order.orders) <= storage.get_phone_number_count(cheated_order.phone_number):
                    continue
                event = CheatedPhoneNumberEvent(
                    unit_id=units.unit_name_to_id[cheated_order.unit_name],
                    common_phone_number_orders=cheated_order,
                )
                message_queue.send_json_message(message_queue_channel, event)
                storage.set_phone_numbers_count(cheated_order.phone_number, count=len(cheated_order.orders))


if __name__ == '__main__':
    main()
