from typing import Iterable

import models
from message_queue_events.base import MessageQueueEvent


class UsedPromoCodeEvent(MessageQueueEvent):

    def __init__(self, unit_id: int, unit_name: str, used_promo_codes: Iterable[models.UnitUsedPromoCode]):
        self.__used_promo_codes = used_promo_codes
        self.__unit_name = unit_name
        self.__unit_id = unit_id

    def get_data(self):
        return {
            'unit_id': self.__unit_id,
            'type': 'PROMO_CODES_USAGE',
            'payload': {
                'unit_name': self.__unit_name,
                'promo_codes': [
                    {
                        'promo_code': promo_code.promo_code,
                        'order_no': promo_code.order_no,
                    } for promo_code in self.__used_promo_codes
                ],
            }
        }
