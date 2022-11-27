import asyncio
import collections
import contextlib
import datetime
import itertools
import pathlib
import uuid
from typing import Iterable

import httpx
from dodolib import DodoAPIClient, AuthClient, DatabaseClient, models
from dodolib.models import AuthToken, StopSaleByIngredients
from dodolib.utils.convert_models import UnitsConverter
from dodolib.utils.exceptions import DodoAPIError

from message_queue import get_message_queue_channel, send_json_message
from storages import IngredientStopSaleIDsStorage

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
    storage_path = pathlib.Path.joinpath(pathlib.Path(__file__).parent.parent, 'local_storage', 'ingredient_stops.json')

    app_settings = get_app_settings()
    country_code = 'ru'
    end = datetime.datetime.utcnow() - datetime.timedelta(hours=3)
    start = end.replace(hour=0, minute=0, second=0, microsecond=0)

    async with DatabaseClient(app_settings.database_api_base_url) as db_client:
        units = UnitsConverter(await db_client.get_units())

    async with AuthClient(app_settings.auth_service_base_url) as auth_client:
        tasks = (auth_client.get_tokens(account_name) for account_name in units.account_names)
        tokens = await asyncio.gather(*tasks)

    stop_sales: list[models.StopSaleByIngredients] = []
    account_names_to_unit_uuids = units.account_names_to_unit_uuids
    async with DodoAPIClient() as api_client:
        for account_token in tokens:
            for _ in range(5):
                with contextlib.suppress(DodoAPIError, httpx.HTTPError):
                    stop_sales += await api_client.get_stop_sales_by_ingredients(
                        token=account_token.access_token,
                        country_code=country_code,
                        unit_uuids=account_names_to_unit_uuids[account_token.account_name],
                        start=start,
                        end=end,
                    )
                    break

    with IngredientStopSaleIDsStorage(storage_path) as storage:
        with get_message_queue_channel() as message_queue_channel:
            stop_sales = [stop_sale for stop_sale in stop_sales if not storage.is_exist(stop_sale.id)]
            unit_name_to_id = units.names_to_ids
            unit_name_to_stop_sales = group_stop_sales_by_unit_name(stop_sales)
            for unit_name, units_stop_sales in unit_name_to_stop_sales.items():
                message_payload = to_payload(unit_name, units_stop_sales)
                message_body = {
                    'unit_id': unit_name_to_id[unit_name],
                    'type': 'STOPS_AND_RESUMES',
                    'payload': message_payload,
                }
                send_json_message(message_queue_channel, message_body)
            for stop_sale in stop_sales:
                storage.add_uuid(stop_sale.id)


if __name__ == '__main__':
    asyncio.run(main())
