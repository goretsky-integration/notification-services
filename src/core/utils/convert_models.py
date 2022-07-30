import collections
import uuid
from dataclasses import dataclass
from typing import Iterable

from core import models


@dataclass(slots=True, frozen=True)
class UnitsConverter:
    units: Iterable[models.Unit]

    @classmethod
    def new(cls, units: Iterable[models.Unit]) -> 'UnitsConverter':
        return cls(units)

    @property
    def uuids(self) -> list[uuid.UUID]:
        return [unit.uuid for unit in self.units]

    @property
    def ids(self) -> list[int]:
        return [unit.id for unit in self.units]

    @property
    def ids_to_names(self) -> dict[int, str]:
        return {unit.id: unit.name for unit in self.units}

    @property
    def names_to_ids(self) -> dict[str, int]:
        return {unit.name: unit.id for unit in self.units}

    @property
    def uuids_to_ids(self) -> dict[uuid.UUID, int]:
        return {unit.uuid: unit.id for unit in self.units}

    @property
    def ids_and_names(self) -> list[models.UnitIdAndName]:
        return [{'id': unit.id, 'name': unit.name} for unit in self.units]

    @property
    def account_names_to_units(self) -> dict[str, 'UnitsConverter']:
        account_name_to_units: dict[str, list[models.Unit]] = collections.defaultdict(list)
        for unit in self.units:
            grouped_units: list[models.Unit] = account_name_to_units[unit.account_name]
            grouped_units.append(unit)
        return {account_name: self.new(units) for account_name, units in account_name_to_units.items()}

    @property
    def account_names_to_unit_ids(self) -> dict[str, list[int]]:
        return {account_name: self.new(units).ids
                for account_name, units in self.account_names_to_units.items()}

    @property
    def account_names_to_unit_uuids(self) -> dict[str, list[uuid.UUID]]:
        return {account_name: self.new(units).uuids
                for account_name, units in self.account_names_to_units.items()}

    def __iter__(self):
        return iter(self.units)
