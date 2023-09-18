from dodo_is_api.models import StopSaleBySalesChannel

from message_queue_events.base import MessageQueueEvent

__all__ = ('StopSaleByChannelEvent',)


class StopSaleByChannelEvent(MessageQueueEvent):

    def __init__(self, unit_id: int, stop_sale: StopSaleBySalesChannel):
        self.__unit_id = unit_id
        self.__stop_sale = stop_sale

    def get_data(self):
        return {
            'unit_id': self.__unit_id,
            'type': 'PIZZERIA_STOP_SALES',
            'payload': {
                'unit_name': self.__stop_sale.unit_name,
                'started_at': self.__stop_sale.started_at,
                'sales_channel_name': self.__stop_sale.sales_channel_name,
                'reason': self.__stop_sale.reason,
            },
        }
