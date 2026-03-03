# 🚀 AnalystAutoFlow

![Python](https://img.shields.io/badge/python-3.9+-blue.svg)
![Airflow](https://img.shields.io/badge/Airflow-2.8.1-007A88?logo=Apache%20Airflow)
![Docker](https://img.shields.io/badge/docker-%230db7ed.svg?logo=docker&logoColor=white)
![PostgreSQL](https://img.shields.io/badge/postgres-%23316192.svg?logo=postgresql&logoColor=white)

**AnalystAutoFlow** — это инструмент автоматической кодогенерации, который работает как мост между аналитиками данных и инфраструктурой Data Engineering. 

Система автоматически сканирует директории со скриптами аналитиков (Python/SQL), извлекает метаданные, валидирует синтаксис (через AST) и генерирует готовые к продакшену DAG-файлы для Apache Airflow с помощью шаблонизатора Jinja2.

## 🌟 Ключевые возможности

* **Zero-Airflow Knowledge для аналитиков:** Аналитикам не нужно знать синтаксис Airflow. Они просто пишут свой `.py` или `.sql` код и добавляют метаданные в комментарии.
* **Умный парсинг:** Автоматическое определение `dag_id`, `schedule`, `owner` через регулярные выражения.
* **Безопасность (AST Validation):** Перед сохранением сгенерированного DAGа, код проверяется на синтаксические ошибки через встроенную библиотеку `ast`. Битовые файлы не попадают в продакшен.
* **Динамический маппинг задач:** Скрипты автоматически превращаются в `PythonOperator` или `SQLExecuteQueryOperator` в зависимости от расширения файла.
* **Готовая инфраструктура:** Полный стек (Airflow, Celery, Redis, PostgreSQL) разворачивается через `docker-compose`.

## 🏗 Архитектура

Проект состоит из двух основных компонентов:
1. **Генератор (Python + Jinja2):** Парсит исходники, рендерит шаблоны, пишет логи.
2. **Оркестратор (Docker + Airflow):** Исполняет сгенерированные графы на архитектуре с CeleryExecutor.

## 🚀 Быстрый старт

### 1. Подготовка окружения
Клонируйте репозиторий и создайте файл переменных окружения:
```bash
git clone [https://github.com/your-username/AnalystAutoFlow.git](https://github.com/your-username/AnalystAutoFlow.git)
cd AnalystAutoFlow
cp .env.example .env
```

2. Запуск генератора
Положите скрипты аналитиков в папку projects/название_дага/ и запустите скрипт:

```bash
python generator.py
```
Сгенерированные файлы автоматически появятся в airflow/dags/, а логи запуска запишутся в generation.log.

3. Поднятие инфраструктуры Airflow
Запустите Docker Compose:

```bash
docker-compose up -d --build
```
Web UI будет доступен по адресу: http://localhost:8080.

💡 Пример использования
Входящий файл аналитика (projects/sales_report/01_extract.py):

```python
# dag_id: daily_sales_report
# schedule: @daily
# owner: data_analytics_team

def extract_data():
    print("Extracting data...")
```
Результат (автоматически в airflow/dags/gen_daily_sales_report.py):

```python
with DAG(dag_id='daily_sales_report', schedule_interval='@daily', ...) as dag:
    task_01_extract = PythonOperator(...)
    # Задачи автоматически выстраиваются в цепочку:
    task_01_extract >> task_02_transform
```
📂 Структура проекта

```Plaintext
├── airflow/                 # Смонтированные volume для Airflow (dags, logs, plugins)
├── projects/                # Исходные скрипты аналитиков
├── docker-compose.yml       # Инфраструктура (Airflow, Postgres, Redis)
├── requirements.txt         # Зависимости Python
├── dag_template.j2          # Трафарет Jinja2 для генерации DAGов
├── generator.py             # Главный скрипт кодогенерации
└── .env.example             # Пример переменных окружения
```
