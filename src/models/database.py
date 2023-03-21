from uuid import UUID

from pydantic import BaseModel

__all__ = ('Unit', 'Account')


class Unit(BaseModel):
    id: int
    name: str
    uuid: UUID
    region: str
    office_manager_account_name: str
    dodo_is_api_account_name: str


class Account(BaseModel):
    name: str
    login: str
    password: str
