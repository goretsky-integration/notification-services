from typing import Iterable
from uuid import UUID

from pydantic import parse_obj_as

import models
from services.external_dodo_api.base import APIService
from services.period import Period

__all__ = ('DodoAPIService',)


class DodoAPIService(APIService):
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
        response = self._client.post(url, params=request_query_params, headers=headers)
        return response.json()

    def get_stop_sales_by_sales_channels(
            self,
            *,
            country_code: str,
            unit_uuids: Iterable[UUID],
            token: str,
            period: Period,
    ) -> tuple[models.StopSaleBySalesChannel, ...]:
        resource = '/channels'
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
        resource = '/ingredients'
        response_data = self.__get_stop_sales_v2(
            resource=resource,
            country_code=country_code,
            unit_uuids=unit_uuids,
            token=token,
            period=period,
        )
        return parse_obj_as(tuple[models.StopSaleByIngredient, ...], response_data)
