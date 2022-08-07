from typing import Iterable
from uuid import UUID

from core import models
from core.rabbitmq import add_notification_to_queue
from core.repositories import (
    get_db_client,
    get_auth_client,
    get_dodo_api_client,
    DodoAPIRepository,
    DatabaseRepository,
    AuthCredentialsRepository,
)
from core.utils import exceptions
from core.utils.convert_models import UnitsConverter


def get_stop_sales(
        dodo_api_client: DodoAPIRepository,
        tokens_and_unit_uuids: Iterable[tuple[models.AuthToken, Iterable[UUID]]],
) -> list[models.StopSaleBySalesChannels]:
    stop_sales = []
    for token, unit_uuids in tokens_and_unit_uuids:
        for _ in range(3):
            try:
                stop_sales += dodo_api_client.get_stop_sales_by_channels(token.access_token, unit_uuids)
                break
            except exceptions.DodoAPIError:
                continue
    return stop_sales


def get_tokens_and_unit_uuids(
        auth_client: AuthCredentialsRepository,
        account_names_to_unit_uuids: dict[str, Iterable[UUID]],
) -> list[tuple[models.AuthToken, Iterable[UUID]]]:
    tokens_and_unit_uuids: list[tuple[models.AuthToken, Iterable[UUID]]] = []
    for account_name, unit_uuids in account_names_to_unit_uuids.items():
        for _ in range(3):
            try:
                token = auth_client.get_tokens(account_name)
            except exceptions.NoTokenError:
                break
            except Exception:
                continue
            else:
                tokens_and_unit_uuids.append((token, unit_uuids))
                break
    return tokens_and_unit_uuids


def get_units(db_client: DatabaseRepository) -> UnitsConverter:
    return UnitsConverter(db_client.get_units())


def to_payload(stop_sale: models.StopSaleBySalesChannels) -> dict:
    return {
        'unit_name': stop_sale.unit_name,
        'started_at': stop_sale.started_at,
        'sales_channel_name': stop_sale.sales_channel_name,
        'reason': stop_sale.reason,
    }


def main():
    with (
        get_db_client() as db_client,
        get_auth_client() as auth_client,
        get_dodo_api_client() as dodo_api_client,
    ):
        units = get_units(db_client)
        tokens_and_unit_uuids = get_tokens_and_unit_uuids(auth_client, units.account_names_to_unit_uuids)
        stop_sales = get_stop_sales(dodo_api_client, tokens_and_unit_uuids)

    unit_uuid_to_unit_id = units.uuids_to_ids
    for stop_sale in stop_sales:
        body = {
            'unit_id': unit_uuid_to_unit_id[stop_sale.unit_uuid],
            'type': 'PIZZERIA_STOP_SALES',
            'payload': to_payload(stop_sale),
        }
        add_notification_to_queue(body)


if __name__ == '__main__':
    main()
