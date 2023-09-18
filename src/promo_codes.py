import collections
import functools
import logging
import pathlib

import httpx
from typing_extensions import DefaultDict

import models
from core import load_config_from_file
from filters import predicates, filter_by_predicates
from message_queue_events.used_promo_code import UsedPromoCodeEvent
from services import message_queue
from services.converters import UnitsConverter
from services.external_dodo_api import DodoAPI, DatabaseAPI, AuthAPI
from services.period import Period
from services.storages.used_promo_codes import UsedPromoCodesStorage
from shortcuts.auth_service import get_account_credentials_batch


def main():
    config_file_path = pathlib.Path(__file__).parent.parent / 'config.toml'
    storage_path = pathlib.Path.joinpath(pathlib.Path(__file__).parent.parent,
                                         'local_storage', 'used_promo_codes.db')

    config = load_config_from_file(config_file_path)

    period = Period.today_to_this_time()

    with httpx.Client(base_url=config.api.database_api_base_url) as http_client:
        database_api = DatabaseAPI(http_client)
        units = UnitsConverter(database_api.get_units())

    with httpx.Client(base_url=config.api.auth_api_base_url) as http_client:
        auth_api = AuthAPI(http_client)

        accounts_cookies = get_account_credentials_batch(
            retrieve_account_credentials=auth_api.get_account_cookies,
            account_names=units.office_manager_account_names,
        )

    units_promo_codes: list[models.UnitUsedPromoCode] = []
    with httpx.Client(base_url=config.api.dodo_api_base_url,
                      timeout=30) as http_client:
        dodo_api = DodoAPI(http_client)

        for account_cookies in accounts_cookies.result:
            for unit_id in units.grouped_by_office_manager_account_name[
                account_cookies.account_name].ids:

                try:
                    units_promo_codes += dodo_api.get_used_promo_codes(
                        cookies=account_cookies.cookies,
                        unit_id=unit_id,
                        country_code=config.country_code,
                        period=period,
                    )
                except Exception:
                    logging.exception(
                        f'Could not retrieve used promo-codes for unit {unit_id}')

    with UsedPromoCodesStorage(storage_path) as storage:
        used_predicates = [
            functools.partial(predicates.is_promo_code_not_in_storage,
                              storage=storage),
        ]
        filtered_promo_codes = filter_by_predicates(units_promo_codes,
                                                    *used_predicates)

    unit_id_to_promo_codes: DefaultDict[
        int, list[models.UnitUsedPromoCode]] = collections.defaultdict(list)
    for unit_used_promo_code in filtered_promo_codes:
        unit_id_to_promo_codes[unit_used_promo_code.unit_id].append(
            unit_used_promo_code)

    events = [
        UsedPromoCodeEvent(unit_id=unit_id,
                           unit_name=units.unit_id_to_name[unit_id],
                           used_promo_codes=promo_codes)
        for unit_id, promo_codes in unit_id_to_promo_codes.items()
    ]

    with message_queue.get_message_queue_channel(
            config.message_queue.rabbitmq_url) as message_queue_channel:
        message_queue.send_events(message_queue_channel, events)

    with UsedPromoCodesStorage(storage_path) as storage:
        for promo_code in filtered_promo_codes:
            storage.insert(unit_id=promo_code.unit_id,
                           promo_code=promo_code.promo_code,
                           order_no=promo_code.order_no)


if __name__ == '__main__':
    main()
