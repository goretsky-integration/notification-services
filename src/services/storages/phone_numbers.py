from services.storages.base import Storage

__all__ = ('PhoneNumbersStorage',)


class PhoneNumbersStorage(Storage):

    def init_tables(self) -> None:
        query = '''
        CREATE TABLE IF NOT EXISTS phone_numbers (
            phone_number TEXT UNIQUE NOT NULL,
            count INTEGER NOT NULL
        );
        '''
        cursor = self._connection.cursor()
        cursor.execute(query)
        self._connection.commit()

    def set_phone_numbers_count(self, phone_number: str, count: int) -> None:
        query = '''
        INSERT INTO phone_numbers (phone_number, count) VALUES (?,?)
        ON CONFLICT (phone_number) DO UPDATE 
        SET count = ? WHERE phone_number = ?;
        '''
        cursor = self._connection.cursor()
        cursor.execute(query, (phone_number, count, count, phone_number))
        self._connection.commit()

    def get_phone_number_count(self, phone_number: str) -> int:
        query = 'SELECT count FROM phone_numbers WHERE phone_number = ?;'
        cursor = self._connection.cursor()
        cursor.execute(query, (phone_number,))
        count = cursor.fetchone()
        return count[0] if count else 0

    def clear_all(self) -> None:
        cursor = self._connection.cursor()
        cursor.execute('DELETE FROM phone_numbers;')
        self._connection.commit()
