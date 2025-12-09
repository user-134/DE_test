# ETL Pipeline: PostgreSQL → Kafka → ClickHouse

Этот проект демонстрирует передачу событий пользователей из PostgreSQL в ClickHouse через Kafka.  
Основная цель — надёжная миграция данных без дублирования и с возможностью масштабирования.

![Python](https://img.shields.io/badge/Python-3.11-blue?logo=python&logoColor=white)
![Docker](https://img.shields.io/badge/Docker-Compose-blue?logo=docker&logoColor=white)
![Kafka](https://img.shields.io/badge/Kafka-Apache-orange?logo=apachekafka&logoColor=white)
![ClickHouse](https://img.shields.io/badge/ClickHouse-DB-lightgrey?logo=clickhouse&logoColor=orange)
![PostgreSQL](https://img.shields.io/badge/PostgreSQL-DB-blue?logo=postgresql&logoColor=white)

---

## 📦 Архитектура

```nginx
PostgreSQL → Kafka Producer → Kafka → Kafka Consumer → ClickHouse
```

- **PostgreSQL** — хранит события пользователей (`user_logins`)  
- **Kafka Producer** — отправляет только новые строки (`sent_to_kafka = FALSE`) в Kafka и помечает их как отправленные  
- **Kafka** — броке сообщений, обеспечивает надёжную доставку  
- **Kafka Consumer** — получает события и вставляет их в ClickHouse  
- **ClickHouse** — хранит данные без дублирования  

---

## 🔑 Особенности

- **sent_to_kafka BOOLEAN** — флаг в PostgreSQL, предотвращающий повторную отправку строк  
- **id в ClickHouse** — сохраняется для контроля уникальности, reconciliation и предотвращения дубликатов  
- **MergeTree** в ClickHouse без id не защищает от дубликатов  
- Консьюмер **не проверяет `sent_to_kafka`**, он получает всё, что пришло из Kafka  

---

## 🚀 Запуск проекта

### 1️⃣ Создать колонку sent_to_kafka в PostgreSQL:

```sql
ALTER TABLE user_logins ADD COLUMN sent_to_kafka BOOLEAN DEFAULT FALSE;
```
---

### 2️⃣ Запустить Docker Compose:

```python
docker-compose up -d
```

Сервисы, которые поднимаются:
- **Zookeeper**
- **Kafka**
- **PostgreSQL**
- **ClickHouse**

---

### 3️⃣ Запустить продюсер:

```python
python producer_pg_to_kafka.py
```

- **Отправляет только новые события в Kafka**
- **После отправки обновляет флаг sent_to_kafka = TRUE**

---

### 4️⃣ Запустить консьюмера:

```python
python consumer_to_clickhouse.py
```

- **Получает события из Kafka**
- **Вставляет их в ClickHouse**
- **Данные поступают один раз, без дублей**

---

### 5️⃣ Проверить результат:

```sql
-- PostgreSQL

SELECT id, username, sent_to_kafka
FROM user_logins
ORDER BY id;

-- Все отправленные строки должны иметь sent_to_kafka = TRUE.
```

```sql
-- ClickHouse

SELECT *
FROM user_logins
ORDER BY event_time;

-- Все события из Kafka должны быть вставлены один раз.
```

---

⚡ Преимущества

- **Надёжная миграция данных без дублирования**
- **Простое масштабирование — новые консьюмеры с разными group_id получают все события**
- **Безопасное хранение конфиденциальных данных через .env и config.py**
- **Лёгкая интеграция с другими системами**

---

🔧 Рекомендации

- **Использовать client.insert() вместо client.command() для ClickHouse, чтобы избежать проблем с кавычками и SQL-инъекциями**
- **Настроить group_id для Kafka Consumer, чтобы контролировать поток сообщений**
- **Добавить обработку ошибок через try/except для устойчивости пайплайна**

---

📂 Структура проекта

```bash
project/
│
├── producer_pg_to_kafka.py   # отправляет новые строки из Postgres в Kafka
├── consumer_to_clickhouse.py # читает Kafka и вставляет в ClickHouse
├── config.py                 # хранит конфигурацию проекта
├── .env.example              # ппример переменных окружения
├── docker-compose.yml        # поднимает все сервисы
└── README.md
```

---

🌱 Пример переменных окружения

```bash
# PostgreSQL
PG_USER=admin
PG_PASS=admin
PG_DB=test_db
PG_HOST=localhost
PG_PORT=5432

# ClickHouse
CH_HOST=localhost
CH_PORT=8123
CH_USER=user
CH_PASS=strongpassword

# Kafka
KAFKA_BOOTSTRAP=localhost:9092
KAFKA_TOPIC=user_events
```
---



