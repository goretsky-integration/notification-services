import pathlib
import sqlite3

import config

DATABASE_PATH = pathlib.Path.joinpath(config.ROOT_PATH / 'local_storage', 'ingredient_stops.db')


def init_db():
    with sqlite3.connect(DATABASE_PATH) as connection:
        cursor = connection.cursor()
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS stops (
            unit_name TEXT NOT NULL,
            ingredient_name TEXT NOT NULL
        );
        ''')


def get_ingredient_names_by_unit_name(unit_name: str) -> set[str]:
    with sqlite3.connect(DATABASE_PATH) as connection:
        cursor = connection.cursor()
        cursor.execute('SELECT ingredient_name FROM stops WHERE unit_name=?;', (unit_name,))
        return {row[0] for row in cursor.fetchall()}


def add_ingredient_names(unit_name: str, *ingredient_names: str):
    params = [(unit_name, ingredient_name) for ingredient_name in ingredient_names]
    with sqlite3.connect(DATABASE_PATH) as connection:
        cursor = connection.cursor()
        cursor.executemany('INSERT INTO stops VALUES (?,?)', params)


def clear_db():
    with sqlite3.connect(DATABASE_PATH) as connection:
        cursor = connection.cursor()
        cursor.execute('DELETE FROM stops;')
