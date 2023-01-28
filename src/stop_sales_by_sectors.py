import pathlib

import httpx

from config import load_config
from message_queue_events import StopSaleBySectorEvent
from services import message_queue
from services.converters import UnitsConverter
from services.external_dodo_api import DatabaseAPI, DodoAPI, AuthAPI
from services.period import Period
from shortcuts.stop_sales import get_stop_sales_v1, filter_not_resumed_stop_sales_v1


def main():
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
            stop_sales = get_stop_sales_v1(
                dodo_api_method=dodo_api.get_stop_sales_by_sectors,
                auth_api=auth_api,
                units=units,
                period=stop_sales_period,
            )

    not_resumed_stop_sales = filter_not_resumed_stop_sales_v1(stop_sales)
    events = [StopSaleBySectorEvent(unit_id=units.unit_name_to_id[stop_sale.unit_name], stop_sale=stop_sale)
              for stop_sale in not_resumed_stop_sales]

    with message_queue.get_message_queue_channel(config.message_queue.rabbitmq_url) as message_queue_channel:
        message_queue.send_events(message_queue_channel, events)


if __name__ == '__main__':
    main()
