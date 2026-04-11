up-infra:
	docker compose up -d

up-airflow:
	docker compose -f docker-compose-airflow.yml up --build -d

down:
	docker compose down
	docker compose -f docker-compose-airflow.yml down

generate-data:
	python src/producer.py
