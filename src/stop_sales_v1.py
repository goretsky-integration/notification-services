import functools
import pathlib
from argparse import ArgumentParser

import httpx

from core import load_config_from_file
from filters import filter_by_predicates, predicates
from message_queue_events import StopSaleByStreetEvent, StopSaleBySectorEvent
from services import message_queue
from services.converters import UnitsConverter
from services.external_dodo_api import DatabaseAPI, AuthAPI, DodoAPI
from services.period import Period
from shortcuts.stop_sales import get_stop_sales_v1


def main():
    argument_parser = ArgumentParser(
        prog='Stop Sales V1 Notifications',
        description='Generate events for stop sales V1',
    )
    argument_parser.add_argument(
        '--by',
        choices=('streets', 'sectors'),
        help='Choose source of stop sales',
        required=True,
    )

    arguments = argument_parser.parse_args()

    stop_sales_source_to_event_type_and_dodo_api_method = {
        'streets': (StopSaleByStreetEvent, DodoAPI.get_stop_sales_by_streets),
        'sectors': (StopSaleBySectorEvent, DodoAPI.get_stop_sales_by_sectors),
    }

    event_type, dodo_api_method = stop_sales_source_to_event_type_and_dodo_api_method[arguments.by]

    config_file_path = pathlib.Path(__file__).parent.parent / 'config.toml'
    config = load_config_from_file(config_file_path)

    stop_sales_period = Period.today_to_this_time()

    with httpx.Client(base_url=config.api.database_api_base_url) as database_client:
        units = DatabaseAPI(database_client).get_units()
    units = UnitsConverter(units)

    with httpx.Client(base_url=config.api.auth_api_base_url) as auth_client:
        with httpx.Client(base_url=config.api.dodo_api_base_url) as dodo_api_client:
            auth_api = AuthAPI(auth_client)
            dodo_api = DodoAPI(dodo_api_client)
            stop_sales = get_stop_sales_v1(
                dodo_api_method=functools.partial(dodo_api_method, self=dodo_api),
                auth_api=auth_api,
                units=units,
                period=stop_sales_period,
                country_code=config.country_code,
            )

    filtered_stop_sales = filter_by_predicates(stop_sales, predicates.is_stop_sale_v1_stopped)
    events = [
        event_type(unit_id=units.unit_name_to_id[stop_sale.unit_name], stop_sale=stop_sale)
        for stop_sale in filtered_stop_sales
    ]

    with message_queue.get_message_queue_channel(config.message_queue.rabbitmq_url) as message_queue_channel:
        message_queue.send_events(message_queue_channel, events)


if __name__ == '__main__':
    main()
