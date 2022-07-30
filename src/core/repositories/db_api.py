from pydantic import parse_obj_as

from core import models
from core.repositories.base import BaseHTTPAPIRepository
from core.utils import exceptions

__all__ = (
    'DatabaseRepository',
)


class DatabaseRepository(BaseHTTPAPIRepository):

    def get_units(self, region: str | None = None) -> list[models.Unit]:
        params = {'region': region} if region is not None else {}
        response = self._client.get('/units/', params=params, timeout=30)
        if response.is_error:
            raise exceptions.DatabaseAPIError
        return parse_obj_as(list[models.Unit], response.json())
