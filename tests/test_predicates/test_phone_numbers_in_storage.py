import os
from dataclasses import dataclass
from uuid import UUID

import pytest
from faker import Faker

import models
from filters import predicates
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


def fake_common_phone_number_orders(orders_count: int) -> models.CommonPhoneNumberOrders:
    return models.CommonPhoneNumberOrders(
        unit_name=faker.name(),
        orders=[
            models.CheatedPhoneNumberOrder(
                number=faker.name(),
                created_at=faker.date_time(),
            ) for _ in range(orders_count)
        ],
        phone_number=faker.phone_number(),
    )


@pytest.mark.parametrize(
    'common_phone_number_orders, count_in_storage',
    [
        (fake_common_phone_number_orders(orders_count=5), 4),
        (fake_common_phone_number_orders(orders_count=3), 2),
        (fake_common_phone_number_orders(orders_count=7), 3),
        (fake_common_phone_number_orders(orders_count=8), 5),
    ]
)
def test_have_more_orders_than_in_storage(storage, common_phone_number_orders, count_in_storage):
    with storage:
        storage.set_phone_numbers_count(common_phone_number_orders.phone_number, count_in_storage)
        assert predicates.is_more_orders_than_in_storage(common_phone_number_orders, storage) == True
    os.remove(STORAGE_PATH)


@pytest.mark.parametrize(
    'common_phone_number_orders, count_in_storage',
    [
        (fake_common_phone_number_orders(orders_count=5), 5),
        (fake_common_phone_number_orders(orders_count=1), 3),
        (fake_common_phone_number_orders(orders_count=6), 10),
    ]
)
def test_have_no_orders_more_than_in_storage(storage, common_phone_number_orders, count_in_storage):
    with storage:
        storage.set_phone_numbers_count(common_phone_number_orders.phone_number, count_in_storage)
        assert predicates.is_more_orders_than_in_storage(common_phone_number_orders, storage) == False
    os.remove(STORAGE_PATH)


@pytest.mark.parametrize(
    'common_phone_number_orders, count',
    [
        (fake_common_phone_number_orders(orders_count=3), 2),
        (fake_common_phone_number_orders(orders_count=5), 4),
        (fake_common_phone_number_orders(orders_count=100), 99),
        (fake_common_phone_number_orders(orders_count=1), 0),
    ]
)
def test_phone_numbers_count_more_than(common_phone_number_orders, count):
    assert predicates.is_orders_count_more_than(common_phone_number_orders, count) == True


@pytest.mark.parametrize(
    'common_phone_number_orders, count',
    [
        (fake_common_phone_number_orders(orders_count=1), 2),
        (fake_common_phone_number_orders(orders_count=3), 4),
        (fake_common_phone_number_orders(orders_count=98), 99),
        (fake_common_phone_number_orders(orders_count=0), 1),
    ]
)
def test_phone_numbers_count_fewer_than(common_phone_number_orders, count):
    assert predicates.is_orders_count_more_than(common_phone_number_orders, count) == False
