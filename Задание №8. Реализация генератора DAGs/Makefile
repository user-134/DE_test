.PHONY: help up down restart logs generate test clean

# Команда по умолчанию, если написать просто `make`
help:
	@echo "🚀 Управление проектом AnalystAutoFlow:"
	@echo "  make up        - Поднять всю инфраструктуру Airflow (Docker)"
	@echo "  make down      - Остановить и удалить контейнеры"
	@echo "  make restart   - Перезапустить инфраструктуру"
	@echo "  make logs      - Посмотреть логи Airflow (webserver)"
	@echo "  make generate  - Запустить ручную генерацию DAG-ов"
	@echo "  make test      - Запустить автотесты pytest"
	@echo "  make clean     - Удалить сгенерированные файлы и логи"

# --- Docker ---
up:
	docker-compose up -d --build

down:
	docker-compose down

restart: down up

logs:
	docker-compose logs -f airflow-webserver

# --- Python ---
generate:
	python generator.py

test:
	pytest -v

# --- Утилиты ---
clean:
	rm -f airflow/dags/gen_*.py
	rm -f *.log
	rm -rf .pytest_cache
	@echo "🧹 Мусор успешно удален!"
