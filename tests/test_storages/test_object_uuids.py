import os
from uuid import uuid4

import pytest

from services.storages import ObjectUUIDStorage


@pytest.mark.parametrize(
    'stop_sale_id',
    [
        uuid4(),
        uuid4(),
        uuid4(),
        uuid4(),
        uuid4(),
    ]
)
def test_insert_and_exists_uuids(stop_sale_id):
    storage_file_path = './daily_ingredient_stop_sales.db'
    with ObjectUUIDStorage(storage_file_path) as storage:
        try:
            assert not storage.is_exist(stop_sale_id)
            storage.insert(stop_sale_id)
            assert storage.is_exist(stop_sale_id)
        finally:
            storage.clear_all()
    os.remove(storage_file_path)
