import os
from pyspark.sql import SparkSession
from pyspark.sql import functions as F
from datetime import datetime
from pyspark.sql.types import ArrayType, StructType, StructField, StringType

# Определяем, где мы запускаемся: в Docker (Airflow) или локально (PyCharm)
if os.getenv("AIRFLOW_HOME"):
    TARGET_HOST = "host.docker.internal"
else:
    TARGET_HOST = "localhost"

# ==========================================
# ШАГ 1: ЗАПУСК И НАСТРОЙКИ (Extract)
# ==========================================
spark = SparkSession.builder \
    .appName("Final_Project") \
    .config("spark.jars.packages", "ru.yandex.clickhouse:clickhouse-jdbc:0.3.2,org.apache.hadoop:hadoop-aws:3.3.4,com.amazonaws:aws-java-sdk-bundle:1.12.262") \
    .config("spark.hadoop.fs.s3a.access.key", "admin") \
    .config("spark.hadoop.fs.s3a.secret.key", "adminpassword") \
    .config("spark.hadoop.fs.s3a.endpoint", f"http://{TARGET_HOST}:9002") \
    .config("spark.hadoop.fs.s3a.path.style.access", "true") \
    .config("spark.hadoop.fs.s3a.connection.ssl.enabled", "false") \
    .config("spark.hadoop.fs.s3a.impl", "org.apache.hadoop.fs.s3a.S3AFileSystem") \
    .config("spark.hadoop.fs.s3a.connection.timeout", "60000") \
    .config("spark.hadoop.fs.s3a.connection.establish.timeout", "5000") \
    .getOrCreate()

# Читаем чистые данные из ClickHouse (MART слой)
df_customers = spark.read.format("jdbc") \
    .option("url", f"jdbc:clickhouse://{TARGET_HOST}:8123/default") \
    .option("dbtable", "customers_mart") \
    .option("user", "admin") \
    .option("password", "admin") \
    .option("driver", "ru.yandex.clickhouse.ClickHouseDriver") \
    .load()

df_purchases = spark.read.format("jdbc") \
    .option("url", f"jdbc:clickhouse://{TARGET_HOST}:8123/default") \
    .option("dbtable", "purchases_mart") \
    .option("user", "admin") \
    .option("password", "admin") \
    .option("driver", "ru.yandex.clickhouse.ClickHouseDriver") \
    .load()

# ==========================================
# ШАГ 2: ВЫЧИСЛЕНИЯ (Transform)
# ==========================================

df_purchases = df_purchases.withColumn("customer", F.get_json_object(F.col("customer"), "$.customer_id"))

# Сшиваем таблицы по ID клиента
df_joined = df_purchases.join(
    df_customers,
    df_purchases.customer == df_customers.customer_id,
    "inner"
)

# Описываем схему (что именно спрятано внутри текста JSON)
items_schema = ArrayType(StructType([
    StructField("product_id", StringType(), True),
    StructField("category", StringType(), True)
]))

# Создаем base df (1 строка = 1 чек)
df_base = df_joined.withColumn("items_array", F.from_json(F.col("items"), items_schema))

# Создаем exploded df (1 строка = 1 товар)
df_exploded = df_base.withColumn("item", F.explode(F.col("items_array")))

# Считаем бизнес-метрики по чекам и профилям
df_features_base = df_base.groupBy("customer_id").agg(
    # Зарегистрировался менее 30 дней назад
    F.when(F.datediff(F.current_date(), F.min("registration_date")) < 30, 1).otherwise(0).alias("new_customer"),

    # Пользовался доставкой хотя бы раз
    F.max(F.when(F.col("is_delivery") == True, 1).otherwise(0)).alias("delivery_user"),

    # Средняя корзина > 1000 руб.
    F.when(F.avg("total_amount") > 1000, 1).otherwise(0).alias("bulk_buyer"),

    # Средняя корзина < 200 руб.
    F.when(F.avg("total_amount") < 200, 1).otherwise(0).alias("low_cost_buyer"),

    # Делал покупки после 20:00 (хотя бы раз)
    F.max(F.when(F.hour("purchase_datetime") >= 20, 1).otherwise(0)).alias("night_shopper"),

    # Делал покупки до 10:00
    F.max(F.when(F.hour("purchase_datetime") <= 10, 1).otherwise(0)).alias("morning_shopper"),

    # Лояльный клиент (карта и ≥3 покупки)
    F.when((F.count("purchase_id") >= 3) & (F.max("is_loyalty_member") == 1), 1).otherwise(0).alias("loyal_customer"),

    # Оплачивал картой ≥ 70% покупок
    F.when(
        F.sum(F.when(F.col("payment_method") == "card",
                     1).otherwise(0)) / F.count("purchase_id") >= 0.7,
           1
    ).otherwise(0).alias("prefers_card"),

    # Делал более 2 покупок за последние 30 дней
    F.when(
        F.sum(F.when(F.datediff(F.current_date(), F.col("purchase_datetime")) <= 30,
                     1).otherwise(0)) > 2,
           1
    ).otherwise(0).alias("recurrent_buyer"),

    # Купил на сумму >2000₽ за последние 7 дней
    F.when(
        F.sum(F.when(F.datediff(F.current_date(), F.col("purchase_datetime")) <= 7
                     , F.col("total_amount")).otherwise(0)) > 2000,
        1
    ).otherwise(0).alias("recent_high_spender"),

    # Среднее кол-во позиций в корзине ≥4
    F.when(F.avg(F.size(F.col("items_array"))) >= 4, 1).otherwise(0).alias("family_shopper"),

    # Диагностические метрики
    #F.round(F.sum("total_amount"), 2).alias("lifetime_value"), # LTV
    #F.count("purchase_id").alias("total_purchases"), # Количество покупок
    #F.round(F.avg("total_amount"), 2).alias("avg_receipt") # Средний чек
)

# Считаем бизнес-метрики по конкретным товарам
df_features_items = df_exploded.groupBy("customer_id").agg(

    # Покупал молочные продукты за последние 30 дней
    F.max(
        F.when(
            (F.col("item.category") == "milk") & (F.datediff(F.current_date(), F.col("purchase_datetime")) <= 30),
                 1
        ).otherwise(0)).alias("bought_milk_last_30d"),

    # Покупал ≥4 разных категорий продуктов
    F.when(F.countDistinct(F.col("item.category")) >= 4, 1).otherwise(0).alias("varied_shopper")
)

# Финальная сборка
df_features = df_features_base.join(df_features_items, on="customer_id", how="inner")

# ==========================================
# ШАГ 3: ВЫГРУЗКА РЕЗУЛЬТАТА (Load)
# ==========================================

print("Проверка рассчитанных метрик:")
df_features.show(5)

# Генерируем строку с текущей датой в формате YYYY_MM_DD
current_date_str = datetime.now().strftime("%Y_%m_%d")

# Финальный путь
output_path = f"s3a://project-bucket/analytic_result_{current_date_str}"

# Отправляем готовые фичи в MinIO по протоколу S3
df_features.write.mode("overwrite").option("header", "true").csv(output_path)

#df_features.show()
print(f"Расчет метрик завершен и данные выгружены в MinIO по пути: {output_path}")
