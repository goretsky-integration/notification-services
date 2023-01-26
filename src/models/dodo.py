import datetime
from uuid import UUID

from pydantic import BaseModel

__all__ = (
    'StopSaleBySector',
    'StopSaleByStreet',
    'StopSaleByIngredient',
    'StopSaleBySalesChannel',
    'CommonPhoneNumberOrders',
    'CheatedPhoneNumberOrder',
)


class StopSaleV1(BaseModel):
    unit_name: str
    started_at: datetime.datetime
    ended_at: datetime.datetime | None
    staff_name_who_stopped: str
    staff_name_who_resumed: str | None
    sector: str


class StopSaleBySector(StopSaleV1):
    pass


class StopSaleByStreet(StopSaleV1):
    street: str


class StopSaleV2(BaseModel):
    id: UUID
    unit_uuid: UUID
    unit_name: str
    reason: str
    started_at: datetime.datetime
    ended_at: datetime.datetime | None
    stopped_by_user_id: UUID
    resumed_by_user_id: UUID | None


class StopSaleBySalesChannel(StopSaleV2):
    sales_channel_name: str
    channel_stop_type: str


class StopSaleByIngredient(StopSaleV2):
    ingredient_name: str


class CheatedPhoneNumberOrder(BaseModel):
    number: str
    created_at: datetime.datetime


class CommonPhoneNumberOrders(BaseModel):
    unit_name: str
    orders: tuple[CheatedPhoneNumberOrder]
    phone_number: str
