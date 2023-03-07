# Notification services
Сервисы которые генерируют события, которые попадают в [router](https://github.com/goretsky-integration/notifications-router).

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
- `country_code` - [список](https://dodo-brands.stoplight.io/docs/dodo-is/90fc31544cd42-dodo-is-api) допустимых значений.
- **logging:**
  - `level` - допустимые значения: `CRITICAL`, `ERROR`, `WARNING`, `INFO`, `DEBUG`.
  - `file_path` - путь до фалйа, куда будут записываться логи.
- **api:**
  - `dodo_api_url` - HTTP URL сервиса [Dodo API](https://github.com/goretsky-integration/api).
  - `database_api_url` - HTTP URL сервиса [Unit's routes database](https://github.com/goretsky-integration/unit-routes-database).
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

### Стопы по ингредиентам:
Запуск: 
```shell
python src/stop_sales_by_ingredients.py
```
Опциональные аргументы:
- `--remember` - сохранить UUID стопов в локальное хранилище.
- `--ignore-remembered` - проигнорировать стопы, сохраненные в локальном хранилище.
- `--only-partial-ingredients` - отфильтровать стопы, которые указаны в разделе __partial_ingredient_stop_sales__ в конфигурационном файле.
- `--include-empty-units` - создавать события по стопам даже у тех пиццерий, в которых на данных момент стопов нет.

### Стопы по улицам/секторам:
Запуск:
```shell
python src/stop_sales_v1.py
```
Обязательные аргументы:
- `--by` - источник стоп-продаж. Варианты: `streets`, `sectors`.
