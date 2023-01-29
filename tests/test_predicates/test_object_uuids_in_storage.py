import os
from dataclasses import dataclass
from uuid import UUID

import pytest
from faker import Faker

from filters import predicates
from services.storages import ObjectUUIDStorage

faker = Faker()

STORAGE_PATH = './storage.db'


@dataclass(frozen=True, slots=True)
class FakeObjectWithUUID:
    uuid: UUID


@pytest.fixture
def storage():
    with ObjectUUIDStorage(STORAGE_PATH) as storage:
        yield storage


@pytest.mark.parametrize(
    'element',
    [
        FakeObjectWithUUID(uuid=faker.uuid4(cast_to=None)),
        FakeObjectWithUUID(uuid=faker.uuid4(cast_to=None)),
        FakeObjectWithUUID(uuid=faker.uuid4(cast_to=None)),
        FakeObjectWithUUID(uuid=faker.uuid4(cast_to=None)),
        FakeObjectWithUUID(uuid=faker.uuid4(cast_to=None)),
        FakeObjectWithUUID(uuid=faker.uuid4(cast_to=None)),
        FakeObjectWithUUID(uuid=faker.uuid4(cast_to=None)),
        FakeObjectWithUUID(uuid=faker.uuid4(cast_to=None)),
    ]
)
def test_object_uuids(element, storage):
    with storage:
        assert predicates.is_object_uuid_not_in_storage(element, storage) == True
        storage.insert(element.uuid)
        assert predicates.is_object_uuid_not_in_storage(element, storage) == False
    os.remove(STORAGE_PATH)
