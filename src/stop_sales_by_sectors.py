import pathlib

import httpx

import models
from config import load_config
from message_queue_events import StopSaleBySectorEvent
from services import message_queue
from services.converters import UnitsConverter
from services.external_dodo_api import DatabaseAPI, DodoAPI, AuthAPI
from services.period import Period


def main():
    config_file_path = pathlib.Path(__file__).parent.parent / 'config.toml'
    config = load_config(config_file_path)

    stop_sales_period = Period.today_to_this_time()

    with httpx.Client(base_url=config.api.database_api_base_url) as database_client:
        units = DatabaseAPI(database_client).get_units()
    units = UnitsConverter(units)

    stop_sales: list[models.StopSaleBySector] = []
    with httpx.Client(base_url=config.api.auth_api_base_url) as auth_client:
        with httpx.Client(base_url=config.api.dodo_api_base_url) as dodo_api_client:
            auth_api = AuthAPI(auth_client)
            dodo_api = DodoAPI(dodo_api_client)
            for account_name, grouped_units in units.grouped_by_account_name.items():
                account_cookies = auth_api.get_account_cookies(account_name)
                stop_sales += dodo_api.get_stop_sales_by_sectors(
                    unit_ids=grouped_units.ids,
                    cookies=account_cookies.cookies,
                    period=stop_sales_period,
                )

    with message_queue.get_message_queue_channel(config.message_queue.rabbitmq_url) as message_queue_channel:
        for stop_sale in stop_sales:
            if stop_sale.staff_name_who_resumed is not None:
                continue
            event = StopSaleBySectorEvent(
                unit_id=units.unit_name_to_id[stop_sale.unit_name],
                stop_sale=stop_sale,
            )
            message_queue.send_json_message(message_queue_channel, event)


if __name__ == '__main__':
    main()
