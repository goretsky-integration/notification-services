import collections
import functools
from dataclasses import dataclass
from typing import Iterable, Self
from uuid import UUID

import models

__all__ = ('UnitsConverter',)


@dataclass
class UnitsConverter:
    units: Iterable[models.Unit]

    @functools.cached_property
    def ids(self) -> set[int]:
        return {unit.id for unit in self.units}

    @functools.cached_property
    def names(self) -> set[str]:
        return {unit.name for unit in self.units}

    @functools.cached_property
    def ids_and_names(self) -> list[dict]:
        return [{'id': unit.id, 'name': unit.name} for unit in self.units]

    @functools.cached_property
    def uuids(self) -> set[UUID]:
        return {unit.uuid for unit in self.units}

    @functools.cached_property
    def account_names(self) -> set[str]:
        return {unit.account_name for unit in self.units}

    @functools.cached_property
    def unit_id_to_name(self) -> dict[int, str]:
        return {unit.id: unit.name for unit in self.units}

    @functools.cached_property
    def unit_uuid_to_name(self) -> dict[UUID, str]:
        return {unit.uuid: unit.name for unit in self.units}

    @functools.cached_property
    def unit_name_to_id(self) -> dict[str, int]:
        return {unit.name: unit.id for unit in self.units}

    @functools.cached_property
    def unit_uuid_to_id(self) -> dict[UUID, int]:
        return {unit.uuid: unit.id for unit in self.units}

    @functools.cached_property
    def grouped_by_account_name(self) -> dict[str, Self]:
        account_name_to_units = collections.defaultdict(list)
        for unit in self.units:
            account_name_to_units[unit.account_name].append(unit)
        return {account_name: UnitsConverter(units) for account_name, units in account_name_to_units.items()}
