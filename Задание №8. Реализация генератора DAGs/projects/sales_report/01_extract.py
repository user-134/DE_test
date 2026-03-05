# dag_id: daily_sales_report
# schedule: @daily
# owner: data_analytics_team

import pandas as pd

def extract_data():
    print("Выгружаем данные о продажах из API...")
    # Rод аналитика
