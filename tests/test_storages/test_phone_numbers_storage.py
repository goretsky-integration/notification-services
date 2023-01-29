import os
from dataclasses import dataclass
from uuid import UUID

import pytest
from faker import Faker

from services.storages import PhoneNumbersStorage

STORAGE_PATH = './phone-numbers-storage.db'

faker = Faker()


@dataclass(frozen=True, slots=True)
class FakeObjectWithUUID:
    uuid: UUID


@pytest.fixture
def storage():
    with PhoneNumbersStorage(STORAGE_PATH) as storage:
        yield storage


@pytest.mark.parametrize(
    'phone_number',
    [
        faker.phone_number()
        for _ in range(10)
    ]
)
def test_phone_number_not_in_storage(storage, phone_number):
    with storage:
        assert storage.get_phone_number_count(phone_number) == 0
    os.remove(STORAGE_PATH)


@pytest.mark.parametrize(
    'phone_number,count',
    [
        (faker.phone_number(), 3),
        (faker.phone_number(), 1),
        (faker.phone_number(), 5),
        (faker.phone_number(), 3),
    ]
)
def test_phone_number_not_in_storage(storage, phone_number, count):
    with storage:
        assert storage.get_phone_number_count(phone_number) == 0
        storage.set_phone_numbers_count(phone_number, count)
        assert storage.get_phone_number_count(phone_number) == count
    os.remove(STORAGE_PATH)
