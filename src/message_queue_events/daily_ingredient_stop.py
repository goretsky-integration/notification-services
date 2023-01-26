from typing import Iterable

import models
from message_queue_events.base import MessageQueueEvent

__all__ = ('DailyIngredientStopEvent',)


class DailyIngredientStopEvent(MessageQueueEvent):

    def __init__(self, unit_id: int, unit_name: str, stop_sales: Iterable[models.StopSaleByIngredient]):
        self.__unit_id = unit_id
        self.__unit_name = unit_name
        self.__stop_sales = stop_sales

    def get_data(self) -> dict:
        ingredients = [
            {
                'started_at': stop_sale.started_at,
                'reason': stop_sale.reason,
                'name': stop_sale.ingredient_name,
            } for stop_sale in self.__stop_sales
        ]
        return {
            'unit_id': self.__unit_id,
            'type': 'STOPS_AND_RESUMES',
            'payload': {
                'unit_name': self.__unit_name,
                'ingredients': ingredients,
            },
        }
