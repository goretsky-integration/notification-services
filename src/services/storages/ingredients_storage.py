from services.storages.base import Storage

__all__ = ('DailyIngredientStopSalesStorage',)


class DailyIngredientStopSalesStorage(Storage):

    def init_tables(self) -> None:
        query = '''
        CREATE TABLE IF NOT EXISTS stop_sales (
            unit_name TEXT,
            ingredient_name TEXT,
            UNIQUE (unit_name, ingredient_name) ON CONFLICT IGNORE
        );
        '''
        cursor = self._connection.cursor()
        cursor.execute(query)
        self._connection.commit()

    def is_exist(self, unit_name: str, ingredient_name: str) -> bool:
        query = 'SELECT unit_name, ingredient_name FROM stop_sales WHERE unit_name=? AND ingredient_name=?;'
        cursor = self._connection.cursor()
        cursor.execute(query, (unit_name, ingredient_name))
        return bool(cursor.fetchone())

    def insert(self, unit_name: str, ingredient_name: str) -> None:
        query = 'INSERT INTO stop_sales (unit_name, ingredient_name) VALUES (?,?);'
        cursor = self._connection.cursor()
        cursor.execute(query, (unit_name, ingredient_name))
        self._connection.commit()

    def clear_all(self) -> None:
        query = 'DELETE FROM stop_sales;'
        cursor = self._connection.cursor()
        cursor.execute(query)
        self._connection.commit()
