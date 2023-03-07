import models
from message_queue_events.base import MessageQueueEvent

__all__ = ('StopSaleByStreetEvent',)


class StopSaleByStreetEvent(MessageQueueEvent):
    __slots__ = ('__unit_id', '__stop_sale')

    def __init__(self, unit_id: int, stop_sale: models.StopSaleByStreet):
        self.__unit_id = unit_id
        self.__stop_sale = stop_sale

    def get_data(self):
        return {
            'unit_id': self.__unit_id,
            'type': 'STREET_STOP_SALES',
            'payload': {
                'unit_name': self.__stop_sale.unit_name,
                'started_at': self.__stop_sale.started_at,
                'street_name': self.__stop_sale.street,
            }
        }
