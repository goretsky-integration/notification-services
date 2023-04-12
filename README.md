# Notification services

Сервисы которые генерируют события, которые попадают
в [router](https://github.com/goretsky-integration/notifications-router).

<p align="center">
<a href="https://codecov.io/gh/goretsky-integration/notification-services" > 
 <img src="https://codecov.io/gh/goretsky-integration/notification-services/branch/main/graph/badge.svg?token=388WJ1TPXN"/> 
</a>

<a href="https://github.com/goretsky-integration/notification-services/actions/workflows/unittests.yml">
  <img src="https://github.com/goretsky-integration/notification-services/actions/workflows/unittests.yml/badge.svg" alt="unit test" />
</a>

<img src="https://camo.githubusercontent.com/449440850ba7a1fc6a2c78a4fe05a5ccc9fddc05a46b85aa17f9f8cf657cb73c/68747470733a2f2f696d672e736869656c64732e696f2f62616467652f707974686f6e2d332e31312d627269676874677265656e" alt="python">
</p>

---

### 📦 Настройка виртуального окружения

Создание виртуального окружения:

```shell
poetry env use python3.11
```

Активация виртуального окружения:

```shell
poetry shell
```

Установка необходимых зависимостей:

```shell
poetry install --without dev
```

---

### ⚙️ Конфигурационный файл

- `country_code` - [список](https://dodo-brands.stoplight.io/docs/dodo-is/90fc31544cd42-dodo-is-api) допустимых
  значений.
- **logging:**
    - `level` - допустимые значения: `CRITICAL`, `ERROR`, `WARNING`, `INFO`, `DEBUG`.
    - `file_path` - путь до фалйа, куда будут записываться логи.
- **api:**
    - `dodo_api_url` - HTTP URL сервиса [Dodo API](https://github.com/goretsky-integration/api).
    - `database_api_url` - HTTP URL
      сервиса [Unit's routes database](https://github.com/goretsky-integration/unit-routes-database).
    - `auth_api_url` - HTTP URL сервиса [Auth server](https://github.com/goretsky-integration/auth-server).
- **partial_ingredient_stop_sales:**
    - `disallowed_ingredient_names` - blacklist слов, по которым будут фильтроваться стопы по ингредиентам.
    - `allowed_ingredient_names` - while-list слов, по которым будут фильтроваться стопы по ингредиентам.
- **cheated_orders:**
    - `skipped_phone_numbers` - while-list номеров телефонов для сервиса **cheated orders**.
- **message_queue:**
    - `rabbitmq_url` - URL RabbitMQ.

---

### 🤖 Сервисы:

**❗️ Все сервисы нужно запускать из корня проекта ❗️**

### Стопы по каналам продаж:

Запуск:

```shell
python src/stop_sales_by_channels.py
```

Обязательные аргументы:

- `--sales-channel-names` - название канала продаж. Варианты: `delivery`, `dine_in`, `takeaway`.

Опциональные аргуметны:

- `--remember` - сохранить UUID стопов в локальное хранилище.
- `--ignore-remembered` - проигнорировать стопы, сохраненные в локальном хранилище.

### Стопы по ингредиентам:

Запуск:

```shell
python src/stop_sales_by_ingredients.py
```

Опциональные аргументы:

- `--remember` - сохранить UUID стопов в локальное хранилище.
- `--ignore-remembered` - проигнорировать стопы, сохраненные в локальном хранилище.
- `--only-partial-ingredients` - отфильтровать стопы, которые указаны в разделе __partial_ingredient_stop_sales__ в
  конфигурационном файле.
- `--include-empty-units` - создавать события по стопам даже у тех пиццерий, в которых на данных момент стопов нет.

### Стопы по улицам/секторам:

Запуск:

```shell
python src/stop_sales_v1.py
```

Обязательные аргументы:

- `--by` - источник стоп-продаж. Варианты: `streets`, `sectors`.

### Использованные промо-коды:

Запуск:

```shell
python src/promo_codes.py
```

### Сертификаты за опоздание:

Запуск:

```shell
python src/late_delivery_vouchers.py
```
