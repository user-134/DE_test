# 🚀 AnalystAutoFlow: Автоматическая генерация DAG для Apache Airflow

![Python](https://img.shields.io/badge/python-3.9+-blue.svg)
![Airflow](https://img.shields.io/badge/Airflow-2.8.1-007A88?logo=Apache%20Airflow)
![Docker](https://img.shields.io/badge/docker-%230db7ed.svg?logo=docker&logoColor=white)
![PostgreSQL](https://img.shields.io/badge/postgres-%23316192.svg?logo=postgresql&logoColor=white)
![pytest](https://img.shields.io/badge/pytest-passing-success.svg?logo=pytest)

**AnalystAutoFlow** - это инструмент кодогенерации, который автоматически превращает SQL и Python скрипты аналитиков в готовые к продакшену DAG-файлы для Airflow. Аналитикам больше не нужно знать синтаксис Airflow: достаточно добавить метаданные в комментарии, а система сама построит граф задач, валидирует синтаксис и развернет код.

## 🌟 Ключевые возможности

* **Zero-Airflow Knowledge:** Аналитики пишут чистый Python или SQL. Вся логика оркестрации (операторы, связи, расписания) генерируется под капотом.
* **Smart Parsing & Jinja2 Templating:** Автоматическое извлечение `dag_id`, `schedule` и `owner` через регулярные выражения с последующим рендерингом через шаблоны Jinja2.
* **AST Validation (Безопасность кода):** Перед сохранением каждый сгенерированный DAG проходит строгую проверку синтаксиса через встроенную библиотеку `ast`. Невалидный код никогда не попадет в Airflow.
* **Кастомная Docker-инфраструктура:** Полный стек (Airflow, CeleryExecutor, PostgreSQL, Redis) разворачивается через `docker-compose`. В кастомный образ вшита **Java (OpenJDK 17)** для бесшовной интеграции с **Apache Spark**.
* **Developer Experience (DX):** Проект управляется через `Makefile` и покрыт изолированными unit-тестами (`pytest`).

## 🏗 Архитектура и структура проекта

```text
AnalystAutoFlow/
├── airflow/                 # Смонтированные volume для Airflow (dags, logs, plugins)
├── projects/                # Исходные скрипты аналитиков (входные данные)
├── tests/                   # Изолированные Unit-тесты (pytest)
│   └── test_generator.py
├── docker-compose.yml       # Инфраструктура оркестратора
├── Dockerfile               # Сборка кастомного образа Airflow (с Java и зависимостями)
├── requirements.txt         # Зависимости Python
├── dag_template.j2          # Трафарет Jinja2 для генерации кода
├── generator.py             # Ядро генерации
├── Makefile                 # Управление проектом
└── .env.example             # Шаблон переменных окружения
```

📋 Требования:
```text
Python 3.9+
Docker и Docker Compose
Make (для работы с Makefile)
```

## 🚀 Быстрый старт

1. Подготовка окружения
   
Клонируйте репозиторий и настройте переменные окружения:
```bash
git clone [https://github.com/user-134/DE_test.git](https://github.com/user-134/DE_test.git)
cd DE_test
cp .env.example .env
```
(Обязательно проверьте файл .env и укажите актуальные креды и AIRFLOW_UID).

Для установки локальных зависимостей (для автокомплита в IDE и запуска тестов):

```bash
pip install -r requirements.txt
```

2. Управление проектом (Makefile)
   
Для удобства все рутинные операции вынесены в Makefile. Выполните команду make help, чтобы увидеть список доступных команд:
```text
make up: Собирает кастомный Docker-образ и поднимает инфраструктуру Airflow.
make down: Останавливает и удаляет контейнеры оркестратора.
make generate: Запускает парсинг папки projects/ и генерирует DAG-файлы.
make test: Запускает набор Unit-тестов через pytest.
make clean: Удаляет кэш, логи и сгенерированные DAGи для чистой сборки.
```

💡 Пример использования (Workflow)

Шаг 1. Аналитик создает скрипты в папке проекта:

Путь: projects/sales_report/01_extract.py

```Python
# dag_id: daily_sales_report
# schedule: @daily
# owner: data_analytics_team

import pandas as pd

def extract_data():
    print("Extracting sales data from API...")
```
Путь: projects/sales_report/02_transform.sql
```SQL
DELETE FROM raw_sales WHERE amount IS NULL;
```

Шаг 2. Запуск генератора:

```Bash
make generate
```

Шаг 3. Автоматический результат:

Система валидирует код и создает готовый файл airflow/dags/gen_daily_sales_report.py:

```Python
# Сгенерировано автоматически AnalystAutoFlow 🤖
with DAG(dag_id='daily_sales_report', schedule_interval='@daily', ...) as dag:
    task_01_extract = PythonOperator(...)
    task_02_transform = SQLExecuteQueryOperator(...)
    
    # Цепочка выполнения выстраивается автоматически
    task_01_extract >> task_02_transform
```

🧪 Тестирование

Проект использует pytest и встроенную фикстуру tmp_path для мокирования файловой системы, что гарантирует чистоту тестов и отсутствие мусора на диске.

Для запуска тестов выполните:

```Bash
make test
```
---

## История проекта: от исходных данных до финального результата в Airflow.



<img width="518" height="276" alt="Снимок экрана 2026-03-05 в 17 16 46" src="https://github.com/user-attachments/assets/a532352d-a4c1-46f9-8173-71c7ecb39576" />

Файл 01_extract.py. Демонстрирует главную фичу - Zero-Airflow подход для аналитиков.






