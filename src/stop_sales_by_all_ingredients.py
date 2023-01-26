import collections
import pathlib
from typing import Iterable, DefaultDict

import httpx

import models
from config import load_config
from message_queue_events import DailyIngredientStopEvent
from services import message_queue
from services.converters import UnitsConverter
from services.external_dodo_api import DatabaseAPI, DodoAPI, AuthAPI
from services.period import Period


def group_stop_sales_by_unit_names(
        stop_sales: Iterable[models.StopSaleByIngredient],
) -> DefaultDict[str, list[models.StopSaleByIngredient]]:
    unit_name_to_stop_sales = collections.defaultdict(list)
    for stop_sale in stop_sales:
        unit_name_to_stop_sales[stop_sale.unit_name].append(stop_sale)
    return unit_name_to_stop_sales


def main():
    config_file_path = pathlib.Path(__file__).parent.parent / 'config.toml'
    config = load_config(config_file_path)

    stop_sales_period = Period.today_to_this_time()

    with httpx.Client(base_url=config.api.database_api_base_url) as database_client:
        units = DatabaseAPI(database_client).get_units()
    units = UnitsConverter(units)

    stop_sales: list[models.StopSaleByIngredient] = []
    with httpx.Client(base_url=config.api.auth_api_base_url) as auth_client:
        with httpx.Client(base_url=config.api.dodo_api_base_url) as dodo_api_client:
            auth_api = AuthAPI(auth_client)
            dodo_api = DodoAPI(dodo_api_client)
            for account_name, grouped_units in units.grouped_by_account_name.items():
                account_tokens = auth_api.get_account_tokens(account_name)
                stop_sales += dodo_api.get_stop_sales_by_ingredients(
                    country_code=config.country_code,
                    unit_uuids=grouped_units.uuids,
                    token=account_tokens.access_token,
                    period=stop_sales_period,
                )

    with message_queue.get_message_queue_channel(config.message_queue.rabbitmq_url) as message_queue_channel:
        stop_sales_grouped_by_unit_name = group_stop_sales_by_unit_names(stop_sales)
        for unit_name, grouped_stop_sales in stop_sales_grouped_by_unit_name.items():
            event = DailyIngredientStopEvent(
                unit_id=units.unit_name_to_id[unit_name],
                unit_name=unit_name,
                stop_sales=grouped_stop_sales,
            )
            message_queue.send_json_message(message_queue_channel, event)


if __name__ == '__main__':
    main()
