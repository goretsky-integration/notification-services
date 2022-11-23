import asyncio
import datetime

from dodolib import DatabaseClient, AuthClient, DodoAPIClient, models
from dodolib.utils.convert_models import UnitsConverter

from message_queue import send_json_message, get_message_queue_channel
from settings import get_app_settings

ALLOWED_INGREDIENT_NAMES = {
    'моцарелла',
    'пицца-соус',
    'тесто',
}


def is_ingredient_name_allowed(ingredient_name: str) -> bool:
    for allowed_ingredient_name in ALLOWED_INGREDIENT_NAMES:
        if allowed_ingredient_name.lower().strip() in ingredient_name:
            return True
    return False


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

    unit_uuids_to_ids = units.uuids_to_ids
    with get_message_queue_channel() as channel:
        for stop_sale in stop_sales:
            if stop_sale.resumed_by_user_id is not None:
                continue
            if not is_ingredient_name_allowed(stop_sale.ingredient_name):
                continue

            message_body = {
                'unit_id': unit_uuids_to_ids[stop_sale.unit_uuid],
                'type': 'INGREDIENTS_STOP_SALES',
                'payload': {
                    'unit_name': stop_sale.unit_name,
                    'started_at': stop_sale.started_at,
                    'ingredient_name': stop_sale.ingredient_name,
                    'reason': stop_sale.reason,
                },
            }
            send_json_message(channel, message_body)


if __name__ == '__main__':
    asyncio.run(main())
