import asyncio
import itertools

from dodolib import DatabaseClient, AuthClient, DodoAPIClient
from dodolib.models import AuthToken, StopSaleBySalesChannels
from dodolib.utils.convert_models import UnitsConverter
from dotenv import load_dotenv

load_dotenv()

from rabbitmq import add_notification_to_queue


def to_payload(stop_sale: StopSaleBySalesChannels) -> dict:
    return {
        'unit_name': stop_sale.unit_name,
        'started_at': stop_sale.started_at,
        'sales_channel_name': stop_sale.sales_channel_name,
        'reason': stop_sale.reason,
    }


async def main():
    async with (
        DatabaseClient() as db_client,
        AuthClient() as auth_client,
        DodoAPIClient() as api_client,
    ):
        units = UnitsConverter(await db_client.get_units())
        unit_uuids_to_ids = units.uuids_to_ids
        account_names_to_unit_uuids = units.account_names_to_unit_uuids
        tasks = (auth_client.get_tokens(account_name) for account_name in units.account_names)
        accounts_tokens: tuple[AuthToken, ...] = await asyncio.gather(*tasks)
        tasks = (api_client.get_stop_sales_by_channels(account_tokens.access_token,
                                                       account_names_to_unit_uuids[account_tokens.account_name])
                 for account_tokens in accounts_tokens)
        all_stop_sales_by_ingredients: tuple[list[StopSaleBySalesChannels], ...] = await asyncio.gather(*tasks)
        stop_sales_by_channels = itertools.chain.from_iterable(all_stop_sales_by_ingredients)

    for stop_sale in stop_sales_by_channels:
        if stop_sale.staff_name_who_resumed is not None:
            continue
        body = {
            'unit_id': unit_uuids_to_ids[stop_sale.unit_uuid],
            'type': 'PIZZERIA_STOP_SALES',
            'payload': to_payload(stop_sale),
        }
        add_notification_to_queue(body)


if __name__ == '__main__':
    asyncio.run(main())
