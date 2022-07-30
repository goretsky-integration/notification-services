import collections
from typing import Generator, Iterable

from core import models
from core.repositories import get_db_client, get_auth_client, get_dodo_api_client
from core.utils import exceptions, logger
from core.utils.convert_models import UnitsConverter


def get_stop_sales() -> Generator[tuple[int, str, list[models.StopSaleByIngredients]], None, None]:
    with (
        get_db_client() as db_client,
        get_auth_client() as auth_client,
        get_dodo_api_client() as dodo_api_client,
    ):
        units = UnitsConverter(db_client.get_units())
        unit_name_to_id = units.names_to_ids
        for account_name, unit_uuids in units.account_names_to_unit_uuids.items():
            account_token = auth_client.get_tokens(account_name)
            try:
                stop_sales = dodo_api_client.get_stop_sales_by_ingredients(account_token.access_token, unit_uuids)
            except exceptions.DodoAPIError:
                logger.error(f'Ingredients {account_name} error')
                continue
            unit_name_to_stop_sales = group_stop_sales_by_unit_name(stop_sales)
            for unit_name, stop_sales in unit_name_to_stop_sales.items():
                yield unit_name_to_id[unit_name], unit_name, stop_sales


def group_stop_sales_by_unit_name(stop_sales: Iterable[models.StopSale]) -> dict[str, list[models.StopSale]]:
    unit_name_to_stop_sales: dict[str, list[models.StopSale]] = collections.defaultdict(list)
    for stop_sale in stop_sales:
        stop_sales_by_unit_name = unit_name_to_stop_sales[stop_sale.unit_name]
        stop_sales_by_unit_name.append(stop_sale)
    return unit_name_to_stop_sales
