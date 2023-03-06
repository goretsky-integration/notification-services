from pydantic import parse_obj_as

import models
from services.external_dodo_api.base import APIService

__all__ = ('DatabaseAPI',)


class DatabaseAPI(APIService):

    def get_units(self) -> tuple[models.Unit, ...]:
        response = self._client.get('/units/')
        response_data = response.json()
        return parse_obj_as(tuple[models.Unit, ...], response_data)
