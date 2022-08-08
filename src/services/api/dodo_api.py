from typing import Iterable
from uuid import UUID

from pydantic import parse_obj_as

import models
from services.api.base import BaseHTTPService
from utils import exceptions

__all__ = (
    'DodoAPIClient',
)


class DodoAPIClient(BaseHTTPService):

    async def get_stop_sales_by_ingredients(
            self,
            token: str,
            unit_uuids: Iterable[UUID],
    ) -> list[models.StopSaleByIngredients]:
        params = {'token': token, 'unit_uuids': unit_uuids}
        response = await self._client.get('/v2/stop-sales/ingredients', params=params)
        if response.is_server_error:
            raise exceptions.DodoAPIError
        return parse_obj_as(list[models.StopSaleByIngredients], response.json())

    async def get_stocks_balance(
            self,
            cookies: dict[str, str],
            unit_ids: Iterable[int],
            days_left_threshold: int,
    ) -> models.StockBalanceStatistics:
        body = {
            'cookies': cookies,
            'unit_ids': unit_ids,
            'days_left_threshold': days_left_threshold,
        }
        response = await self._client.post('/stocks/', json=body)
        if response.is_server_error:
            raise exceptions.DodoAPIError
        return models.StockBalanceStatistics.parse_obj(response.json())

    async def get_stop_sales_by_channels(
            self,
            token: str,
            unit_uuids: Iterable[UUID],
    ) -> list[models.StopSaleBySalesChannels]:
        params = {'token': token, 'unit_uuids': unit_uuids}
        response = await self._client.get('/v2/stop-sales/channels', params=params)
        if response.is_server_error:
            raise exceptions.DodoAPIError
        return parse_obj_as(list[models.StopSaleBySalesChannels], response.json())

    async def get_cheated_orders(
            self,
            cookies: dict[str, str],
            unit_ids_and_names: Iterable[models.UnitIdAndName],
            repeated_phones_count_threshold: int,
    ) -> list[models.CheatedOrders]:
        body = {
            'cookies': cookies,
            'units': unit_ids_and_names,
            'repeated_phone_number_count_threshold': repeated_phones_count_threshold,
        }
        response = await self._client.get('/v1/cheated-orders', json=body)
        if response.is_server_error:
            raise exceptions.DodoAPIError
        return parse_obj_as(list[models.CheatedOrders], response.json())
