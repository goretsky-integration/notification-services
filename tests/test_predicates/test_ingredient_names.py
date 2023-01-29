import pytest
from faker import Faker

import models
from filters import predicates

faker = Faker()


def fake_stop_sale_by_ingredient(ingredient_name: str) -> models.StopSaleByIngredient:
    return models.StopSaleByIngredient(
        id=faker.uuid4(cast_to=None),
        unit_uuid=faker.uuid4(cast_to=None),
        unit_name=faker.name(),
        reason=faker.text(),
        started_at=faker.date_time(),
        ended_at=faker.date_time(),
        stopped_by_user_id=faker.uuid4(cast_to=None),
        resumed_by_user_id=faker.uuid4(cast_to=None),
        ingredient_name=ingredient_name,
    )


@pytest.mark.parametrize(
    'stop_sale, allowed_names',
    [
        (fake_stop_sale_by_ingredient('Тесто 35'), {'банан', 'тесто'},),
        (fake_stop_sale_by_ingredient('сыр пармезан'), {'пармезан', 'брынза'})
    ]
)
def test_ingredient_name_allowed(stop_sale, allowed_names):
    assert predicates.is_ingredient_name_allowed(stop_sale, allowed_names) == True


@pytest.mark.parametrize(
    'stop_sale, allowed_names',
    [
        (fake_stop_sale_by_ingredient('тесто 35'), {'банан', '45'}),
        (fake_stop_sale_by_ingredient('маффин шоколадный'), {'молочный', 'фруктовый'})
    ]
)
def test_ingredient_name_not_allowed(stop_sale, allowed_names):
    assert predicates.is_ingredient_name_allowed(stop_sale, allowed_names) == False


@pytest.mark.parametrize(
    'stop_sale,blocked_names',
    [
        (fake_stop_sale_by_ingredient('тесто 35'), {'35', 'тесто'}),
        (fake_stop_sale_by_ingredient('помидоры черри'), {'помидоры', 'тесто'}),
        (fake_stop_sale_by_ingredient('кола'), {'кола', 'фанта'}),
        (fake_stop_sale_by_ingredient('слоеное тесто'), {'слоеное', 'фанта'}),
    ]
)
def test_ingredient_name_blocked(stop_sale, blocked_names):
    assert predicates.is_ingredient_name_not_blocked(stop_sale, blocked_names) == False


@pytest.mark.parametrize(
    'stop_sale,blocked_names',
    [
        (fake_stop_sale_by_ingredient('тесто 35'), {'45', '25'}),
        (fake_stop_sale_by_ingredient('помидоры черри'), {'огурцы', 'лук'}),
        (fake_stop_sale_by_ingredient('кола'), {'пепси', 'фанта'}),
        (fake_stop_sale_by_ingredient('моцарелла'), {'пармезан', 'сыр'}),
    ]
)
def test_ingredient_name_not_blocked(stop_sale, blocked_names):
    assert predicates.is_ingredient_name_not_blocked(stop_sale, blocked_names) == True
