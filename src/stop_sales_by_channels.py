import datetime
import pathlib

import httpx

from argparse import ArgumentParser
from core import load_config
from filters import filter_by_predicates, predicates
from message_queue_events import StopSaleByChannelEvent
from services import message_queue
from services.converters import UnitsConverter
from services.external_dodo_api import DatabaseAPI, DodoAPI, AuthAPI
from services.period import Period
from shortcuts.stop_sales import get_stop_sales_v2


def main():
    argument_parser = ArgumentParser(
        prog='Stop sales by sales channels',
        description='Generate events for stop sales by sales channels',
    )
    argument_parser.add_argument(
        '---remember',
        action='store_true',
        help='Save stop sale\'s IDs in the local storage',
    )
    argument_parser.add_argument(
        '--ignore-remembered',
        action='store_true',
        help='Ignore if stop sale\'s ID in the local storage',
    )
    argument_parser.add_argument(
        '--include-empty-units',
        action='store_true',
        help='Create event even if unit has no stop sales',
    )

    arguments = argument_parser.parse_args()

    storage_file_path = pathlib.Path.joinpath(
        pathlib.Path(__file__).parent.parent,
        'local_storage',
        'sales_channels_stops.db',
    )

    config_file_path = pathlib.Path(__file__).parent.parent / 'config.toml'
    config = load_config(config_file_path)

    stop_sales_period = Period.today_to_this_time()

    with httpx.Client(base_url=config.api.database_api_base_url) as database_client:
        units = DatabaseAPI(database_client).get_units()
    units = UnitsConverter(units)

    with httpx.Client(base_url=config.api.auth_api_base_url) as auth_client:
        with httpx.Client(base_url=config.api.dodo_api_base_url) as dodo_api_client:
            auth_api = AuthAPI(auth_client)
            dodo_api = DodoAPI(dodo_api_client)
            stop_sales = get_stop_sales_v2(
                dodo_api_method=dodo_api.get_stop_sales_by_sales_channels,
                auth_api=auth_api,
                units=units,
                country_code=config.country_code,
                period=stop_sales_period,
            )
    filtered_stop_sales = filter_by_predicates(stop_sales, predicates.is_stop_sale_v2_stopped)
    events = [StopSaleByChannelEvent(unit_id=units.unit_name_to_id[stop_sale.unit_name], stop_sale=stop_sale)
              for stop_sale in filtered_stop_sales]

    # with message_queue.get_message_queue_channel(config.message_queue.rabbitmq_url) as message_queue_channel:
    #     message_queue.send_events(message_queue_channel, events)


if __name__ == '__main__':
    main()
