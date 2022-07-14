import uuid
from datetime import datetime

from pydantic import BaseModel, Field

__all__ = (
    'Unit',
    'StopSaleBySalesChannels',
    'StopSaleByIngredients',
    'StopSaleByProduct',
    'OrderByUUID',
)


class Unit(BaseModel):
    id: int = Field(..., alias='_id')
    name: str
    uuid: uuid.UUID
    account_name: str
    region: str


class StopSale(BaseModel):
    unit_id: uuid.UUID
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
