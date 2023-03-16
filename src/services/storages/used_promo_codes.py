from services.storages.base import Storage

__all__ = ('UsedPromoCodesStorage',)


class UsedPromoCodesStorage(Storage):

    def init_tables(self) -> None:
        cursor = self._connection.cursor()
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS used_promo_codes (
            unit_id INTEGER NOT NULL,
            promo_code TEXT NOT NULL,
            order_no TEXT NOT NULL,
            PRIMARY KEY (unit_id, promo_code, order_no)
        );
        ''')

    def is_exists(self, *, unit_id: int, promo_code: str, order_no: str) -> bool:
        query = '''
        SELECT EXISTS (
            SELECT 1 FROM used_promo_codes 
            WHERE unit_id = ? AND promo_code = ? AND order_no = ?
        );
        '''
        cursor = self._connection.cursor()
        cursor.execute(query, (unit_id, promo_code, order_no))
        result: tuple[int] = cursor.fetchone()
        return bool(result[0])

    def insert(self, *, unit_id: int, promo_code: str, order_no: str) -> None:
        query = '''
        INSERT INTO used_promo_codes (unit_id, promo_code, order_no) 
        VALUES (?, ?, ?)
        ON CONFLICT DO NOTHING ;
        '''
        cursor = self._connection.cursor()
        cursor.execute(query, (unit_id, promo_code, order_no))
        self._connection.commit()
