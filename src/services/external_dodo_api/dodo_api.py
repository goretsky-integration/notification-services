from typing import Iterable

from pydantic import parse_obj_as

import models
from services.external_dodo_api.base import APIService
from services.period import Period

__all__ = ('DodoAPI',)


class DodoAPI(APIService):

    def get_stocks_balance(
            self,
            *,
            country_code: str,
            unit_ids: Iterable[int],
            cookies: dict,
            days_left_threshold: int,
    ) -> models.StocksBalanceReport:
        request_query_params = {
            'days_left_threshold': days_left_threshold,
            'unit_ids': tuple(unit_ids),
        }
        response = self._client.get(f'/v1/{country_code}/stocks',
                                    cookies=cookies,
                                    params=request_query_params)
        return models.StocksBalanceReport.parse_obj(response.json())

    def get_cheated_orders(
            self,
            *,
            unit_ids_and_names: Iterable[dict],
            cookies: dict,
            country_code: str,
            repeated_phone_number_count_threshold: int,
    ) -> tuple[models.CommonPhoneNumberOrders, ...]:
        request_data = {
            'units': tuple(unit_ids_and_names),
            'repeated_phone_number_count_threshold': repeated_phone_number_count_threshold,
        }
        response = self._client.post(f'/v1/{country_code}/cheated-orders',
                                     cookies=cookies, json=request_data)
        return parse_obj_as(tuple[models.CommonPhoneNumberOrders, ...],
                            response.json())

    def get_canceled_orders(
            self,
            *,
            cookies: dict,
            period: Period,
            country_code: str,
    ) -> tuple[models.CanceledOrder, ...]:
        response = self._client.get(
            f'/v1/{country_code}/canceled-orders',
            cookies=cookies,
            params={
                'start': period.start.isoformat(),
                'end': period.end.isoformat(),
            }
        )
        return parse_obj_as(tuple[models.CanceledOrder, ...], response.json())

    def get_used_promo_codes(
            self,
            *,
            unit_id: int,
            cookies: dict,
            country_code: str,
            period: Period,
    ) -> tuple[models.UnitUsedPromoCode, ...]:
        request_query_params = {
            'start': period.start.isoformat(), 'end': period.end.isoformat()
        }
        url = f'/v1/{country_code}/used-promo-codes/{unit_id}'
        response = self._client.get(url, cookies=cookies,
                                    params=request_query_params)
        response_data = response.json()
        return parse_obj_as(tuple[models.UnitUsedPromoCode, ...], response_data)
