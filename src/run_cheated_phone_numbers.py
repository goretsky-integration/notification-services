import functools
import pathlib

import httpx

import models
from core import load_config, setup_logging
from filters import filter_by_predicates, predicates
from message_queue_events import CheatedPhoneNumberEvent
from services import message_queue
from services.converters import UnitsConverter
from services.external_dodo_api import DatabaseAPI, DodoAPI, AuthAPI
from services.storages import PhoneNumbersStorage


def main():
    storage_file_path = pathlib.Path.joinpath(pathlib.Path(__file__).parent.parent, 'local_storage', 'phone_numbers.db')
    config_file_path = pathlib.Path(__file__).parent.parent / 'config.toml'
    config = load_config(config_file_path)

    setup_logging(loglevel=config.logging.level, logfile_path=config.logging.file_path)

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
        filtered_common_phone_number_orders = filter_by_predicates(
            cheated_orders,
            functools.partial(predicates.is_orders_count_more_than, count=2),
            functools.partial(predicates.is_more_orders_than_in_storage, storage=storage),
        )
    events = [CheatedPhoneNumberEvent(unit_id=units.unit_name_to_id[cheated_order.unit_name],
                                      common_phone_number_orders=cheated_order)
              for cheated_order in filtered_common_phone_number_orders]
    with message_queue.get_message_queue_channel(config.message_queue.rabbitmq_url) as message_queue_channel:
        message_queue.send_events(message_queue_channel, events)

    with PhoneNumbersStorage(storage_file_path) as storage:
        for common_phone_number_orders in filtered_common_phone_number_orders:
            storage.set_phone_numbers_count(
                phone_number=common_phone_number_orders.phone_number,
                count=len(common_phone_number_orders.orders),
            )


if __name__ == '__main__':
    main()
