from pyspark.sql import SparkSession

# Берём стабильную версию от Яндекса
spark = SparkSession.builder \
    .appName("ClickhouseToS3_ETL") \
    .config("spark.jars.packages", "ru.yandex.clickhouse:clickhouse-jdbc:0.3.2") \
    .getOrCreate()

# Читаем всю таблицу целиком
df = spark.read \
    .format("jdbc") \
    .option("url", "jdbc:clickhouse://localhost:8123/default") \
    .option("user", "admin") \
    .option("password", "admin") \
    .option("driver", "ru.yandex.clickhouse.ClickHouseDriver") \
    .option("dbtable", "customers_mart") \
    .load()

df.printSchema()
df.show(5)
