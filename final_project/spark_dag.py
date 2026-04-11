from airflow import DAG
from airflow.operators.bash import BashOperator
from datetime import datetime

# Создаем маршрут, который запускается каждый день в 3:00 ночи
with DAG(dag_id="spark_customer_features", start_date=datetime(2026, 4, 10), schedule_interval="0 10 * * *", catchup=False) as dag:

    run_etl_job = BashOperator(
        task_id="run_pyspark_script",
        bash_command="python /opt/airflow/spark_etl.py"
    )
