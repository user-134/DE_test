import os
import json
from pymongo import MongoClient

# Подключаемся к MongoDB из нашего Docker-контейнера
client = MongoClient("mongodb://admin:adminpassword@localhost:27017/")

# Создаем БД (или подключаемся к ней, если она уже есть).
db = client["piccha_db"]

base_dir = "data"

# Обходим все папки (будущие коллекции) внутри директории data
for collection_name in os.listdir(base_dir):
    collection_path = os.path.join(base_dir, collection_name)

    # Проверяем, что это действительно папка
    if os.path.isdir(collection_path):

        # Создаем или выбираем коллекцию в базе с таким же именем
        collection = db[collection_name]
        print(f"Загружаем данные в коллекцию: {collection_name}...")

        # Обходим все файлы внутри этой папки
        for filename in os.listdir(collection_path):
            if filename.endswith(".json"):
                file_path = os.path.join(collection_path, filename)

                # Открываем файл на чтение
                with open(file_path, "r", encoding="utf-8") as f:
                    # Превращаем JSON-файл в Python-словарь
                    document = json.load(f)

                    # Вставляем документ в коллекцию MongoDB
                    collection.insert_one(document)

print("Все данные успешно загружены в MongoDB!")
