# Object Storage (S3-compatible) — практические задания

## Цель работы

Целью данной работы является практическое освоение базовых механизмов  
**S3-совместимого Object Storage**, которые используются в Data Lake и аналитических системах:

- программное взаимодействие с Object Storage (через boto3)
- управление доступом к данным (bucket policy)
- защита данных от перезаписи (versioning)
- автоматическое управление жизненным циклом данных (lifecycle policy)

Все задания выполнены на примере **MinIO** как S3-совместимого хранилища,  
что эквивалентно работе с AWS S3 / Selectel Object Storage по API и семантике.

## Примечание

В используемой версии MinIO Community Web UI отсутствует возможность настройки versioning и lifecycle policies.
Поэтому данные настройки были выполнены через официальный MinIO Client (mc), который является рекомендованным production-инструментом для управления S3-совместимым хранилищем.

## Используемое окружение

- Язык программирования: **Python 3**
- SDK для S3: **boto3**
- Object Storage: **MinIO (S3-compatible)**
- Способ развертывания: **Docker**
- Управление хранилищем:
  - MinIO Web UI (где доступно)
  - MinIO Client (`mc`) — официальный CLI / API-инструмент

### Endpoint’ы

- S3 API: `http://localhost:9002`
- Web UI: `http://localhost:9001`

---

### Задание №1 

## Реализация клиента

Реализация вынесена в отдельный класс `S3Client`, который инкапсулирует работу с S3 API.

Файл: `s3_client.py`

### Инициализация клиента

Клиент принимает параметры подключения:
- `endpoint` — адрес S3-хранилища
- `access_key` — ключ доступа
- `secret_key` — секретный ключ
- `bucket` — имя бакета

```python
client = S3Client(
    endpoint="http://localhost:9002",
    access_key="minioadmin",
    secret_key="minioadmin123",
    bucket="my-bucket"
)
```

####Метод list_files()
Возвращает список всех объектов, находящихся в указанном бакете.
Если бакет пуст — возвращается пустой список
Если объекты присутствуют — возвращается список их имён (keys)

Возвращаемое значение
```python
list[str]
```

Реализация
Метод использует вызов list_objects_v2 S3 API.

---

####Метод file_exists(object_name)
Проверяет существование объекта с указанным именем в бакете.

Параметры
object_name — имя объекта (ключ)

Возвращаемое значение
```python
bool
```
True — объект существует
False — объект отсутствует

Реализация
Метод использует head_object.
При отсутствии объекта отлавливается исключение ClientError.

Проверка работоспособности
Для демонстрации корректной работы клиента используется отдельный скрипт.

Файл: test_s3_client.py

Пример использования:

```python
from s3_client import S3Client

client = S3Client(
    endpoint="http://localhost:9002",
    access_key="minioadmin",
    secret_key="minioadmin123",
    bucket="my-bucket",
)

print("FILES:", client.list_files())
print("EXISTS sales.csv:", client.file_exists("sales.csv"))
```

Результат выполнения
При запуске тестового скрипта:

клиент успешно подключается к Object Storage

метод list_files() возвращает список объектов

метод file_exists() возвращает корректный булевый результат

Пример вывода:
```sql
FILES: ['sales.csv']
EXISTS sales.csv: True
```
--- 

Критерии приёма
✅ методы корректно принимают параметры
✅ методы возвращают ожидаемые значения
✅ код является рабочим
✅ продемонстрирована реальная работа с S3-совместимым хранилищем

Работоспособность подтверждена запуском тестового скрипта
и скриншотом вывода в консоли.

<img width="319" height="137" alt="Снимок экрана 2026-02-01 в 21 28 46" src="https://github.com/user-attachments/assets/c2c34f58-76b1-4134-8e1c-8b3237291631" />

---

Задание №2 состоит из трёх частей:
1. Настройка bucket policy (public read / private write)
2. Включение versioning и работа с версиями объектов
3. Настройка lifecycle policy (автоматическое удаление объектов)

---

## ЧАСТЬ 1. Bucket Policy (Public Read / Private Write)

### Требования
- Любой пользователь может читать объекты из бакета
- Запись в бакет разрешена только владельцу (по access/secret key)

### Реализация

Настройка выполнена **через MinIO Web UI**:

1. В бакете включён **Anonymous / Public Read** доступ
2. Публичная запись (PUT) отключена
3. Запись возможна только при наличии корректных credentials

### Проверка

- Публичное чтение:
  - Файл успешно скачивается по прямой ссылке в режиме инкогнито
- Публичная запись:
  - PUT-запрос без credentials возвращает `AccessDenied`
- Запись с ключами владельца:
  - Успешна

### Подтверждение
- Скриншоты:
  - настроек доступа бакета
    <img width="1352" height="69" alt="Снимок экрана 2026-02-01 в 18 49 56" src="https://github.com/user-attachments/assets/1fa9e6ef-1aac-4edb-9041-3da652996193" />

---


## ЧАСТЬ 2. Versioning

### Требования
- Включить versioning на бакете
- Загрузить файл с одинаковым именем несколько раз
- Скачать предыдущую версию файла

### Реализация

В используемой версии **MinIO Community Web UI отсутствует настройка Versioning**,  
поэтому versioning был включён **через официальный MinIO Client (`mc`)**, что является production-подходом.

#### Включение versioning

```bash
mc version enable localminio/my-bucket
```

Проверка:
```bash
mc version info localminio/my-bucket
```

Загрузка файла несколько раз
```bash
mc cp sales.csv localminio/my-bucket/sales.csv
# файл изменён
mc cp sales.csv localminio/my-bucket/sales.csv
```

Просмотр версий
```bash
mc ls --versions localminio/my-bucket/sales.csv
```

Скачивание предыдущей версии

```bash
mc cp --version-id <OLD_VERSION_ID> \
  localminio/my-bucket/sales.csv \
  sales_old.csv
```

Подтверждение:

- Скрин списка версий объекта
<img width="764" height="90" alt="Снимок экрана 2026-02-01 в 19 22 29" src="https://github.com/user-attachments/assets/c4a8f28d-688b-4aae-b4c0-f2bf249bd0c0" />

Скрин скачивания старой версии
<img width="1346" height="54" alt="Снимок экрана 2026-02-01 в 19 24 46" src="https://github.com/user-attachments/assets/33f9a1f0-07a7-422e-9df8-58a3c6c599ab" />

---

## ЧАСТЬ 3. Lifecycle Policy (Auto Delete)

Требования
Автоматическое удаление объектов через 3 дня

Реализация
Lifecycle policy также настроена через MinIO Client (mc),
так как Web UI Community Edition не предоставляет интерфейс для ILM.

Добавление lifecycle-правила
```bash
mc ilm add --expire-days 3 localminio/my-bucket
```

Проверка правила
```bash
mc ilm ls localminio/my-bucket
```

Правило:

Status: Enabled

Expiration: 3 days

⚠️ Ожидание фактического удаления объектов не требуется —
достаточно наличия активного правила.

Подтверждение
Скрин вывода mc ilm ls

<img width="700" height="147" alt="Снимок экрана 2026-02-01 в 19 29 01" src="https://github.com/user-attachments/assets/ef8eaf59-5738-431a-a20f-ab39a9c57021" />

---

Итог
В ходе выполнения задания:
- Настроены политики доступа к бакету
- Реализована защита от перезаписи данных с помощью versioning
- Настроена автоматическая очистка хранилища через lifecycle policy

Все требования задания выполнены.
Использованы допустимые способы настройки: Web UI и S3-compatible API (MinIO Client).

---

