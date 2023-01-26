from typing import Iterable

import models
from message_queue_events.base import MessageQueueEvent

__all__ = ('StocksBalanceEvent',)


class StocksBalanceEvent(MessageQueueEvent):

    def __init__(self, unit_id: int, unit_name: str, units_stocks_balance: Iterable[models.UnitStocksBalance]):
        self.__unit_id = unit_id
        self.__unit_name = unit_name
        self.__units_stocks_balance = units_stocks_balance

    def get_data(self):
        return {
            'type': 'STOCKS_BALANCE',
            'unit_id': self.__unit_id,
            'payload': {
                'unit_name': self.__unit_name,
                'stocks_balance': [
                    {
                        'unit_id': stock_balance.unit_id,
                        'ingredient_name': stock_balance.ingredient_name,
                        'days_left': stock_balance.days_left,
                        'stocks_count': stock_balance.stocks_count,
                        'stocks_unit': stock_balance.stocks_unit,
                    } for stock_balance in self.__units_stocks_balance
                ]
            }
        }
