import pytest
from faker import Faker

import models
from filters import predicates

faker = Faker()


@pytest.mark.parametrize(
    'order',
    [
        models.CanceledOrder(
            unit_name=faker.name(),
            created_at=faker.date_time(),
            receipt_printed_at=faker.date_time(),
            number=faker.name(),
            type=faker.name(),
            canceled_at=faker.date_time(),
            price=100,
            uuid=faker.uuid4(cast_to=None),
        ) for _ in range(10)
    ]
)
def test_orders_have_printed_receipt(order):
    assert predicates.has_printed_receipt(order) == True


@pytest.mark.parametrize(
    'order',
    [
        models.CanceledOrder(
            unit_name=faker.name(),
            created_at=faker.date_time(),
            receipt_printed_at=None,
            number=faker.name(),
            type=faker.name(),
            canceled_at=faker.date_time(),
            price=100,
            uuid=faker.uuid4(cast_to=None),
        ) for _ in range(10)
    ]
)
def test_orders_without_printed_receipt(order):
    assert predicates.has_printed_receipt(order) == False
