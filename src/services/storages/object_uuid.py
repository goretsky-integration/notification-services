from uuid import UUID

from services.storages.base import Storage

__all__ = ('ObjectUUIDStorage',)


class ObjectUUIDStorage(Storage):

    def init_tables(self) -> None:
        query = 'CREATE TABLE IF NOT EXISTS uuids (id TEXT UNIQUE NOT NULL);'
        cursor = self._connection.cursor()
        cursor.execute(query)
        self._connection.commit()

    def is_exist(self, object_uuid: UUID) -> bool:
        query = 'SELECT id FROM uuids WHERE id=?;'
        cursor = self._connection.cursor()
        cursor.execute(query, (object_uuid.hex,))
        return bool(cursor.fetchone())

    def insert(self, object_uuid: UUID) -> None:
        query = 'INSERT INTO uuids (id) VALUES (?) ON CONFLICT (id) DO NOTHING;'
        cursor = self._connection.cursor()
        cursor.execute(query, (object_uuid.hex,))
        self._connection.commit()

    def clear_all(self) -> None:
        query = 'DELETE FROM uuids;'
        cursor = self._connection.cursor()
        cursor.execute(query)
        self._connection.commit()
