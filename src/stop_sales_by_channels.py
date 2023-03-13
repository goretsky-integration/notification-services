import functools
import logging
import pathlib
from argparse import ArgumentParser

import httpx

import models
from core import load_config, setup_logging
from filters import filter_by_predicates, predicates, filter_via_any_predicate
from message_queue_events import StopSaleByChannelEvent
from services import message_queue
from services.converters import UnitsConverter
from services.external_dodo_api import DatabaseAPI, DodoAPI, AuthAPI
from services.period import Period
from services.storages import ObjectUUIDStorage
from shortcuts.auth_service import get_account_credentials_batch
from shortcuts.dodo_api_service import get_stop_sales_v2_batch


def main():
    argument_parser = ArgumentParser(
        prog='Stop sales by sales channels',
        description='Generate events for stop sales by sales channels',
    )
    argument_parser.add_argument(
        '--remember',
        action='store_true',
        help='Save stop sale\'s IDs in the local storage',
    )
    argument_parser.add_argument(
        '--ignore-remembered',
        action='store_true',
        help='Ignore if stop sale\'s ID in the local storage',
    )
    argument_parser.add_argument(
        '--sales-channel-names',
        action='append',
        help='Allowed sales channel names',
        choices=[sales_channel_name.name.lower() for sales_channel_name in models.SalesChannelName],
        required=True,
    )

    arguments = argument_parser.parse_args()

    period_today = Period.today_to_this_time()

    storage_file_path = pathlib.Path.joinpath(
        pathlib.Path(__file__).parent.parent,
        'local_storage',
        'sales_channels_stops.db',
    )

    config_file_path = pathlib.Path(__file__).parent.parent / 'config.toml'
    config = load_config(config_file_path)

    setup_logging(loglevel=config.logging.level, logfile_path=config.logging.file_path)

    with httpx.Client(base_url=config.api.database_api_base_url) as http_client:
        database_api = DatabaseAPI(http_client)
        units = UnitsConverter(database_api.get_units())

    with httpx.Client(base_url=config.api.auth_api_base_url) as http_client:
        auth_api = AuthAPI(http_client)
        accounts_credentials = get_account_credentials_batch(
            retrieve_account_credentials=auth_api.get_account_tokens,
            account_names=units.account_names,
        )

    for account_name in accounts_credentials.errors:
        logging.warning(f'Could not retrieve credentials for account {account_name}')

    with httpx.Client(base_url=config.api.dodo_api_base_url, timeout=30) as http_client:
        dodo_api = DodoAPI(http_client)

        stop_sales = get_stop_sales_v2_batch(
            retrieve_stop_sales=dodo_api.get_stop_sales_by_sales_channels,
            account_tokens=accounts_credentials.result,
            country_code=config.country_code,
            units=units,
            period=period_today,
        )

    with ObjectUUIDStorage(storage_file_path) as storage:

        used_predicates = [predicates.is_stop_sale_v2_stopped]

        if arguments.ignore_remembered:
            used_predicates.append(functools.partial(predicates.is_object_uuid_not_in_storage, storage=storage))

        sales_channel_name_predicates = [
            functools.partial(
                predicates.is_stop_sales_channel_by,
                sales_channel_name=models.SalesChannelName[allowed_sales_channel_name.upper()],
            ) for allowed_sales_channel_name in arguments.sales_channel_names
        ]

        filtered_stop_sales = filter_via_any_predicate(
            filter_by_predicates(stop_sales.result, *used_predicates),
            *sales_channel_name_predicates,
        )

    events = [
        StopSaleByChannelEvent(
            unit_id=units.unit_uuid_to_id[stop_sale.unit_uuid],
            stop_sale=stop_sale,
        ) for stop_sale in filtered_stop_sales
    ]

    logging.debug(events)

    with message_queue.get_message_queue_channel(config.message_queue.rabbitmq_url) as message_queue_channel:
        message_queue.send_events(message_queue_channel, events)

    if arguments.remember:

        with ObjectUUIDStorage(storage_file_path) as storage:

            for stop_sale in filtered_stop_sales:
                storage.insert(stop_sale.uuid)


if __name__ == '__main__':
    main()
