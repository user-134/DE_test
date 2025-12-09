import psycopg2
import config
from kafka import KafkaProducer
import json
import time

conn = psycopg2.connect(
    dbname=config.PG_DB,
    user=config.PG_USER,
    password=config.PG_PASS,
    host=config.PG_HOST,
    port=config.PG_PORT,
)

producer = KafkaProducer(
    bootstrap_servers=config.KAFKA_BOOTSTRAP,
    value_serializer=lambda v: json.dumps(v).encode("utf-8")
)

cursor = conn.cursor()

cursor.execute("""
                SELECT id, 
                       username, 
                       event_type, 
                       extract(epoch FROM event_time) 
                FROM user_logins
                WHERE sent_to_kafka = FALSE
                """)

rows = cursor.fetchall()

for row in rows:
    id_ = row[0]

    data = {
        "id": id_,
        "user": row[1],
        "event": row[2],
        "timestamp": float(row[3])  # преобразуем Decimal → float
    }

    producer.send("user_events", value=data)
    print("Sent:", data)

    cursor.execute(
        "UPDATE user_logins SET sent_to_kafka = TRUE WHERE id = %s",
        (id_,)
    )
    conn.commit()

    time.sleep(0.5)
