import datetime
from uuid import UUID

import pytest
from faker import Faker

import models
from canceled_orders import filter_canceled_orders

faker = Faker()


@pytest.mark.parametrize(
    'canceled_order, is_skipped',
    [
        (
                models.CanceledOrder(
                    unit_name=faker.city(),
                    created_at=faker.date_time(),
                    canceled_at=faker.date_time(),
                    receipt_printed_at=None,
                    number=faker.random_int(),
                    type='Ресторан',
                    price=faker.random_int(),
                    uuid=faker.uuid4(),
                    courier_name=None,
                    rejected_by_user_name=None,
                ),
                True,
        ),
        (
                models.CanceledOrder(
                    unit_name=faker.city(),
                    created_at=faker.date_time(),
                    canceled_at=faker.date_time(),
                    receipt_printed_at=None,
                    number=faker.random_int(),
                    type='Ресторан',
                    price=faker.random_int(),
                    uuid=faker.uuid4(),
                    courier_name=None,
                    rejected_by_user_name=faker.name(),
                ),
                False,
        ),
        (
                models.CanceledOrder(
                    unit_name=faker.city(),
                    created_at=faker.date_time(),
                    canceled_at=faker.date_time(),
                    receipt_printed_at=faker.date_time(),
                    number=faker.random_int(),
                    type='Ресторан',
                    price=faker.random_int(),
                    uuid=faker.uuid4(),
                    courier_name=None,
                    rejected_by_user_name=faker.name(),
                ),
                False,
        ),
        (
                models.CanceledOrder(
                    unit_name=faker.city(),
                    created_at=faker.date_time(),
                    canceled_at=faker.date_time(),
                    receipt_printed_at=faker.date_time(),
                    number=faker.random_int(),
                    type='Доставка',
                    price=faker.random_int(),
                    uuid=faker.uuid4(),
                    courier_name=faker.name(),
                    rejected_by_user_name=None,
                ),
                False,
        ),
        (
                models.CanceledOrder(
                    unit_name=faker.city(),
                    created_at=faker.date_time(),
                    canceled_at=faker.date_time(),
                    receipt_printed_at=None,
                    number=faker.random_int(),
                    type='Доставка',
                    price=faker.random_int(),
                    uuid=faker.uuid4(),
                    courier_name=faker.name(),
                    rejected_by_user_name=None,
                ),
                False,
        ),
        (
                models.CanceledOrder(
                    unit_name=faker.city(),
                    created_at=faker.date_time(),
                    canceled_at=faker.date_time(),
                    receipt_printed_at=None,
                    number=faker.random_int(),
                    type='Доставка',
                    price=faker.random_int(),
                    uuid=faker.uuid4(),
                    courier_name=None,
                    rejected_by_user_name=None,
                ),
                True,
        ),
    ]
)
def test_filter_canceled_orders(canceled_order, is_skipped):
    expected = [] if is_skipped else [canceled_order]
    assert filter_canceled_orders([canceled_order]) == expected
