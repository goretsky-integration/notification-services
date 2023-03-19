import textwrap

import pytest

import models


@pytest.fixture
def expected_config() -> models.Config:
    return models.Config(
        country_code='ru',
        logging=models.LoggingConfig(
            level='DEBUG',
            file_path='/var/log/gi/logs.log',
        ),
        message_queue=models.MessageQueueConfig(
            rabbitmq_url='amqp://127.0.0.1:5672',
        ),
        partial_ingredients=models.PartialIngredientStopSalesConfig(
            allowed_ingredient_names={"цыпленок"},
            disallowed_ingredient_names={"сыр", "косичка"}
        ),
        cheated_orders=models.CheatedOrdersConfig(
            skipped_phone_numbers={'796263637912'},
        ),
        api=models.APIConfig(
            auth_api_base_url='http://127.0.0.1:8000/auth',
            dodo_api_base_url='http://127.0.0.1:8000/gi',
            database_api_base_url='http://127.0.0.1:8000/db',
        ),
    )


@pytest.fixture
def config_string() -> str:
    return textwrap.dedent('''\
        country_code = "ru"
        [logging]
        level = "DEBUG"
        file_path = "/var/log/gi/logs.log"

        [api]
        dodo_api_url = "http://127.0.0.1:8000/gi"
        database_api_url = "http://127.0.0.1:8000/db"
        auth_api_url = "http://127.0.0.1:8000/auth"

        [partial_ingredient_stop_sales]
        disallowed_ingredient_names = [
            "сыр",
            "косичка",
        ]
        allowed_ingredient_names = [
            "цыпленок",
        ]

        [cheated_orders]
        skipped_phone_numbers = [
            "796263637912",
        ]

        [message_queue]
        rabbitmq_url = "amqp://127.0.0.1:5672"
    ''')
