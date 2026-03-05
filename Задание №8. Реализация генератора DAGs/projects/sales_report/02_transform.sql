-- Очищаем сырые данные
DELETE FROM raw_sales WHERE amount IS NULL;

-- Агрегируем продажи по дням
INSERT INTO mart_sales (sale_date, total_amount)
SELECT sale_date, SUM(amount)
FROM raw_sales
GROUP BY sale_date;
