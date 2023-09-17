import datetime
from dataclasses import dataclass
from decimal import Decimal
from enum import Enum
from typing import Generic, TypeVar
from uuid import UUID

from pydantic import BaseModel, Field

__all__ = (
    'StopSaleByIngredient',
    'StopSaleBySalesChannel',
    'CommonPhoneNumberOrders',
    'CheatedPhoneNumberOrder',
    'CanceledOrder',
    'UnitStocksBalance',
    'StocksBalanceReport',
    'StopSaleV2',
    'StopSalesBatchResponse',
    'SalesChannelName',
    'ChannelStopType',
    'UnitUsedPromoCode',
)


class StopSaleV2(BaseModel):
    uuid: UUID = Field(alias='id')
    unit_uuid: UUID
    unit_name: str
    reason: str
    started_at: datetime.datetime
    ended_at: datetime.datetime | None
    stopped_by_user_id: UUID
    resumed_by_user_id: UUID | None


class SalesChannelName(Enum):
    DELIVERY = 'Delivery'
    TAKEAWAY = 'Takeaway'
    DINE_IN = 'Dine-in'


class ChannelStopType(Enum):
    COMPLETE = 'Complete'
    REDIRECTION = 'Redirection'


class StopSaleBySalesChannel(StopSaleV2):
    sales_channel_name: SalesChannelName
    channel_stop_type: ChannelStopType


class StopSaleByIngredient(StopSaleV2):
    ingredient_name: str


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
