import functools
import pathlib

import httpx
from dodo_is_api.connection import DodoISAPIConnection
from dodo_is_api.connection.http_clients import closing_http_client
from dodo_is_api.mappers import map_late_delivery_voucher_dto
from dodo_is_api.models import LateDeliveryVoucher

from core import load_config_from_file
from filters import predicates, filter_by_predicates
from message_queue_events import LateDeliveryVouchersEvent
from services import message_queue
from services.converters import UnitsConverter
from services.external_dodo_api import DatabaseAPI, AuthAPI
from services.mappers import group_by_unit_uuid
from services.period import Period
from services.storages import ObjectUUIDStorage
from shortcuts.auth_service import get_account_credentials_batch


def main():
    storage_path = pathlib.Path.joinpath(pathlib.Path(__file__).parent.parent, 'local_storage',
                                         'late_delivery_vouchers.db')
    config_file_path = pathlib.Path(__file__).parent.parent / 'config.toml'
    config = load_config_from_file(config_file_path)

    period = Period.today_to_this_time()

    with httpx.Client(base_url=config.api.database_api_base_url) as http_client:
        units = UnitsConverter(DatabaseAPI(http_client).get_units())

    with httpx.Client(base_url=config.api.auth_api_base_url) as http_client:
        auth_api = AuthAPI(http_client)
        accounts_tokens = get_account_credentials_batch(
            retrieve_account_credentials=auth_api.get_account_tokens,
            account_names=units.office_manager_account_names
        )

    late_delivery_vouchers: list[LateDeliveryVoucher] = []
    for account_tokens in accounts_tokens.result:

        with closing_http_client(
                access_token=account_tokens.access_token,
                country_code=config.country_code,
        ) as http_client:

            dodo_is_api_connection = DodoISAPIConnection(http_client=http_client)

            late_delivery_vouchers_iterator = dodo_is_api_connection.iter_late_delivery_vouchers(
                from_date=period.start,
                to_date=period.end,
                units=units.grouped_by_dodo_is_api_account_name[account_tokens.account_name].uuids,
            )

            for units_late_delivery_vouchers in late_delivery_vouchers_iterator:
                late_delivery_vouchers += [
                    map_late_delivery_voucher_dto(late_delivery_voucher)
                    for late_delivery_voucher in units_late_delivery_vouchers
                ]

    with ObjectUUIDStorage(storage_path) as storage:
        used_predicates = [
            functools.partial(predicates.is_object_uuid_not_in_storage, storage=storage, key='order_id'),
        ]

        filtered_late_delivery_vouchers = filter_by_predicates(late_delivery_vouchers, *used_predicates)

    late_delivery_vouchers_grouped_by_unit_uuid = group_by_unit_uuid(filtered_late_delivery_vouchers)

    events = [
        LateDeliveryVouchersEvent(
            unit_id=units.unit_uuid_to_id[unit_uuid],
            unit_name=units.unit_uuid_to_name[unit_uuid],
            late_delivery_vouchers=late_delivery_vouchers,
        ) for unit_uuid, late_delivery_vouchers in late_delivery_vouchers_grouped_by_unit_uuid.items()
    ]

    with message_queue.get_message_queue_channel(config.message_queue.rabbitmq_url) as message_queue_channel:
        message_queue.send_events(message_queue_channel, events)

    with ObjectUUIDStorage(storage_path) as storage:
        for late_delivery_voucher in filtered_late_delivery_vouchers:
            storage.insert(late_delivery_voucher.order_id)


if __name__ == '__main__':
    main()
