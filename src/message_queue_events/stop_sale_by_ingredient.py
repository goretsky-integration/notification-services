from dodo_is_api.models import StopSaleByIngredient

from message_queue_events.base import MessageQueueEvent

__all__ = ('StopSaleByIngredientEvent',)


class StopSaleByIngredientEvent(MessageQueueEvent):

    def __init__(self, unit_id: int, stop_sale: StopSaleByIngredient):
        self.__unit_id = unit_id
        self.__stop_sale = stop_sale

    def get_data(self):
        return {
            'unit_id': self.__unit_id,
            'type': 'INGREDIENTS_STOP_SALES',
            'payload': {
                'unit_name': self.__stop_sale.unit_name,
                'started_at': self.__stop_sale.started_at,
                'ingredient_name': self.__stop_sale.ingredient_name,
                'reason': self.__stop_sale.reason,
            },
        }

    def __repr__(self):
        return f'<Event Partial Ingredients Stop Sale {self.__stop_sale.unit_name}, {self.__stop_sale.ingredient_name}>'
