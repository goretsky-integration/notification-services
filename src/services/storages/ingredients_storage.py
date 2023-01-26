from uuid import UUID

from services.storages.base import Storage

__all__ = ('DailyIngredientStopSalesStorage',)


class DailyIngredientStopSalesStorage(Storage):

    def init_tables(self) -> None:
        query = 'CREATE TABLE IF NOT EXISTS stop_sales (id TEXT UNIQUE NOT NULL);'
        cursor = self._connection.cursor()
        cursor.execute(query)
        self._connection.commit()

    def is_exist(self, stop_sale_id: UUID) -> bool:
        query = 'SELECT id FROM stop_sales WHERE id=?;'
        cursor = self._connection.cursor()
        cursor.execute(query, (stop_sale_id.hex,))
        return bool(cursor.fetchone())

    def insert(self, stop_sale_id: UUID) -> None:
        query = 'INSERT INTO stop_sales (id) VALUES (?);'
        cursor = self._connection.cursor()
        cursor.execute(query, (stop_sale_id.hex,))
        self._connection.commit()

    def clear_all(self) -> None:
        query = 'DELETE FROM stop_sales;'
        cursor = self._connection.cursor()
        cursor.execute(query)
        self._connection.commit()
