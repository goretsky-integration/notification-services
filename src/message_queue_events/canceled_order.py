import models
from message_queue_events.base import MessageQueueEvent

__all__ = ('CanceledOrderEvent',)


class CanceledOrderEvent(MessageQueueEvent):

    def __init__(self, unit_id: int, canceled_order: models.CanceledOrder):
        self.__unit_id = unit_id
        self.__canceled_order = canceled_order

    def get_data(self):
        return {
            'unit_id': self.__unit_id,
            'type': 'CANCELED_ORDERS',
            'payload': {
                "unit_name": self.__canceled_order.unit_name,
                "created_at": self.__canceled_order.created_at,
                "receipt_printed_at": self.__canceled_order.receipt_printed_at,
                "number": self.__canceled_order.number,
                "type": self.__canceled_order.type,
                "price": self.__canceled_order.price,
                "uuid": self.__canceled_order.uuid
            },
        }
