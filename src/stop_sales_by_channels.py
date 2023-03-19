import functools
import logging
import pathlib
from argparse import ArgumentParser

import httpx
from dodo_is_api.connection.http_clients import closing_http_client
from dodo_is_api.connection import DodoISAPIConnection
from dodo_is_api.models import StopSaleBySalesChannel
from dodo_is_api.mappers import map_stop_sale_by_sales_channel_dto

import models
from core import load_config_from_file, setup_logging
from filters import filter_by_predicates, predicates, filter_via_any_predicate
from message_queue_events import StopSaleByChannelEvent
from services import message_queue
from services.converters import UnitsConverter
from services.external_dodo_api import DatabaseAPI, AuthAPI
from services.period import Period
from services.storages import ObjectUUIDStorage
from shortcuts.auth_service import get_account_credentials_batch


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
    config = load_config_from_file(config_file_path)

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

    stop_sales: list[StopSaleBySalesChannel] = []
    for account_tokens in accounts_credentials.result:
        with closing_http_client(
                access_token=account_tokens.access_token,
                country_code=config.country_code,
        ) as http_client:
            units_related_to_account = units.grouped_by_account_name[account_tokens.account_name]

            dodo_is_api_connection = DodoISAPIConnection(http_client=http_client)

            raw_stop_sales = dodo_is_api_connection.get_stop_sales_by_sales_channels(
                from_date=period_today.start,
                to_date=period_today.end,
                units=units_related_to_account.uuids,
            )
            stop_sales += [map_stop_sale_by_sales_channel_dto(stop_sale) for stop_sale in raw_stop_sales]

    with ObjectUUIDStorage(storage_file_path) as storage:

        used_predicates = [predicates.is_stop_sale_v2_stopped]

        if arguments.ignore_remembered:
            used_predicates.append(
                functools.partial(predicates.is_object_uuid_not_in_storage, storage=storage, key='id')
            )

        sales_channel_name_predicates = [
            functools.partial(
                predicates.is_stop_sales_channel_by,
                sales_channel_name=models.SalesChannelName[allowed_sales_channel_name.upper()],
            ) for allowed_sales_channel_name in arguments.sales_channel_names
        ]

        filtered_stop_sales = filter_via_any_predicate(
            filter_by_predicates(stop_sales, *used_predicates),
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
                storage.insert(stop_sale.id)


if __name__ == '__main__':
    main()
