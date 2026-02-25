"""
ETL Pipeline
Источник: books.toscrape.com
База данных: PostgreSQL
"""

import logging
import time
import requests
import pandas as pd
from bs4 import BeautifulSoup
from sqlalchemy import create_engine

# Настройка логгирования
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

# Конфигурация
CONFIG = {
    "BASE_URL": "https://books.toscrape.com/",
    "HEADERS": {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
        "Accept-Language": "ru-RU,ru;q=0.8,en-US;q=0.5,en;q=0.3",
        "Referer": "https://www.google.com/"
    },
    "DELAY": 2,
    "MAX_RETRIES": 3,
    "TIMEOUT": 10
}

# База данных
DB_URL = "postgresql://ваш_пользователь:ваш_пароль@localhost:5432/my_library"

def get_page(url: str):
    """Отправляет GET-запрос с защитой от сбоев соединения"""
    for attempt in range(CONFIG["MAX_RETRIES"]):
        try:
            response = requests.get(url, headers=CONFIG["HEADERS"], timeout=CONFIG["TIMEOUT"])
            if response.status_code == 200:
                return BeautifulSoup(response.text, "html.parser")
        except Exception as e:
            logging.warning(f"Попытка {attempt + 1} для {url} провалена: {e}")
        time.sleep(CONFIG["DELAY"])
    return None

def parse_books(soup) -> list:
    """Извлекает название, цену, наличие и рейтинг из HTML-кода"""
    books_list = []
    items = soup.find_all("article", class_="product_pod")
    
    for item in items:
        title = item.h3.a["title"]
        price = item.find("p", class_="price_color").text
        stock = item.find("p", class_="instock").text.strip()
        rating = item.find("p", class_="star-rating")["class"][1]
        
        books_list.append({
            "title": title,
            "price": price,
            "stock": stock,
            "rating": rating
        })
    return books_list

def extract_data() -> list:
    """Обходит страницы каталога и собирает сырые данные"""
    all_books = []
    current_page_url = "catalogue/page-1.html"
    
    while current_page_url:
        full_url = CONFIG["BASE_URL"] + current_page_url
        logging.info(f"Парсинг: {full_url}")
        
        soup = get_page(full_url)
        if not soup:
            logging.error("Сайт не ответил. Остановка сбора.")
            break 
            
        all_books.extend(parse_books(soup))
        
        next_button = soup.find("li", class_="next")
        if next_button:
            next_page_link = next_button.a["href"]
            current_page_url = next_page_link if "catalogue/" in next_page_link else "catalogue/" + next_page_link
        else:
            logging.info("Достигнута последняя страница.")
            current_page_url = None 
            
        time.sleep(CONFIG["DELAY"]) 
        
    return all_books


def main():
    """Оркестрация ETL процессов"""
    # Extract
    logging.info("--- СТАРТ: EXTRACT ---")
    raw_data = extract_data()
    
    if not raw_data:
        logging.error("Нет данных для обработки.")
        return

    df = pd.DataFrame(raw_data)

    # Transform
    logging.info("--- СТАРТ: TRANSFORM ---")
    df['price'] = df['price'].str.extract(r'(\d+\.\d+)').astype(float)
    
    rating_map = {"One": 1, "Two": 2, "Three": 3, "Four": 4, "Five": 5}
    df['rating'] = df['rating'].map(rating_map)
    df['stock'] = df['stock'].str.strip()

    # Проверка на целостность
    initial_len = len(df)
    df = df.dropna()
    if len(df) < initial_len:
        logging.warning(f"Удалено {initial_len - len(df)} строк с пустыми значениями.")

    # Сохраняем локальную копию
    df.to_csv("books_cleaned.csv", index=False, encoding="utf-8-sig")
    logging.info(f"Данные очищены. Итоговых записей: {len(df)}")

    # Load
    logging.info("--- СТАРТ: LOAD ---")
    filtered_df = df[df['rating'] >= 4] # Берем только книги с рейтингом 4 и 5
    
    try:
        engine = create_engine(DB_URL)
        filtered_df.to_sql('top_books', engine, if_exists='replace', index=False)
        logging.info("✅ УСПЕШНО: Данные загружены в PostgreSQL!")
    except Exception as e:
        logging.error(f"❌ Ошибка загрузки в БД: {e}")

if __name__ == "__main__":
    main()
