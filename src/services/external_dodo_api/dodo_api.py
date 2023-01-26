import datetime
from typing import Iterable
from uuid import UUID

from pydantic import parse_obj_as

import models
from services.external_dodo_api.base import APIService
from services.period import Period

__all__ = ('DodoAPI',)


class DodoAPI(APIService):
    def __get_stop_sales_v1(
            self,
            *,
            resource: str,
            unit_ids: Iterable[int],
            cookies: dict,
            period: Period,
    ) -> list[dict]:
        request_body = {
            'unit_ids': tuple(unit_ids),
            'cookies': cookies,
            'start': period.start.strftime('%Y-%m-%dT%H:%M:%S'),
            'end': period.end.strftime('%Y-%m-%dT%H:%M:%S'),
        }
        url = f'/v1/stop-sales/{resource}'
        response = self._client.post(url, json=request_body)
        return response.json()

    def get_stop_sales_by_sectors(
            self,
            *,
            unit_ids: Iterable[int],
            cookies: dict,
            period: Period,
    ) -> tuple[models.StopSaleBySector, ...]:
        resource = 'sectors'
        response_data = self.__get_stop_sales_v1(
            resource=resource,
            unit_ids=unit_ids,
            cookies=cookies,
            period=period,
        )
        return parse_obj_as(tuple[models.StopSaleBySector, ...], response_data)

    def get_stop_sales_by_streets(
            self,
            *,
            unit_ids: Iterable[int],
            cookies: dict,
            period: Period,
    ) -> tuple[models.StopSaleByStreet, ...]:
        resource = 'streets'
        response_data = self.__get_stop_sales_v1(
            resource=resource,
            unit_ids=unit_ids,
            cookies=cookies,
            period=period,
        )
        return parse_obj_as(tuple[models.StopSaleByStreet, ...], response_data)

    def __get_stop_sales_v2(
            self,
            *,
            resource: str,
            country_code: str,
            unit_uuids: Iterable[UUID],
            token: str,
            period: Period,
    ) -> list[dict]:
        request_query_params = {
            'unit_uuids': tuple(unit_uuids),
            'start': period.start.strftime('%Y-%m-%dT%H:%M:%S'),
            'end': period.end.strftime('%Y-%m-%dT%H:%M:%S'),
        }
        headers = {'Authorization': f'Bearer {token}'}
        url = f'/v2/{country_code}/stop-sales/{resource}'
        response = self._client.get(url, params=request_query_params, headers=headers)
        return response.json()

    def get_stop_sales_by_sales_channels(
            self,
            *,
            country_code: str,
            unit_uuids: Iterable[UUID],
            token: str,
            period: Period,
    ) -> tuple[models.StopSaleBySalesChannel, ...]:
        resource = 'channels'
        response_data = self.__get_stop_sales_v2(
            resource=resource,
            country_code=country_code,
            unit_uuids=unit_uuids,
            token=token,
            period=period,
        )
        return parse_obj_as(tuple[models.StopSaleBySalesChannel, ...], response_data)

    def get_stop_sales_by_ingredients(
            self,
            *,
            country_code: str,
            unit_uuids: Iterable[UUID],
            token: str,
            period: Period,
    ) -> tuple[models.StopSaleByIngredient, ...]:
        resource = 'ingredients'
        response_data = self.__get_stop_sales_v2(
            resource=resource,
            country_code=country_code,
            unit_uuids=unit_uuids,
            token=token,
            period=period,
        )
        return parse_obj_as(tuple[models.StopSaleByIngredient, ...], response_data)

    def get_stocks_balance(
            self,
            *,
            unit_ids: Iterable[int],
            cookies: dict,
            days_left_threshold: int,
    ) -> models.StocksBalanceReport:
        request_data = {
            'cookies': cookies,
            'days_left_threshold': days_left_threshold,
            'unit_ids': tuple(unit_ids),
        }
        response = self._client.post('/stocks/', json=request_data)
        return models.StocksBalanceReport.parse_obj(response.json())

    def get_cheated_orders(
            self,
            *,
            unit_ids_and_names: Iterable[dict],
            cookies: dict,
            repeated_phone_number_count_threshold: int,
    ) -> tuple[models.CommonPhoneNumberOrders, ...]:
        request_data = {
            'cookies': cookies,
            'units': tuple(unit_ids_and_names),
            'repeated_phone_number_count_threshold': repeated_phone_number_count_threshold,
        }
        response = self._client.post('/v1/cheated-orders', json=request_data)
        return parse_obj_as(tuple[models.CommonPhoneNumberOrders, ...], response.json())

    def get_canceled_orders(
            self,
            *,
            cookies: dict,
            date: datetime.date,
    ) -> tuple[models.CanceledOrder, ...]:
        request_data = {
            'cookies': cookies,
            'date': date.strftime('%Y-%m-%d'),
        }
        response = self._client.post('/v1/canceled-orders', json=request_data)
        return parse_obj_as(tuple[models.CanceledOrder, ...], response.json())
