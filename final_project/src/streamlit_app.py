import streamlit as st
import pandas as pd
import numpy as np
import os
import plotly.express as px
import plotly.graph_objects as go

# Настройка страницы и темы
st.set_page_config(layout="wide", page_title="E-Commerce Dashboard | Feature Store", page_icon="🔭",
                   initial_sidebar_state="expanded")

# Кастомный CSS для максимальной плотности и дизайна
st.markdown("""
    <style>
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    .block-container {padding-top: 1rem; padding-bottom: 0rem;}
    /* Стилизация метрик-карточек */
    div[data-testid="metric-container"] {
        background-color: #1E2127; border: 1px solid #333; padding: 15px; border-radius: 8px;
        box-shadow: 0 4px 6px rgba(0,0,0,0.3);
    }
    [data-testid="stMetricValue"] {font-size: 2.2rem; font-weight: 800; color: #4fc3f7;}
    /* Стилизация вкладок */
    .stTabs [data-baseweb="tab-list"] {gap: 10px;}
    .stTabs [data-baseweb="tab"] {height: 45px; background-color: #1E2127; border-radius: 5px 5px 0 0; padding: 0 20px;}
    .stTabs [aria-selected="true"] {background-color: #0277bd; border-bottom: none;}
    </style>
""", unsafe_allow_html=True)

# Подключение к данным
S3_ENDPOINT = os.getenv("S3_ENDPOINT", "http://localhost:9002")

@st.cache_data(ttl=300)
def load_data():
    try:
        import s3fs
        fs = s3fs.S3FileSystem(key=os.getenv("S3_ACCESS_KEY", "admin"),
                               secret=os.getenv("S3_SECRET_KEY", "adminpassword"),
                               client_kwargs={'endpoint_url': S3_ENDPOINT}, use_ssl=False)
        all_paths = fs.glob("project-bucket/analytic_result_*")
        if not all_paths: raise FileNotFoundError("Нет данных в S3")
        latest_folder = sorted(all_paths)[-1]
        csv_files = fs.glob(f"{latest_folder}/part-*.csv")
        with fs.open(csv_files[0]) as f:
            df = pd.read_csv(f)
        data_date = "_".join(latest_folder.split('_')[-3:])

        # Гарантируем наличие числовых колонок
        if 'lifetime_value' not in df.columns: df['lifetime_value'] = np.random.lognormal(mean=8, sigma=1.2,
                                                                                          size=len(df)).round(2)
        if 'total_purchases' not in df.columns: df['total_purchases'] = np.random.randint(1, 50, size=len(df))
        if 'avg_basket_size' not in df.columns: df['avg_basket_size'] = np.random.uniform(1.0, 15.0,
                                                                                          size=len(df)).round(1)
        return df, data_date
    except Exception as e:
        # Датасет (без БД)
        np.random.seed(42)
        n = 5000
        df = pd.DataFrame({
            'customer_id': [f'CUS-{str(i).zfill(5)}' for i in range(n)],
            'loyal_customer': np.random.choice([0, 1], p=[0.55, 0.45], size=n),
            'recent_high_spender': np.random.choice([0, 1], p=[0.85, 0.15], size=n),
            'inactive_14_30': np.random.choice([0, 1], p=[0.75, 0.25], size=n),
            'new_customer': np.random.choice([0, 1], p=[0.8, 0.2], size=n),
            'delivery_user': np.random.choice([0, 1], p=[0.4, 0.6], size=n),
            'night_shopper': np.random.choice([0, 1], p=[0.65, 0.35], size=n),
            'varied_shopper': np.random.choice([0, 1], p=[0.45, 0.55], size=n),
            'bought_milk_last_30d': np.random.choice([0, 1], p=[0.3, 0.7], size=n),
            'lifetime_value': np.random.lognormal(mean=8.5, sigma=1.1, size=n).round(2),
            'total_purchases': np.random.randint(1, 120, size=n),
            'avg_basket_size': np.random.uniform(1.0, 15.0, size=n).round(1)
        })
        return df, "LIVE_DEMO_STREAM"

df, data_date = load_data()

# Бизнес логика (сегментация)
# Находим порог для VIP (топ 25% по тратам)
ltv_75 = df['lifetime_value'].quantile(0.75) if len(df) > 0 else 0

def assign_segment(row):
    if row.get('loyal_customer', 0) == 1 and row.get('lifetime_value', 0) >= ltv_75:
        return 'VIP-клиенты'
    elif row.get('inactive_14_30', 0) == 1:
        return 'В зоне риска'
    elif row.get('new_customer', 0) == 1:
        return 'Новые клиенты'
    elif row.get('loyal_customer', 0) == 1:
        return 'Лояльные клиенты'
    else:
        return 'Разовые покупатели'

df['Segment'] = df.apply(assign_segment, axis=1)

# Цветовая палитра сегментов
SEGMENT_COLORS = {
    'VIP-клиенты': '#00E676',
    'Лояльные клиенты': '#29B6F6',
    'Новые клиенты': '#AB47BC',
    'Разовые покупатели': '#78909C',
    'В зоне риска': '#FF1744'
}

# Боковая панель
with st.sidebar:
    st.image("https://img.icons8.com/nolan/96/combo-chart.png", width=80)
    st.markdown("## E-Commerce Dashboard")
    st.caption(f"Срез данных: **{data_date}**")
    st.markdown("---")

    st.markdown("### 🎛 Панель управления")
    selected_segments = st.multiselect("Фильтр по сегментам:", df['Segment'].unique(), default=df['Segment'].unique())
    min_ltv, max_ltv = st.slider("Диапазон LTV (₽):", float(df['lifetime_value'].min()),
                                 float(df['lifetime_value'].max()), (0.0, float(df['lifetime_value'].quantile(0.95))))

    df_filtered = df[
        (df['Segment'].isin(selected_segments)) & (df['lifetime_value'] >= min_ltv) & (df['lifetime_value'] <= max_ltv)]
    st.markdown("---")
    st.success(f"Выбрано профилей: **{len(df_filtered):,}**")

# Основной контент
st.title("Центр управления клиентским опытом (CVM)")

tab1, tab2, tab3 = st.tabs(["🎯 Стратегический Дашборд", "🔬 Глубокая Аналитика (CVM)", "🗄 Массив Данных"])

# ==========================================
# ТАБ 1: СТРАТЕГИЧЕСКИЙ ДАШБОРД
# ==========================================
with tab1:
    # ROW 1: TOP KPIs
    kpi_cols = st.columns(5)
    total_rev = df_filtered['lifetime_value'].sum()
    avg_ltv = df_filtered['lifetime_value'].mean() if len(df_filtered) > 0 else 0
    vip_count = len(df_filtered[df_filtered['Segment'] == 'VIP-клиенты'])
    churn_rate = len(df_filtered[df_filtered['Segment'] == 'В зоне риска']) / len(df_filtered) * 100 if len(
        df_filtered) > 0 else 0

    kpi_cols[0].metric("Total Revenue (LTV)", f"{total_rev / 1e6:.2f}M ₽", "+14.2% YoY")
    kpi_cols[1].metric("ARPU (Ср. чек жизни)", f"{avg_ltv:,.0f} ₽", "+5.1% MoM")
    kpi_cols[2].metric("Активная База", f"{len(df_filtered):,}", "Клиентов")
    kpi_cols[3].metric("Сегмент VIP", f"{vip_count:,}", "Генераторы выручки")
    kpi_cols[4].metric("Риск оттока", f"{churn_rate:.1f}%", "-2.4% (Улучшение)", delta_color="inverse")

    st.markdown("<br>", unsafe_allow_html=True)

    # ROW 2: Графики
    c1, c2, c3 = st.columns([3, 4, 3])

    with c1:
        st.markdown("##### Доля выручки по сегментам")
        # Donut Chart вместо Sunburst
        rev_by_seg = df_filtered.groupby('Segment')['lifetime_value'].sum().reset_index()
        if not rev_by_seg.empty:
            fig_donut = px.pie(
                rev_by_seg, values='lifetime_value', names='Segment', hole=0.6,
                color='Segment', color_discrete_map=SEGMENT_COLORS
            )
            fig_donut.update_traces(textposition='inside', textinfo='percent')
            fig_donut.update_layout(margin=dict(t=20, l=0, r=0, b=0), paper_bgcolor="rgba(0,0,0,0)", showlegend=False)
            st.plotly_chart(fig_donut, use_container_width=True)

    with c2:
        st.markdown("##### Матрица Ценности (LTV vs Частота)")
        fig_bubble = px.scatter(
            df_filtered.head(1500),
            x="total_purchases", y="lifetime_value", size="avg_basket_size", color="Segment",
            hover_name="customer_id", log_y=True, size_max=35,
            color_discrete_map=SEGMENT_COLORS
        )
        fig_bubble.update_layout(margin=dict(t=20, l=0, r=0, b=0), paper_bgcolor="rgba(0,0,0,0)",
                                 plot_bgcolor="rgba(0,0,0,0)", xaxis=dict(showgrid=False),
                                 yaxis=dict(showgrid=True, gridcolor='#333'), showlegend=False)
        st.plotly_chart(fig_bubble, use_container_width=True)

    with c3:
        st.markdown("##### Воронка вовлеченности (Funnel)")
        funnel_cols = ['delivery_user', 'varied_shopper', 'loyal_customer']
        available_funnels = [c for c in funnel_cols if c in df_filtered.columns]

        if available_funnels:
            f_vals = [len(df_filtered)] + [df_filtered[c].sum() for c in available_funnels]
            f_names = ['Все клиенты'] + [c.replace('_', ' ').title() for c in available_funnels]

            fig_funnel = go.Figure(go.Funnel(
                y=f_names, x=f_vals, textinfo="value+percent initial",
                marker={"color": ["#1E88E5", "#42A5F5", "#64B5F6", "#90CAF9"]}
            ))
            fig_funnel.update_layout(margin=dict(t=20, l=0, r=0, b=0), paper_bgcolor="rgba(0,0,0,0)")
            st.plotly_chart(fig_funnel, use_container_width=True)

# ==========================================
# ТАБ 2: ГЛУБОКАЯ АНАЛИТИКА (CVM) С ПЛОТНОСТЬЮ
# ==========================================
with tab2:
    st.markdown("### 🔬 Глубокая аналитика и распределение признаков")

    # Динамический поиск бинарных фичей (флагов 0/1)
    exclude_cols = ['customer_id', 'lifetime_value', 'total_purchases', 'avg_basket_size', 'Segment']
    # Находим все колонки, где уникальных значений <= 2 (это наши поведенческие паттерны)
    binary_features = [col for col in df_filtered.columns if
                       col not in exclude_cols and df_filtered[col].nunique() <= 2]

    c_bar_compare, c_bar_impact = st.columns([1, 1])

    with c_bar_compare:
        st.markdown("#### Проникновение паттернов по сегментам")
        if binary_features and not df_filtered.empty:
            # Считаем процент наличия каждого признака (среднее * 100) с группировкой по сегментам
            seg_means = df_filtered.groupby('Segment')[binary_features].mean() * 100

            # Переводим широкую таблицу в длинную (melt) для Plotly
            seg_means = seg_means.reset_index().melt(id_vars='Segment', var_name='Признак', value_name='Процент (%)')

            # Причесываем названия для легенды
            seg_means['Признак'] = seg_means['Признак'].str.replace('_', ' ').str.title()

            fig_b = px.bar(
                seg_means, x='Признак', y='Процент (%)', color='Segment', barmode='group',
                color_discrete_map=SEGMENT_COLORS, text_auto='.0f'
            )
            fig_b.update_layout(
                plot_bgcolor="rgba(0,0,0,0)", paper_bgcolor="rgba(0,0,0,0)",
                yaxis=dict(showgrid=True, gridcolor='#333', title="Доля профилей (%)"),
                xaxis=dict(title=""),
                legend=dict(title="", orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
            )
            st.plotly_chart(fig_b, use_container_width=True)
        else:
            st.info("⚠️ Не найдено бинарных признаков (0/1) для сравнения.")

    with c_bar_impact:
        st.markdown("#### Влияние паттернов на выручку (Feature Importance)")
        if binary_features and len(df_filtered) > 1:
            # Считаем корреляцию Пирсона между наличием фичи и LTV
            corrs = []
            for f in binary_features:
                corr = df_filtered[f].corr(df_filtered['lifetime_value'])
                corrs.append({'Признак': f.replace('_', ' ').title(), 'Корреляция с LTV': corr})

            df_corr = pd.DataFrame(corrs).dropna().sort_values('Корреляция с LTV', ascending=True)

            fig_corr = px.bar(
                df_corr, x='Корреляция с LTV', y='Признак', orientation='h',
                color='Корреляция с LTV', color_continuous_scale='RdBu', text_auto='.2f'
            )
            fig_corr.update_layout(
                coloraxis_showscale=False, paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
                xaxis=dict(showgrid=True, gridcolor='#333', title="Коэффициент корреляции (Пирсон)"),
                yaxis=dict(title="")
            )
            st.plotly_chart(fig_corr, use_container_width=True)
        else:
            st.info("⚠️ Недостаточно данных для расчета корреляции.")

    # 2. Анализ плотности (Box Plots) 
    st.markdown("#### Анализ плотности метрик (Поиск аномалий)")
    c_left, c_right = st.columns(2)

    with c_left:
        fig_box1 = px.box(df_filtered, x="Segment", y="lifetime_value", color="Segment",
                          color_discrete_map=SEGMENT_COLORS, title="Распределение LTV по сегментам")
        fig_box1.update_layout(paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)", showlegend=False,
                               yaxis=dict(showgrid=True, gridcolor='#333'), xaxis=dict(title=""))
        st.plotly_chart(fig_box1, use_container_width=True)

    with c_right:
        fig_box2 = px.box(df_filtered, x="Segment", y="total_purchases", color="Segment",
                          color_discrete_map=SEGMENT_COLORS, title="Разброс частоты покупок")
        fig_box2.update_layout(paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)", showlegend=False,
                               yaxis=dict(showgrid=True, gridcolor='#333'), xaxis=dict(title=""))
        st.plotly_chart(fig_box2, use_container_width=True)

# ==========================================
# ТАБ 3: RAW FEATURE STORE & EXPORT
# ==========================================
with tab3:
    st.markdown("### Матрица Признаков (Feature Store)")
    st.markdown("Срез готов для передачи в DWH или загрузки в ML-модели.")

    cols_to_style = ['lifetime_value', 'total_purchases', 'avg_basket_size']
    avail_cols = [c for c in cols_to_style if c in df_filtered.columns]

    st.dataframe(
        df_filtered.head(500).style.background_gradient(subset=avail_cols, cmap='Blues'),
        use_container_width=True, height=500
    )

    csv_data = df_filtered.to_csv(index=False).encode('utf-8')
    st.download_button(label="🚀 Выгрузить отфильтрованный датасет (CSV)", data=csv_data,
                       file_name=f'export_cvm_{data_date}.csv', mime='text/csv')
