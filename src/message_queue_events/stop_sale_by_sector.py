from dodo_is_api.models import StopSaleBySector

from message_queue_events.base import MessageQueueEvent

__all__ = ('StopSaleBySectorEvent',)


class StopSaleBySectorEvent(MessageQueueEvent):
    __slots__ = ('__unit_id', '__stop_sale')

    def __init__(self, unit_id: int, stop_sale: StopSaleBySector):
        self.__unit_id = unit_id
        self.__stop_sale = stop_sale

    def get_data(self):
        return {
            'unit_id': self.__unit_id,
            'type': 'SECTOR_STOP_SALES',
            'payload': {
                'unit_name': self.__stop_sale.unit_name,
                'started_at': self.__stop_sale.started_at,
                'sector_name': self.__stop_sale.sector_name,
            }
        }
