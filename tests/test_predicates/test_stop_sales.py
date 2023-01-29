import pytest
from faker import Faker

import models
from filters import predicates

faker = Faker()


@pytest.mark.parametrize(
    'stop_sale',
    [
        models.StopSaleV1(
            unit_name=faker.name(),
            started_at=faker.date_time(),
            ended_at=None,
            staff_name_who_stopped=faker.name(),
            staff_name_who_resumed=None,
            sector=faker.address(),
        ) for _ in range(10)
    ]
)
def test_stopped_v1_stop_sales(stop_sale):
    assert predicates.is_stop_sale_v1_stopped(stop_sale) == True


@pytest.mark.parametrize(
    'stop_sale',
    [
        models.StopSaleV1(
            unit_name=faker.name(),
            started_at=faker.date_time(),
            ended_at=faker.date_time(),
            staff_name_who_stopped=faker.name(),
            staff_name_who_resumed=faker.name(),
            sector=faker.address(),
        ) for _ in range(10)
    ]
)
def test_resumed_v1_stop_sales(stop_sale):
    assert predicates.is_stop_sale_v1_stopped(stop_sale) == False


@pytest.mark.parametrize(
    'stop_sale',
    [
        models.StopSaleV2(
            id=faker.uuid4(cast_to=None),
            unit_uuid=faker.uuid4(cast_to=None),
            unit_name=faker.name(),
            reason=faker.text(),
            started_at=faker.date_time(),
            ended_at=None,
            stopped_by_user_id=faker.uuid4(cast_to=None),
            resumed_by_user_id=None,
        ) for _ in range(10)
    ]
)
def test_stopped_v2_stop_sales(stop_sale):
    assert predicates.is_stop_sale_v2_stopped(stop_sale) == True


@pytest.mark.parametrize(
    'stop_sale',
    [
        models.StopSaleV2(
            id=faker.uuid4(cast_to=None),
            unit_uuid=faker.uuid4(cast_to=None),
            unit_name=faker.name(),
            reason=faker.text(),
            started_at=faker.date_time(),
            ended_at=faker.date_time(),
            stopped_by_user_id=faker.uuid4(cast_to=None),
            resumed_by_user_id=faker.uuid4(cast_to=None),
        ) for _ in range(10)
    ]
)
def test_resumed_v2_stop_sales(stop_sale):
    assert predicates.is_stop_sale_v2_stopped(stop_sale) == False
