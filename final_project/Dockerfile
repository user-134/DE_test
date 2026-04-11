# Берем официальный образ Airflow
FROM apache/airflow:2.8.1

# Временно становимся администратором (root), чтобы установить системную Java
USER root
RUN apt-get update \
  && apt-get install -y --no-install-recommends default-jre-headless \
  && apt-get autoremove -yqq --purge \
  && apt-get clean \
  && rm -rf /var/lib/apt/lists/*

# Указываем системе, где теперь лежит Java
ENV JAVA_HOME=/usr/lib/jvm/default-java

# Возвращаемся к правам обычного пользователя Airflow и ставим PySpark нужной версии
USER airflow
RUN pip install --no-cache-dir pyspark==3.5.3
