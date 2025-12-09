import config
from kafka import KafkaConsumer
import json
import clickhouse_connect
import time

consumer = KafkaConsumer(
    config.KAFKA_TOPIC,
    bootstrap_servers=config.KAFKA_BOOTSTRAP,
    value_deserializer=lambda x: json.loads(x.decode("utf-8")),
    group_id="user_events_group",
)

client = clickhouse_connect.get_client(
    host=config.CH_HOST,
    port=config.CH_PORT,
    username=config.CH_USER,
    password=config.CH_PASS
)

# В консьюмере должен быть group_id. Иначе консьюмер работает вот так: каждый запуск = чтение топика заново → дубликаты в ClickHouse.
# Теперь Kafka гарантирует:
# если ты уже читал сообщение → больше не получишь
# если упал → начнёшь от последнего коммита

client = clickhouse_connect.get_client(host='localhost', port=8123, username='user', password='strongpassword')

client.command("""
CREATE TABLE IF NOT EXISTS user_logins (
    id UInt64,
    username String,
    event_type String,
    event_time DateTime
) ENGINE = MergeTree()
ORDER BY (id, event_time)
""")

for message in consumer:
    data = message.value
    print("Received:", data)
# Cтоит добавить обработку ошибок - try/except, чтобы обеспечить устойчивость приложения при сбоях подключения или некорректных данных.
    try:
      # Для вставки данных в clickhouse лучше использовать client.insert(). 
      # Запросы через client.command() и f-строки может приводить к ошибкам при наличии кавычек в данных и создаёт риск SQL-инъекций.
      client.insert(
          "user_logins",
          [[data["id"], data["user"], data["event"], data["timestamp"]]],
          column_names=["id", "username", "event_type", "event_time"]
      )
    except Exception as e:
      print("Ошибка вставки:", e)
      time.sleep(1)
      continue
