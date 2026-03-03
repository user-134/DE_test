# 1. Берем за основу официальный стабильный образ Airflow
FROM apache/airflow:2.8.1

# 2. Переключаемся на пользователя root для установки системных программ
USER root

# 3. Устанавливаем Java (OpenJDK 17) — она критически важна для работы Apache Spark.
# Флаг --no-install-recommends и удаление кэша (rm -rf) делают наш итоговый образ намного легче!
RUN apt-get update \
  && apt-get install -y --no-install-recommends \
         openjdk-17-jre-headless \
  && apt-get autoremove -yqq --purge \
  && apt-get clean \
  && rm -rf /var/lib/apt/lists/*

# 4. Прописываем путь к Java, чтобы Spark и Airflow могли её найти
ENV JAVA_HOME=/usr/lib/jvm/java-17-openjdk-amd64

# 5. Возвращаемся на безопасного пользователя airflow
USER airflow

# 6. Копируем наш список библиотек из проекта внутрь контейнера
COPY requirements.txt /requirements.txt

# 7. Устанавливаем все нужные Python-библиотеки (pandas, pyspark, провайдеры)
# Флаг --no-cache-dir также экономит место, не сохраняя установочные архивы
RUN pip install --no-cache-dir -r /requirements.txt
