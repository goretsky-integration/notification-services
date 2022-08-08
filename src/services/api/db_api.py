from pydantic import parse_obj_as

import models
from services.api.base import BaseHTTPService
from utils import exceptions

__all__ = (
    'DatabaseClient',
)


class DatabaseClient(BaseHTTPService):

    async def get_units(self, region: str | None = None) -> list[models.Unit]:
        params = {'region': region} if region is not None else {}
        response = await self._client.get('/units/', params=params, timeout=30)
        if response.is_error:
            raise exceptions.DatabaseAPIError
        return parse_obj_as(list[models.Unit], response.json())
