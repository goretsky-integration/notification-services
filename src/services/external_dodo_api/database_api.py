from pydantic import parse_obj_as

import models
from services.external_dodo_api.base import APIService

__all__ = ('DatabaseAPI',)


class DatabaseAPI(APIService):

    def get_units(self) -> tuple[models.Unit, ...]:
        request_query_params = {
            'limit': 100,
            'offset': 0,
        }
        all_units: list[dict] = []
        while True:
            response = self._client.get('/units/', params=request_query_params)
            response_data = response.json()

            if response_data['units']:
                all_units += response_data['units']

            if response_data['is_end_of_list_reached']:
                break

            request_query_params['offset'] += request_query_params['limit']

        return parse_obj_as(tuple[models.Unit, ...], all_units)
