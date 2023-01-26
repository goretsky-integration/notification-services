import models
from message_queue_events.base import MessageQueueEvent

__all__ = ('CheatedPhoneNumberEvent',)


class CheatedPhoneNumberEvent(MessageQueueEvent):

    def __init__(self, unit_id: int, common_phone_number_orders: models.CommonPhoneNumberOrders):
        self.__unit_id = unit_id
        self.__common_phone_number_orders = common_phone_number_orders

    def get_data(self):
        return {
            'unit_id': self.__unit_id,
            'type': 'CHEATED_PHONE_NUMBERS',
            'payload': {
                'unit_name': self.__common_phone_number_orders.unit_name,
                'phone_number': self.__common_phone_number_orders.phone_number,
                'orders': [{'number': order.number, 'created_at': order.created_at}
                           for order in self.__common_phone_number_orders.orders]
            },
        }
