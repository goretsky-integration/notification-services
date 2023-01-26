from pydantic import parse_obj_as

import models
from services.external_dodo_api.base import APIService

__all__ = ('DatabaseAPI',)


class DatabaseAPI(APIService):

    def get_units(self) -> tuple[models.Unit, ...]:
        response = self._client.get('/units/')
        response_data = response.json()
        return parse_obj_as(tuple[models.Unit, ...], response_data)

    def get_accounts(self) -> tuple[models.Account, ...]:
        response = self._client.get('/accounts/')
        response_data = response.json()
        return parse_obj_as(tuple[models.Account, ...], response_data)
