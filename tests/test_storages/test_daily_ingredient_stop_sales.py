import os

import pytest

from services.storages import DailyIngredientStopSalesStorage


@pytest.mark.parametrize(
    'unit_name, ingredient_name',
    [
        ('Москва 4-1', 'Тесто-35'),
        ('Москва 4-1', 'Тесто-25'),
        ('Москва 4-1', 'Тесто-45'),
        ('Москва 4-2', 'Тесто-35'),
        ('Москва 4-3', 'Тесто-25'),
    ]
)
def test_insert_and_exists_stop_sales(unit_name, ingredient_name):
    storage_file_path = './daily_ingredient_stop_sales.db'
    with DailyIngredientStopSalesStorage(storage_file_path) as storage:
        try:
            assert not storage.is_exist(unit_name, ingredient_name)
            storage.insert(unit_name, ingredient_name)
            assert storage.is_exist(unit_name, ingredient_name)
        finally:
            storage.clear_all()
    os.remove(storage_file_path)
