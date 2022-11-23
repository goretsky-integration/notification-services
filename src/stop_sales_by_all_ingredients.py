import asyncio
import collections
import datetime
from typing import Iterable

from dodolib import DodoAPIClient, AuthClient, DatabaseClient, models
from dodolib.models import StopSaleByIngredients
from dodolib.utils.convert_models import UnitsConverter

from message_queue import send_json_message, get_message_queue_channel
from settings import get_app_settings


def to_payload(unit_name: str, stop_sales_by_ingredients: Iterable[StopSaleByIngredients]) -> dict:
    ingredient_stops = [
        {
            'started_at': stop_sale.started_at,
            'reason': stop_sale.reason,
            'name': stop_sale.ingredient_name,
        } for stop_sale in stop_sales_by_ingredients
    ]
    return {'unit_name': unit_name, 'ingredients': ingredient_stops, }


def group_stop_sales_by_unit_name(
        stop_sales: Iterable[StopSaleByIngredients],
) -> dict[str, list[StopSaleByIngredients]]:
    unit_name_to_stop_sales: dict[str, list[StopSaleByIngredients]] = collections.defaultdict(list)
    for stop_sale in stop_sales:
        stop_sales_by_unit_name = unit_name_to_stop_sales[stop_sale.unit_name]
        stop_sales_by_unit_name.append(stop_sale)
    return unit_name_to_stop_sales


async def main():
    app_settings = get_app_settings()
    country_code = 'ru'
    end = datetime.datetime.utcnow() - datetime.timedelta(hours=3)
    start = end.replace(hour=0, minute=0, second=0, microsecond=0)

    async with DatabaseClient(app_settings.database_api_base_url) as db_client:
        units = UnitsConverter(await db_client.get_units())

    async with AuthClient(app_settings.auth_service_base_url) as auth_client:
        tasks = (auth_client.get_tokens(account_name) for account_name in units.account_names)
        tokens = await asyncio.gather(*tasks)

    account_names_to_unit_uuids = units.account_names_to_unit_uuids
    async with DodoAPIClient() as api_client:
        tasks = (
            api_client.get_stop_sales_by_ingredients(
                token=account_token.access_token,
                country_code=country_code,
                unit_uuids=account_names_to_unit_uuids[account_token.account_name],
                start=start,
                end=end,
            )
            for account_token in tokens)
        all_stop_sales: tuple[list[models.StopSaleByIngredients], ...] = await asyncio.gather(*tasks,
                                                                                              return_exceptions=True)
        stop_sales = []
        for stop_sales_group in all_stop_sales:
            if isinstance(stop_sales_group, Exception):
                continue
            stop_sales += stop_sales_group

    unit_names_to_ids = units.names_to_ids
    with get_message_queue_channel() as channel:
        for unit_name, units_stop_sales in group_stop_sales_by_unit_name(stop_sales).items():
            not_resumed_stop_sales = [stop_sale for stop_sale in units_stop_sales
                                      if stop_sale.resumed_by_user_id is None]
            message_body = {
                'unit_id': unit_names_to_ids[unit_name],
                'type': 'STOPS_AND_RESUMES',
                'payload': to_payload(unit_name, not_resumed_stop_sales),
            }
            send_json_message(channel, message_body)


if __name__ == '__main__':
    asyncio.run(main())
