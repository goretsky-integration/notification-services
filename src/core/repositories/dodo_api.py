from typing import Iterable
from uuid import UUID

from pydantic import parse_obj_as

from core import models
from core.repositories.base import BaseHTTPAPIRepository

__all__ = (
    'DodoAPIRepository',
)

from core.utils import exceptions


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
