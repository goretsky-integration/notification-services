import pathlib
from typing import Iterable

import httpx

import models
from config import load_config
from message_queue_events import StopSaleByIngredientEvent
from services import message_queue
from services.converters import UnitsConverter
from services.external_dodo_api import DatabaseAPI, DodoAPI, AuthAPI
from services.period import Period


class IngredientNameFilter:

    def __init__(self, allowed_ingredient_names: Iterable[str], disallowed_ingredient_names: Iterable[str]):
        self.__allowed_ingredient_names = allowed_ingredient_names
        self.__disallowed_ingredient_names = disallowed_ingredient_names

    def is_allowed(self, ingredient_name: str) -> bool:
        ingredient_name = ingredient_name.lower().strip()
        for disallowed_ingredient_name in self.__disallowed_ingredient_names:
            if disallowed_ingredient_name.lower().strip() in ingredient_name:
                return False
        for allowed_ingredient_name in self.__allowed_ingredient_names:
            if allowed_ingredient_name.lower().strip() in ingredient_name:
                return True
        return False


def main():
    config_file_path = pathlib.Path(__file__).parent.parent / 'config.toml'
    config = load_config(config_file_path)

    ingredient_name_filter = IngredientNameFilter(
        allowed_ingredient_names=config.partial_ingredients.allowed_ingredient_names,
        disallowed_ingredient_names=config.partial_ingredients.disallowed_ingredient_names,
    )

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
        for stop_sale in stop_sales:
            if stop_sale.resumed_by_user_id is not None:
                continue
            if not ingredient_name_filter.is_allowed(stop_sale.ingredient_name):
                continue
            event = StopSaleByIngredientEvent(
                unit_id=units.unit_name_to_id[stop_sale.unit_name],
                stop_sale=stop_sale,
            )
            message_queue.send_json_message(message_queue_channel, event)


if __name__ == '__main__':
    main()
