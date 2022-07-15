from typing import TypeAlias, TypedDict

__all__ = (
    'Cookies',
    'AccessToken',
    'Event',
    'UnitIdAndName',
)

Cookies: TypeAlias = dict[str, str]
AccessToken: TypeAlias = str


class Event(TypedDict):
    type: str
    unit_id: int
    payload: list | dict


class UnitIdAndName(TypedDict):
    id: int
    name: str
