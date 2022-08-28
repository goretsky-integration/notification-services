from dataclasses import dataclass
from typing import Literal, TypeAlias
from uuid import UUID

EventType: TypeAlias = Literal['EXPIRE_AT_15_MINUTES', 'EXPIRE_AT_10_MINUTES',
                               'EXPIRE_AT_5_MINUTES', 'ALREADY_EXPIRED']


@dataclass(frozen=True, slots=True)
class Unit:
    id: int
    name: str
    uuid: UUID


@dataclass(frozen=True, slots=True)
class WriteOffEvent:
    id: UUID
    data: dict
    type: EventType


@dataclass(frozen=True, slots=True)
class PingEvent:
    type: Literal['ping']
    data: dict
