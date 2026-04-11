import json
import hashlib
import re
import time
from pymongo import MongoClient
from kafka import KafkaProducer

# функция маскировки
def anonymize_data(record):
    # Убираем системное поле _id, которое MongoDB добавляет автоматически
    # т.к. Kafka оно не нужно и может вызвать ошибку сериализации
    if "_id" in record:
        del record["_id"]

    # Если есть ключ "customer" (как в чеках) — смотрим внутрь него. Иначе берем сам документ.
    target = record["customer"] if "customer" in record else record

    if target.get("phone"):
        clean_phone = re.sub(r'\D', '', target["phone"])
        target["phone"] = hashlib.sha256(clean_phone.encode("utf-8")).hexdigest()

    if target.get("email"):
        clean_email = target["email"].strip().lower()
        target["email"] = hashlib.sha256(clean_email.encode("utf-8")).hexdigest()

    return record

# Подключаемся к MongoDB
client = MongoClient("mongodb://admin:adminpassword@localhost:27017/")
db = client["piccha_db"]

# Настраиваем Kafka Producer
producer = KafkaProducer(
    bootstrap_servers=["localhost:9092"],
    # Учим продюсера автоматически делать Dict -> JSON -> Bytes
    value_serializer=lambda v: json.dumps(v, ensure_ascii=False).encode("utf-8"),
)

# Список коллекций, которые нам нужно перенести
collections_to_send = ["stores", "products", "customers", "purchases"]

print("Начинаем отправку данных в Kafka...")

for name in collections_to_send:
    print(f"В MongoDB в коллекции {name} лежит {db[name].count_documents({})} документов")

    print(f"Отправляем данные из коллекции {name} в топик {name}...")
    for document in db[name].find({}):
        anonymize_data(document)
        # Отправляем и ЖДЕМ подтверждения от брокера (до 10 секунд)
        future = producer.send(name, value=document)
        future.get(timeout=10)

# Ждем, пока все сообщения из внутренней очереди уйдут в брокер
producer.flush()
print("Все обезличенные данные успешно отправлены в Kafka!")
