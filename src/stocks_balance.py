import pathlib

import httpx

from core import load_config_from_file, setup_logging
from message_queue_events import StocksBalanceEvent
from services import message_queue
from services.converters import UnitsConverter
from services.external_dodo_api import DatabaseAPI, DodoAPI, AuthAPI
from shortcuts.stocks_balance import get_stocks_balance, group_stocks_balance_by_unit_id


def main():
    config_file_path = pathlib.Path(__file__).parent.parent / 'config.toml'
    config = load_config_from_file(config_file_path)

    setup_logging(loglevel=config.logging.level, logfile_path=config.logging.file_path)

    with httpx.Client(base_url=config.api.database_api_base_url) as database_client:
        units = DatabaseAPI(database_client).get_units()
    units = UnitsConverter(units)

    with httpx.Client(base_url=config.api.auth_api_base_url) as auth_client:
        with httpx.Client(base_url=config.api.dodo_api_base_url, timeout=60) as dodo_api_client:
            auth_api = AuthAPI(auth_client)
            dodo_api = DodoAPI(dodo_api_client)
            stocks_balance = get_stocks_balance(dodo_api=dodo_api, auth_api=auth_api,
                                                units=units, country_code=config.country_code)
    running_out_stocks_grouped_by_unit_id = group_stocks_balance_by_unit_id(stocks_balance)
    unit_ids_without_running_out_stocks = units.ids - set(running_out_stocks_grouped_by_unit_id)
    events_with_running_out_stocks = [
        StocksBalanceEvent(
            unit_id=unit_id,
            unit_name=units.unit_id_to_name[unit_id],
            units_stocks_balance=unit_stocks_balance,
        ) for unit_id, unit_stocks_balance in running_out_stocks_grouped_by_unit_id.items()
    ]
    events_without_running_out_stocks = [
        StocksBalanceEvent(
            unit_id=unit_id,
            unit_name=units.unit_id_to_name[unit_id],
            units_stocks_balance=[],
        ) for unit_id in unit_ids_without_running_out_stocks
    ]
    events = events_with_running_out_stocks + events_without_running_out_stocks
    with message_queue.get_message_queue_channel(config.message_queue.rabbitmq_url) as message_queue_channel:
        message_queue.send_events(message_queue_channel, events)


if __name__ == '__main__':
    main()
