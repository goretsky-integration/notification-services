import asyncio
import datetime

from dodolib import DatabaseClient, AuthClient, DodoAPIClient, models
from dodolib.utils.convert_models import UnitsConverter

from message_queue import get_message_queue_channel, send_json_message
from settings import get_app_settings


async def main():
    app_settings = get_app_settings()

    ended_at = datetime.datetime.utcnow() + datetime.timedelta(hours=3)
    started_at = ended_at.replace(hour=0, minute=0, second=0, microsecond=0)

    async with DatabaseClient(app_settings.database_api_base_url) as db_client:
        units = UnitsConverter(await db_client.get_units())

    async with AuthClient(app_settings.auth_service_base_url) as auth_client:
        tasks = (auth_client.get_cookies(account_name) for account_name in units.account_names)
        accounts_cookies = await asyncio.gather(*tasks)

    account_names_to_unit_ids = units.account_names_to_unit_ids
    async with DodoAPIClient(app_settings.dodo_api_base_url) as api_client:
        tasks = (api_client.get_stop_sales_by_sectors(account_cookies.cookies,
                                                      account_names_to_unit_ids[account_cookies.account_name],
                                                      started_at,
                                                      ended_at)
                 for account_cookies in accounts_cookies)
        all_stop_sales: tuple[list[models.StopSaleBySectors], ...] = await asyncio.gather(*tasks,
                                                                                          return_exceptions=True)
        stop_sales = [stop_sale for stop_sales in all_stop_sales
                      for stop_sale in stop_sales
                      if not isinstance(stop_sales, Exception)]

    unit_names_to_unit_ids = units.names_to_ids
    with get_message_queue_channel() as channel:
        for stop_sale in stop_sales:
            if stop_sale.staff_name_who_resumed is not None:
                continue
            message_body = {
                'unit_id': unit_names_to_unit_ids[stop_sale.unit_name],
                'type': 'SECTOR_STOP_SALES',
                'payload': {
                    'unit_name': stop_sale.unit_name,
                    'started_at': stop_sale.started_at,
                    'sector_name': stop_sale.sector,
                }
            }
            send_json_message(channel, message_body)


if __name__ == '__main__':
    asyncio.run(main())
