import functools
import logging
import pathlib

import httpx

import models
from core import load_config_from_file, setup_logging
from filters import filter_by_predicates, predicates, filter_via_any_predicate
from message_queue_events import CanceledOrderEvent
from services import message_queue
from services.converters import UnitsConverter
from services.external_dodo_api import DatabaseAPI, DodoAPI, AuthAPI
from services.storages import ObjectUUIDStorage


def main():
    storage_file_path = pathlib.Path.joinpath(pathlib.Path(__file__).parent.parent, 'local_storage',
                                              'canceled_orders.db')
    config_file_path = pathlib.Path(__file__).parent.parent / 'config.toml'
    config = load_config_from_file(config_file_path)

    setup_logging(loglevel=config.logging.level, logfile_path=config.logging.file_path)

    with httpx.Client(base_url=config.api.database_api_base_url) as database_client:
        database_api = DatabaseAPI(database_client)
        units = database_api.get_units()
    units = UnitsConverter(units)

    canceled_orders: list[models.CanceledOrder] = []
    with httpx.Client(base_url=config.api.auth_api_base_url) as auth_client:
        with httpx.Client(base_url=config.api.dodo_api_base_url) as dodo_api_client:
            auth_api = AuthAPI(auth_client)
            dodo_api = DodoAPI(dodo_api_client)

            accounts = auth_api.get_accounts()
            shift_manager_account_names = {account.name for account in accounts if account.name.startswith('shift')}

            for account_name in shift_manager_account_names:
                try:
                    account_cookies = auth_api.get_account_cookies(account_name)
                    canceled_orders += dodo_api.get_canceled_orders(cookies=account_cookies.cookies,
                                                                    country_code=config.country_code)
                except Exception:
                    logging.error(f'Could not get canceled orders for account {account_name}')
    with ObjectUUIDStorage(storage_file_path) as storage:
        filtered_canceled_orders = filter_by_predicates(
            filter_via_any_predicate(
                canceled_orders,
                predicates.has_appointed_courier,
                predicates.has_rejected_by_user_name,
            ),
            functools.partial(predicates.is_object_uuid_not_in_storage, storage=storage),
        )
    events = [
        CanceledOrderEvent(unit_id=units.unit_name_to_id[canceled_order.unit_name], canceled_order=canceled_order)
        for canceled_order in filtered_canceled_orders
    ]
    with message_queue.get_message_queue_channel(config.message_queue.rabbitmq_url) as message_queue_channel:
        message_queue.send_events(message_queue_channel, events)

    with ObjectUUIDStorage(storage_file_path) as storage:
        for canceled_order in filtered_canceled_orders:
            storage.insert(canceled_order.uuid)
            logging.info(f'New canceled order {canceled_order.uuid}')


if __name__ == '__main__':
    main()
