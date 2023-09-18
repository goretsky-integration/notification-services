import datetime
from dataclasses import dataclass
from decimal import Decimal
from typing import Generic, TypeVar
from uuid import UUID

from pydantic import BaseModel

__all__ = (
    'CommonPhoneNumberOrders',
    'CheatedPhoneNumberOrder',
    'CanceledOrder',
    'UnitStocksBalance',
    'StocksBalanceReport',
    'StopSalesBatchResponse',
    'UnitUsedPromoCode',
)


class CheatedPhoneNumberOrder(BaseModel):
    number: str
    created_at: datetime.datetime


class CommonPhoneNumberOrders(BaseModel):
    unit_name: str
    orders: tuple[CheatedPhoneNumberOrder, ...]
    phone_number: str


class CanceledOrder(BaseModel):
    unit_name: str
    created_at: datetime.datetime
    canceled_at: datetime.datetime
    receipt_printed_at: datetime.datetime | None
    number: str
    type: str
    price: int
    uuid: UUID
    courier_name: str | None
    rejected_by_user_name: str | None


class UnitStocksBalance(BaseModel):
    unit_id: int
    ingredient_name: str
    days_left: int
    stocks_count: float
    stocks_unit: str


class StocksBalanceReport(BaseModel):
    units: list[UnitStocksBalance]
    error_unit_ids: set[int]


StopSalesT = TypeVar('StopSalesT')


@dataclass(frozen=True, slots=True)
class StopSalesBatchResponse(Generic[StopSalesT]):
    result: list[StopSalesT]
    error_unit_ids: list[int]


class UnitUsedPromoCode(BaseModel):
    unit_id: int
    promo_code: str
    event: str
    typical_description: str
    order_type: str
    order_status: str
    order_no: str
    ordered_at: datetime.datetime
    order_price: Decimal
