from typing import Iterable

from dodo_is_api.models import LateDeliveryVoucher

from message_queue_events.base import MessageQueueEvent

__all__ = ('LateDeliveryVouchersEvent',)


class LateDeliveryVouchersEvent(MessageQueueEvent):

    def __init__(self, unit_id: int, unit_name: str, late_delivery_vouchers: Iterable[LateDeliveryVoucher]):
        self.__unit_id = unit_id
        self.__unit_name = unit_name
        self.__late_delivery_vouchers = late_delivery_vouchers

    def get_data(self):
        return {
            'unit_id': self.__unit_id,
            'type': 'LATE_DELIVERY_VOUCHERS',
            'payload': {
                'unit_name': self.__unit_name,
                'order_numbers': [
                    late_delivery_voucher.order_number for
                    late_delivery_voucher in self.__late_delivery_vouchers
                ]
            }
        }
