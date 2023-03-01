import logging
from typing import Callable, TypeVar, Iterable

import models
from services.converters import UnitsConverter
from services.period import Period

StopSalesT = TypeVar('StopSalesT')


def get_stop_sales_v2_batch(
        *,
        retrieve_stop_sales: Callable[..., list[StopSalesT] | tuple[StopSalesT, ...]],
        account_tokens: Iterable[models.AccountTokens],
        country_code: str,
        units: UnitsConverter,
        period: Period,
        attempts_count: int = 3
) -> models.StopSalesBatchResponse[StopSalesT]:
    result: list[StopSalesT] = []
    error_unit_ids: list[int] = []
    for account_token in account_tokens:
        units_stop_sales_to_retrieve = units.grouped_by_account_name[account_token.account_name]
        for _ in range(attempts_count):
            try:
                stop_sales = retrieve_stop_sales(
                    country_code=country_code,
                    unit_uuids=units_stop_sales_to_retrieve.uuids,
                    token=account_token.access_token,
                    period=period,
                )
            except Exception:
                logging.exception(f'Could not retrieve stop sales for {units_stop_sales_to_retrieve.ids}. Trying again')
            else:
                result += stop_sales
                break
        else:
            error_unit_ids += units_stop_sales_to_retrieve.ids
            logging.exception(f'Could not eventually retrieve stop sales for {units_stop_sales_to_retrieve.ids}')
    return models.StopSalesBatchResponse(result=result, error_unit_ids=error_unit_ids)
