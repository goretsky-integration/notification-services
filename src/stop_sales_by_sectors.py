import pathlib

import httpx
from dodo_is_api.connection import DodoISAPIConnection
from dodo_is_api.models import StopSaleBySector, CountryCode

from core.config import load_config_from_file
from filters import filter_by_predicates
from filters.predicates import is_stop_sale_v2_stopped
from message_queue_events import StopSaleBySectorEvent
from services import message_queue
from services.converters import UnitsConverter
from services.external_dodo_api import DatabaseAPI, AuthAPI
from services.message_queue import send_events
from services.period import Period
from shortcuts.auth_service import get_account_credentials_batch


def main() -> None:
    config_file_path = pathlib.Path(__file__).parent.parent / 'config.toml'
    config = load_config_from_file(config_file_path)

    period_today = Period.today_to_this_time()

    with httpx.Client(
            timeout=120,
            base_url=config.api.database_api_base_url,
    ) as http_client:
        database_api = DatabaseAPI(http_client)
        units = database_api.get_units()

    units_set = UnitsConverter(units)

    with httpx.Client(
            timeout=120,
            base_url=config.api.auth_api_base_url,
    ) as http_client:
        auth_api = AuthAPI(http_client)
        accounts_credentials = get_account_credentials_batch(
            retrieve_account_credentials=auth_api.get_account_tokens,
            account_names=units_set.dodo_is_api_account_names,
        )

    stop_sales: list[StopSaleBySector] = []
    for account_tokens in accounts_credentials.result:
        with httpx.Client(timeout=120) as http_client:
            dodo_is_api_connection = DodoISAPIConnection(
                http_client=http_client,
                country_code=CountryCode(config.country_code),
                access_token=account_tokens.access_token,
            )
            stop_sales += dodo_is_api_connection.get_stop_sales_by_sectors(
                from_date=period_today.start,
                to_date=period_today.end,
                units=units_set.grouped_by_dodo_is_api_account_name[
                    account_tokens.account_name].uuids,
            )

    predicates = [is_stop_sale_v2_stopped]

    stop_sales = filter_by_predicates(stop_sales, *predicates)

    events = [
        StopSaleBySectorEvent(
            unit_id=units_set.unit_uuid_to_id[stop_sale.unit_uuid],
            stop_sale=stop_sale,
        ) for stop_sale in stop_sales
    ]

    with message_queue.get_message_queue_channel(
            rabbitmq_url=config.message_queue.rabbitmq_url,
    ) as message_queue_channel:
        send_events(
            channel=message_queue_channel,
            events=events,
        )


if __name__ == '__main__':
    main()
