import pathlib

import httpx

from config import load_config
from filters import predicates, filter_by_predicates
from message_queue_events import DailyIngredientStopEvent
from services import message_queue
from services.converters import UnitsConverter
from services.external_dodo_api import DatabaseAPI, DodoAPI, AuthAPI
from services.period import Period
from shortcuts.stop_sales import get_stop_sales_v2, group_stop_sales_by_unit_names


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
            stop_sales = get_stop_sales_v2(
                dodo_api_method=dodo_api.get_stop_sales_by_ingredients,
                auth_api=auth_api,
                units=units,
                country_code=config.country_code,
                period=stop_sales_period,
            )
    filtered_stop_sales = filter_by_predicates(stop_sales, predicates.is_stop_sale_v2_stopped)
    stop_sales_grouped_by_unit_name = group_stop_sales_by_unit_names(filtered_stop_sales)
    events = [
        DailyIngredientStopEvent(
            unit_id=units.unit_name_to_id[unit_name],
            unit_name=unit_name,
            stop_sales=grouped_stop_sales,
        ) for unit_name, grouped_stop_sales in stop_sales_grouped_by_unit_name.items()
    ]
    with message_queue.get_message_queue_channel(config.message_queue.rabbitmq_url) as message_queue_channel:
        message_queue.send_events(message_queue_channel, events)


if __name__ == '__main__':
    main()
