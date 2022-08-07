from typing import Iterable
from uuid import UUID

from pydantic import parse_obj_as

from core import models
from core.repositories.base import BaseHTTPAPIRepository
from core.utils import exceptions

__all__ = (
    'DodoAPIRepository',
)


class DodoAPIRepository(BaseHTTPAPIRepository):

    def get_stop_sales_by_ingredients(
            self,
            token: str,
            unit_uuids: Iterable[UUID],
    ) -> list[models.StopSaleByIngredients]:
        params = {'token': token, 'unit_uuids': unit_uuids}
        response = self._client.get('/v2/stop-sales/ingredients', params=params)
        if response.is_server_error:
            raise exceptions.DodoAPIError
        return parse_obj_as(list[models.StopSaleByIngredients], response.json())

    def get_stocks_balance(
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
        response = self._client.post('/stocks/', json=body)
        if response.is_server_error:
            raise exceptions.DodoAPIError
        return models.StockBalanceStatistics.parse_obj(response.json())

    def get_stop_sales_by_channels(
            self,
            token: str,
            unit_uuids: Iterable[UUID],
    ) -> list[models.StopSaleBySalesChannels]:
        params = {'token': token, 'unit_uuids': unit_uuids}
        response = self._client.get('/v2/stop-sales/channels', params=params)
        if response.is_server_error:
            raise exceptions.DodoAPIError
        return parse_obj_as(list[models.StopSaleBySalesChannels], response.json())
