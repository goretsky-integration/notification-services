from uuid import UUID

from services.storages.base import Storage

__all__ = ('CanceledOrdersStorage',)


class CanceledOrdersStorage(Storage):

    def init_tables(self) -> None:
        query = 'CREATE TABLE IF NOT EXISTS canceled_orders (id TEXT UNIQUE NOT NULL);'
        cursor = self._connection.cursor()
        cursor.execute(query)
        self._connection.commit()

    def is_exist(self, stop_sale_id: UUID) -> bool:
        query = 'SELECT id FROM canceled_orders WHERE id=?;'
        cursor = self._connection.cursor()
        cursor.execute(query, (stop_sale_id.hex,))
        return bool(cursor.fetchone())

    def insert(self, stop_sale_id: UUID) -> None:
        query = 'INSERT INTO canceled_orders (id) VALUES (?);'
        cursor = self._connection.cursor()
        cursor.execute(query, (stop_sale_id.hex,))
        self._connection.commit()

    def clear_all(self) -> None:
        query = 'DELETE FROM canceled_orders;'
        cursor = self._connection.cursor()
        cursor.execute(query)
        self._connection.commit()
