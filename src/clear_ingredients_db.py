from core.utils import logger
from ingredient_stop_sales import db


def main():
    db.clear_db()
    logger.info('Database has been cleared')


if __name__ == '__main__':
    main()
