# 🛒 E-Commerce Data Pipeline & Feature Store

![Python](https://img.shields.io/badge/Python-3.8+-blue.svg?style=for-the-badge&logo=python&logoColor=white)
![Apache Spark](https://img.shields.io/badge/Apache%20Spark-3.3+-orange.svg?style=for-the-badge&logo=apachespark&logoColor=white)
![Apache Airflow](https://img.shields.io/badge/Apache%20Airflow-2.5+-blueviolet.svg?style=for-the-badge&logo=apacheairflow&logoColor=white)
![ClickHouse](https://img.shields.io/badge/ClickHouse-OLAP-yellow.svg?style=for-the-badge&logo=clickhouse&logoColor=white)
![MinIO](https://img.shields.io/badge/MinIO-S3_Storage-red.svg?style=for-the-badge&logo=minio&logoColor=white)
![Kafka](https://img.shields.io/badge/Kafka-Streaming-black.svg?style=for-the-badge&logo=apachekafka&logoColor=white)
![Docker](https://img.shields.io/badge/Docker-Containerized-2496ED.svg?style=for-the-badge&logo=docker&logoColor=white)

> **💡 От разрозненных транзакций к единому профилю клиента.** <br>
> 
> Автоматизированный End-to-End конвейер, эмулирующий инфраструктуру сетевого ритейла. \
> Проект объединяет потоковую загрузку данных (Kafka → ClickHouse) и распределенную батч-обработку (PySpark) для трансформации полуструктурированных логов в унифицированную матрицу признаков. \
> Итоговый Feature Store служит надежным фундаментом для BI-аналитики и обучения ML-моделей.

## 🏗️ Архитектура конвейера 

Пайплайн спроектирован по гибридной архитектуре (Streaming + Batch). 

Сырые данные генерируются в Kafka и оседают в ClickHouse (MART слой). Затем PySpark извлекает данные, рассчитывает сложные бизнес-метрики и выгружает готовый Feature Store в S3-хранилище. Оркестрация и расписание контролируются Apache Airflow.

```mermaid
graph LR
    %% Иконки и узлы
    node_kafka[fa:fa-paper-plane Kafka]
    node_ch[fa:fa-database ClickHouse OLAP]
    node_spark[fa:fa-bolt PySpark ETL]
    node_minio[fa:fa-cloud MinIO S3]
    node_airflow[fa:fa-clock Apache Airflow]
    node_gen[fa:fa-code Python Generator]

    %% Группировка
    subgraph STREAMS [Layer 1: Streaming]
        node_gen == JSON ==> node_kafka
    end

    subgraph DWH [Layer 2: MART]
        node_kafka -- Real-time Ingest --> node_ch
    end

    subgraph BATCH [Layer 3: ETL]
        node_ch -- JDBC Extract --> node_spark
        node_spark -. Aggregate & Join .-> node_spark
    end

    subgraph LAKE [Layer 4: Data Lake]
        node_spark ==>|Save as CSV| node_minio
    end

    subgraph OPS [Orchestration]
        node_airflow -->|Trigger daily at 10:00 AM| node_spark
    end

    %% Стилизация
    classDef streams fill:#e1f5fe,stroke:#01579b,stroke-width:2px,color:#01579b,font-weight:bold;
    classDef dwh fill:#fff3e0,stroke:#e65100,stroke-width:2px,color:#e65100,font-weight:bold;
    classDef batch fill:#e8f5e9,stroke:#1b5e20,stroke-width:2px,color:#1b5e20,font-weight:bold;
    classDef lake fill:#fce4ec,stroke:#880e4f,stroke-width:2px,color:#880e4f,font-weight:bold;
    classDef ops fill:#f3e5f5,stroke:#4a148c,stroke-width:2px,color:#4a148c,font-weight:bold;

    class node_gen,node_kafka streams;
    class node_ch dwh;
    class node_spark batch;
    class node_minio lake;
    class node_airflow ops;
```

## 🎯 Бизнес-ценность: Матрица признаков (Feature Store)

На выходе пайплайн генерирует обогащенную витрину (13+ уникальных метрик на клиента), готовую для передачи Data Science команде (прогнозирование оттока, кластеризация) или аналитикам:

* **Поведенческие паттерны:** `recurrent_buyer`, `recent_high_spender`, `night_shopper`, `morning_shopper`.
* **Финансовые метрики:** `lifetime_value` (LTV), `avg_receipt`, `bulk_buyer`, `low_cost_buyer`.
* **Продуктовая аналитика (JSON parsing):** `bought_milk_last_30d`, `varied_shopper` (покупки в 4+ разных категориях), `family_shopper` (корзина ≥ 4 позиций).
* **Лояльность:** `loyal_customer`, `delivery_user`.

## 📁 Структура репозитория 

В проекте используется модульная структура, разделяющая код инфраструктуры, логику оркестрации и скрипты обработки данных:

```text
📦 E-Commerce Data Pipeline
 ┣ 📂 dags                   # Направляемые ациклические графы (DAGs)
 ┃ ┗ 📜 spark_dag.py         # Логика оркестрации пайплайна в Airflow
 ┣ 📂 src                    # Исходный код пайплайна
 ┃ ┣ 📜 spark_etl.py         # Ядро: Трансформации PySpark и логика Feature Store
 ┃ ┣ 📜 data_generate.py     # Модуль: Генератор синтетических профилей и чеков
 ┃ ┣ 📜 producer.py          # Модуль: Отправка потоковых событий в Kafka
 ┃ ┣ 📜 etl_job.py           # Модуль: Альтернативные сценарии загрузки
 ┃ ┗ 📜 load_to_nosql.py     # Модуль: Интеграция с NoSQL решениями
 ┣ 📜 docker-compose.yml     # Инфраструктура Storage (ClickHouse, MinIO, Kafka, Zookeeper)
 ┣ 📜 docker-compose-airflow.yml # Инфраструктура Orchestration (Airflow, PostgreSQL, Redis)
 ┣ 📜 Dockerfile             # Кастомный образ: Airflow + Java + PySpark + ClickHouse JDBC
 ┣ 📜 Makefile               # Автоматизация команд запуска
 ┣ 📜 requirements.txt       # Зависимости Python
 ┣ 📜 .env.example           # Шаблон переменных окружения
 ┣ 📜 .gitignore             # Исключения для Git
 ┗ 📜 README.md              # Документация проекта
```

## 🛠️ Как развернуть и запустить локально

Вся инфраструктура упакована в Docker для быстрого старта "в один клик".

#### Шаг 1: Подготовка окружения

Склонируйте репозиторий и создайте необходимые директории для корректной работы Apache Airflow (во избежание проблем с правами доступа):

```bash
git clone https://github.com/user-134/DE_test.git
cd DE_test/final_project

# Создаем папки для монтирования volumes Airflow
mkdir -p ./logs ./plugins

# Копируем шаблон переменных окружения
cp .env.example .env
```
#### Шаг 2: Запуск слоя хранения и оркестрации (через Makefile)

В проекте настроен Makefile для удобного управления контейнерами:

```bash
# 1. Поднимаем базовую инфраструктуру (ClickHouse, MinIO, Kafka)
make up-infra

# 2. Собираем кастомный образ и запускаем Airflow
make up-airflow
```

(При первом запуске Airflow потребуется около минуты на инициализацию базы данных).

#### Шаг 3: Генерация потоковых данных 

Чтобы конвейеру было с чем работать, запустите скрипт-продюсер. Он сгенерирует синтетические транзакции и отправит их в Kafka:

```bash
pip install -r requirements.txt
make generate-data
```
#### Шаг 4: Доступ к интерфейсам и запуск DAG

Система работает в фоне. Мониторинг осуществляется через Web-интерфейсы:

- 🎯 Airflow UI: http://localhost:8080 (Логин/Пароль: airflow / airflow)

- 🪣 MinIO Console (S3): http://localhost:9001 (Логин/Пароль: admin / adminpassword)

- 📊 ClickHouse: localhost:8123

Зайдите в Airflow, найдите DAG spark_customer_features, переведите тумблер в состояние Unpause и нажмите Trigger DAG (▶️).

---

## 📸 Результаты работы конвейера

✅ Успешное выполнение направленного графа (DAG) в Apache Airflow:

<img width="1440" height="239" alt="Снимок экрана 2026-04-11 в 21 17 41" src="https://github.com/user-attachments/assets/97accf69-2663-4ba0-8f87-54be51358811" />

<img width="1440" height="263" alt="Снимок экрана 2026-04-11 в 21 18 48" src="https://github.com/user-attachments/assets/227e7579-e92d-4c2e-b5b4-e5c323cebb8f" />

✅ Сформированная матрица признаков, выгруженная в MinIO (S3):

<img width="1440" height="346" alt="Снимок экрана 2026-04-11 в 21 20 35" src="https://github.com/user-attachments/assets/f0878f46-297c-4399-a5c3-a3abc1bded64" />

---

## 🧠 Под капотом PySpark ETL

Самая интересная техническая задача проекта — обработка полуструктурированных данных без потери производительности и искажения метрик. В исходном слое (ClickHouse) корзина покупателя хранится в виде сырого строкового JSON-массива: `[{"category": "milk"}, {"category": "bread"}]`.

Чтобы рассчитать корректные бизнес-метрики, пайплайн использует паттерн **Split-Aggregation**.

#### 1. Парсинг и Развертывание (The Explode)
PySpark строго типизирует сырую строку через `StructType` и применяет функцию `F.explode`, превращая один чек в набор независимых строк (одна строка = один товар).

```python
# Извлекаем категории для продуктовой аналитики
df_exploded = df_base.withColumn("item", F.explode(F.from_json(F.col("items"), items_schema)))
```
#### 2. Split-Aggregation Pattern (Защита от дублей)
Если считать средний чек (Base metric) на "взорванных" данных, чеки с большим количеством товаров получат больший математический вес, что приведет к искажению аналитики. Поток данных физически разделяется на две ветки агрегации, которые затем безопасно сшиваются обратно:

```mermaid
graph TD
    A[(Raw DataFrame<br>от ClickHouse)] -->|1 строка = 1 чек| B[Base DF]
    A --> C{F.explode}
    C -->|1 строка = 1 товар| D[Items DF]

    B -->|LTV, Ср. чек, Частота| E(Aggregated Base Features)
    D -->|Поиск 'milk', Разнообразие категорий| F(Aggregated Items Features)

    E --> G((Inner Join<br>by customer_id))
    F --> G
    
    G --> H[(Финальная матрица<br>Feature Store)]
    
    classDef source fill:#fff3e0,stroke:#ff9800,stroke-width:2px;
    classDef transform fill:#e3f2fd,stroke:#2196f3,stroke-width:2px;
    classDef agg fill:#e8f5e9,stroke:#4caf50,stroke-width:2px;
    classDef target fill:#fce4ec,stroke:#e91e63,stroke-width:2px;
    
    class A source;
    class B,D,C transform;
    class E,F agg;
    class H target;
```
#### 3. Идемпотентность и Оркестрация (Airflow Safe)

Пайплайн спроектирован так, что повторный запуск задачи (Retry) при сбое не приведет к дублированию данных: 
* **Overwrite Mode:** Данные записываются в S3 с использованием `mode("overwrite")`.
* **Dynamic Partitioning:** Имя финального файла формируется динамически (`analytic_result_YYYY_MM_DD`), гарантируя консистентность срезов данных по дням.

---

## 🚀 Дальнейшее развитие

- [ ] Интеграция `dbt` для управления трансформациями на слое DWH.
- [ ] Добавление метрик качества данных (Data Quality checks) через `Great Expectations`. 
- [ ] Развертывание дашборда `Apache Superset` поверх финальной витрины для визуализации оттока.
