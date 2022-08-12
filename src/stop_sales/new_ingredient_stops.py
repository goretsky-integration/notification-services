import asyncio
import collections
import itertools
from datetime import datetime
from typing import Iterable

from dodolib import DodoAPIClient, AuthClient, DatabaseClient
from dodolib.models import AuthToken, StopSaleByIngredients
from dodolib.utils.convert_models import UnitsConverter
from dotenv import load_dotenv
from pydantic import BaseModel

load_dotenv()

from rabbitmq import add_notification_to_queue
from storage import get_ingredient_names_by_unit_name, add_ingredient_names, init_db


class IngredientStop(BaseModel):
    started_at: datetime
    reason: str
    name: str


class StopSalesByIngredients(BaseModel):
    unit_name: str
    ingredients: list[IngredientStop]


def to_payload(unit_name: str, stop_sales_by_ingredients: Iterable[StopSaleByIngredients]) -> dict:
    ingredient_stops = [
        IngredientStop(
            started_at=stop_sale.started_at,
            reason=stop_sale.reason,
            name=stop_sale.ingredient_name,
        ) for stop_sale in stop_sales_by_ingredients
    ]
    return StopSalesByIngredients(unit_name=unit_name, ingredients=ingredient_stops).dict()


def group_stop_sales_by_unit_name(
        stop_sales: Iterable[StopSaleByIngredients],
) -> dict[str, list[StopSaleByIngredients]]:
    unit_name_to_stop_sales: dict[str, list[StopSaleByIngredients]] = collections.defaultdict(list)
    for stop_sale in stop_sales:
        stop_sales_by_unit_name = unit_name_to_stop_sales[stop_sale.unit_name]
        stop_sales_by_unit_name.append(stop_sale)
    return unit_name_to_stop_sales


async def main():
    init_db()
    async with (
        DatabaseClient() as db_client,
        AuthClient() as auth_client,
        DodoAPIClient() as api_client,
    ):
        units = UnitsConverter(await db_client.get_units())
        unit_names_to_ids = units.names_to_ids
        account_names_to_unit_uuids = units.account_names_to_unit_uuids
        tasks = (auth_client.get_tokens(account_name) for account_name in units.account_names)
        accounts_tokens: tuple[AuthToken, ...] = await asyncio.gather(*tasks)
        tasks = (api_client.get_stop_sales_by_ingredients(account_tokens.access_token,
                                                          account_names_to_unit_uuids[account_tokens.account_name])
                 for account_tokens in accounts_tokens)
        all_stop_sales_by_ingredients: tuple[list[StopSaleByIngredients], ...] = await asyncio.gather(*tasks)
        stop_sales_by_ingredients = itertools.chain.from_iterable(all_stop_sales_by_ingredients)

    for unit_name, stop_sales in group_stop_sales_by_unit_name(stop_sales_by_ingredients).items():
        ingredient_names_in_db = get_ingredient_names_by_unit_name(unit_name)
        stop_sales = [stop_sale for stop_sale in stop_sales
                      if stop_sale.staff_name_who_resumed is None
                      and stop_sale.ingredient_name not in ingredient_names_in_db]
        if not stop_sales:
            continue
        body = {
            'unit_id': unit_names_to_ids[unit_name],
            'type': 'STOPS_AND_RESUMES',
            'payload': to_payload(unit_name, stop_sales),
        }
        add_notification_to_queue(body)
        add_ingredient_names(unit_name, *[stop_sale.ingredient_name for stop_sale in stop_sales])


if __name__ == '__main__':
    asyncio.run(main())
