from collections.abc import Iterable

import models
from message_queue_events.base import MessageQueueEvent

__all__ = ('UnitCanceledOrdersEvent',)


class UnitCanceledOrdersEvent(MessageQueueEvent):

    def __init__(
            self,
            *,
            unit_id: int,
            unit_name: str,
            canceled_orders: Iterable[models.CanceledOrder],
    ):
        self.__unit_id = unit_id
        self.__unit_name = unit_name
        self.__canceled_orders = canceled_orders

    def get_data(self):
        return {
            'unit_id': self.__unit_id,
            'type': 'CANCELED_ORDERS',
            'payload': {
                "unit_name": self.__unit_name,
                'canceled_orders': [
                    {
                        'id': canceled_order.uuid,
                        'sold_at': canceled_order.created_at,
                        'canceled_at': canceled_order.canceled_at,
                        'number': canceled_order.number,
                        'sales_channel_name': canceled_order.type,
                        'price': canceled_order.price,
                    } for canceled_order in self.__canceled_orders
                ]
            },
        }
