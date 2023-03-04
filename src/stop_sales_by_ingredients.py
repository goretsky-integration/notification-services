import functools
import logging
import pathlib
from argparse import ArgumentParser

import httpx

from core import setup_logging
from core.config import load_config
from filters import predicates, filter_by_predicates
from message_queue_events import StopSaleByIngredientEvent, DailyIngredientStopEvent
from services import message_queue
from services.converters import UnitsConverter
from services.external_dodo_api import AuthAPI, DodoAPI, DatabaseAPI
from services.period import Period
from services.storages import ObjectUUIDStorage
from shortcuts.auth_service import get_account_credentials_batch
from shortcuts.dodo_api_service import get_stop_sales_v2_batch
from shortcuts.stop_sales import group_stop_sales_by_unit_names


def main():
    argument_parser = ArgumentParser(
        prog='Stop sales V2 notifications',
        description='Generate events for stop sales V2',
    )
    argument_parser.add_argument(
        '--remember',
        action='store_true',
        help='Save stop sale\'s IDs in the local storage',
    )
    argument_parser.add_argument(
        '--ignore-remembered',
        action='store_true',
        help='Ignore if stop sale\'s ID in the local storage',
    )
    argument_parser.add_argument(
        '--only-partial-ingredients',
        action='store_true',
        help='Filter only partial ingredients in the config file',
    )
    argument_parser.add_argument(
        '--include-empty-units',
        action='store_true',
        help='Create event even if unit has no stop sales',
    )

    arguments = argument_parser.parse_args()

    period_today = Period.today_to_this_time()

    storage_file_path = pathlib.Path.joinpath(pathlib.Path(__file__).parent.parent, 'local_storage',
                                              'daily_ingredient_stops.db')

    config_file_path = pathlib.Path(__file__).parent.parent / 'config.toml'
    config = load_config(config_file_path)

    setup_logging(loglevel=config.logging.level, logfile_path=config.logging.file_path)

    with httpx.Client(base_url=config.api.database_api_base_url) as http_client:
        database_api = DatabaseAPI(http_client)
        units = UnitsConverter(database_api.get_units())

    with httpx.Client(base_url=config.api.auth_api_base_url) as http_client:
        auth_api = AuthAPI(http_client)
        accounts_credentials = get_account_credentials_batch(
            retrieve_account_credentials=auth_api.get_account_tokens,
            account_names=units.account_names,
        )

    for account_name in accounts_credentials.errors:
        logging.warning(f'Could not retrieve credentials for account {account_name}')

    with httpx.Client(base_url=config.api.dodo_api_base_url, timeout=30) as http_client:
        dodo_api = DodoAPI(http_client)

        stop_sales = get_stop_sales_v2_batch(
            retrieve_stop_sales=dodo_api.get_stop_sales_by_ingredients,
            account_tokens=accounts_credentials.result,
            country_code=config.country_code,
            units=units,
            period=period_today,
        )

    with ObjectUUIDStorage(storage_file_path) as storage:

        used_predicates = [predicates.is_stop_sale_v2_stopped]

        if arguments.only_partial_ingredients:
            used_predicates.append(
                functools.partial(
                    predicates.is_ingredient_name_not_blocked,
                    disallowed_ingredient_names=config.partial_ingredients.disallowed_ingredient_names
                )
            )
            used_predicates.append(
                functools.partial(
                    predicates.is_ingredient_name_allowed,
                    allowed_ingredient_names=config.partial_ingredients.allowed_ingredient_names,
                )
            )

        if arguments.ignore_remembered:
            used_predicates.append(functools.partial(predicates.is_object_uuid_not_in_storage, storage=storage))

        logging.debug(f'Used predicates: {used_predicates}')

        filtered_stop_sales = filter_by_predicates(stop_sales.result, *used_predicates)

    if arguments.only_partial_ingredients:
        events = [
            StopSaleByIngredientEvent(
                unit_id=units.unit_uuid_to_id[stop_sale.unit_uuid],
                stop_sale=stop_sale,
            ) for stop_sale in filtered_stop_sales
        ]
    else:
        stop_sales_grouped_by_unit_name = group_stop_sales_by_unit_names(filtered_stop_sales)

        events = [
            DailyIngredientStopEvent(
                unit_id=units.unit_name_to_id[unit_name],
                unit_name=unit_name,
                stop_sales=grouped_stop_sales,
            ) for unit_name, grouped_stop_sales in stop_sales_grouped_by_unit_name.items()
        ]

        if arguments.include_empty_units:
            unit_names_with_stop_sales = set(stop_sales_grouped_by_unit_name)
            unit_names_without_stop_sales = units.names - unit_names_with_stop_sales

            events += [
                DailyIngredientStopEvent(
                    unit_id=units.unit_name_to_id[unit_name],
                    unit_name=unit_name,
                    stop_sales=[],
                ) for unit_name in unit_names_without_stop_sales
            ]

    logging.debug(events)

    with message_queue.get_message_queue_channel(config.message_queue.rabbitmq_url) as message_queue_channel:
        message_queue.send_events(message_queue_channel, events)

    if arguments.remember:

        with ObjectUUIDStorage(storage_file_path) as storage:

            for stop_sale in filtered_stop_sales:
                storage.insert(stop_sale.uuid)


if __name__ == '__main__':
    main()
