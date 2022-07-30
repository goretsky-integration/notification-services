import uuid
from datetime import datetime

from pydantic import BaseModel, Field, validator

__all__ = (
    'Unit',
    'StopSale',
    'StopSaleBySalesChannels',
    'StopSaleByIngredients',
    'StopSaleByProduct',
    'OrderByUUID',
    'CheatedOrders',
    'CheatedOrder',
    'StockBalance',
    'StockBalanceStatistics',
)


class Unit(BaseModel):
    id: int
    name: str
    uuid: uuid.UUID
    account_name: str
    region: str


class StopSale(BaseModel):
    unit_uuid: uuid.UUID = Field(alias='unit_id')
    unit_name: str
    reason: str
    started_at: datetime
    ended_at: datetime | None
    staff_name_who_stopped: str
    staff_name_who_resumed: str | None


class StopSaleByIngredients(StopSale):
    ingredient_name: str


class StopSaleByProduct(StopSale):
    product_name: str


class StopSaleBySalesChannels(StopSale):
    sales_channel_name: str


class OrderByUUID(BaseModel):
    unit_name: str
    created_at: datetime
    receipt_printed_at: datetime | None
    number: str
    type: str
    price: int
    uuid: uuid.UUID


class CheatedOrder(BaseModel):
    created_at: datetime
    number: str


class CheatedOrders(BaseModel):
    unit_name: str
    phone_number: str
    orders: list[CheatedOrder]

    @property
    def orders_count(self) -> int:
        return len(self.orders)

    @validator('phone_number')
    def humanize_phone_number(cls, value: str) -> str:
        value = value.removesuffix('.0')
        if len(value) != 11:
            return value
        return f'+{value[0]} {value[1:4]} {value[4:7]}-{value[7:9]}-{value[9:11]}'


class StockBalance(BaseModel):
    unit_id: int
    ingredient_name: str
    days_left: int
    stocks_count: int | float
    stocks_unit: str


class StockBalanceStatistics(BaseModel):
    error_unit_ids: list[int]
    units: list[StockBalance]
