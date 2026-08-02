import streamlit as st
import matplotlib.pyplot as plt
from src.data_cleaner import data_cleaner

df = data_cleaner()
df['total_amount'] = df['quantity'] * df['price_per_unit']

st.set_page_config(
    page_title="Анализ эффективности магазина",
    layout="wide"
)

st.title("Эффективность работы интернет-магазина")
st.subheader("Сырые данные")

# Создание фильтра
with st.sidebar:
    st.header("Фильтры")
    date_options = ["Все даты"] + list(df['order_date'].dt.date.unique())
    selected_date = st.selectbox(
        label="Выберите дату:",
        options=date_options
    )
    category_options = ["Все категории"] + list(df['category'].unique())
    selected_category = st.selectbox(
        label="Выберите категорию:",
        options=category_options
    )

filtered_df = df.copy()
if selected_date != "Все даты":
    filtered_df = filtered_df[filtered_df['order_date'].dt.date == selected_date]
if selected_category != "Все категории":
    filtered_df = filtered_df[filtered_df['category'] == selected_category]

st.write(f"""Дата заказа – **{selected_date}**  
Категория заказа – **{selected_category}**""")

filtered_df.index = filtered_df.index + 1
st.dataframe(
    filtered_df,
    column_config={
        "order_id": "id Заказа",
        "user_id": "id Клиента",
        "order_date": "Дата и время заказа",
        "item_id": "id Товара",
        "quantity": "Количество ед.",
        "price_per_unit": "Цена за ед.",
        "user_name": "Клиент",
        "registration_date": "Дата регистрации",
        "city": "Город",
        "user_segment": "Сегмент клиента",
        "item_name": "Название товара",
        "category": "Категория",
        "supplier": "Поставщик",
        "base_price": "Базовая цена",
        "total_amount": "Сумма заказа"
    }
)

# Блок - ключевые показатели
st.subheader("Ключевые показатели")
col1, col2, col3, col4 = st.columns(4)
with col1:
    count_orders = len(filtered_df['order_id'].unique())
    st.metric(label="Общее количество заказов", value=count_orders)
with col2:
    count_uniq_users = len(filtered_df['user_name'].unique())
    st.metric(label="Уникальных пользователей", value=count_uniq_users)
with col3:
    total_amount = filtered_df['total_amount'].sum()
    st.metric(label="Общая выручка", value=f"{total_amount} ₽")
with col4:
    avg_amount = total_amount / filtered_df['order_id'].count()
    st.metric(label="Средний чек", value=f"{avg_amount:.2f} ₽")

# Блок с графиками
st.subheader("Визуализация")

# Столбчатая диаграмма - ТОП-10 товаров по выручке
top_items = filtered_df.groupby('item_name')['total_amount'].sum().sort_values(ascending=False).reset_index()
top_10 = top_items.head(10)

fig, ax = plt.subplots()
bars = ax.barh(top_10['item_name'], top_10['total_amount'], color="royalblue")
ax.set_title("Топ-10 товаров по выручке")
ax.set_xlabel("Выручка (руб.)")
ax.set_ylabel("Название товара")
ax.bar_label(bars, fmt="{:,.0f} руб.", padding=5, fontsize=8)
st.pyplot(fig)

# Круговая диаграмма - выручка по категориям товаров
category_amount = filtered_df.groupby('category')['total_amount'].sum().reset_index()
category_amount = category_amount.sort_values('total_amount')
fig, ax = plt.subplots()
ax.pie(
    category_amount['total_amount'],
    labels=category_amount['category'],
    autopct="%1.1f%%",
    colors=plt.cm.Paired.colors,
    textprops={"fontsize": 8}
)
ax.set_title("Выручка по категориям товаров", fontsize=9, fontweight="bold")
st.pyplot(fig)

# Зависимость количества заказов от дня недели
filtered_df['day_of_week_num'] = filtered_df['order_date'].dt.weekday
filtered_df['day_of_week_name'] = filtered_df['day_of_week_num'].map(
    {0: "Понедельник",
     1: "Вторник",
     2: "Среда",
     3: "Четверг",
     4: "Пятница",
     5: "Суббота",
     6: "Воскресенье"}
)
df_day_week = (
    filtered_df.groupby(['day_of_week_num', 'day_of_week_name'])['order_id']
    .nunique()
    .reset_index()
    .sort_values('day_of_week_num')
)
fig, ax = plt.subplots(figsize=(6, 3))
bars = ax.bar(df_day_week['day_of_week_name'], df_day_week['order_id'], color="teal")

ax.bar_label(bars, padding=-10, fontsize=6, color="white")
ax.set_title("Заказы по дням недели", fontsize=10, fontweight="bold")
ax.set_xlabel("День недели", fontsize=8)
ax.set_ylabel("Заказов (шт.)", fontsize=8)
ax.tick_params(axis='both', labelsize=6)

plt.xticks(rotation=45)
st.pyplot(fig)

# Блок с аналитическими выводами
# Поиск дат с самой большой и самой маленькой выручкой
daily_amount = (
    df.groupby(df['order_date'].dt.date)['total_amount']
    .sum()
    .reset_index()
    .sort_values('total_amount', ascending=False)
)

# Вычисление количества заказов и выручки по сегментам клиентов
user_segments = (
    df.groupby('user_segment')
    .agg(
        {
            "order_id": "nunique",
            "total_amount": "sum",
        }
    )
    .sort_values('order_id', ascending=False)
    .reset_index()
)

# Вычисление самого популярного товара
item_popularity = df.groupby('item_name')['quantity'].sum().reset_index()
max_quantity = item_popularity['quantity'].max()
top_items = item_popularity[item_popularity['quantity'] == max_quantity]

# Вычисление самого популярного поставщика
supplier_popularity = df.groupby('supplier')['quantity'].sum().reset_index()
max_quantity_supplier = supplier_popularity['quantity'].max()
top_supplier = supplier_popularity[supplier_popularity['quantity'] == max_quantity_supplier]

st.subheader("Аналитические выводы")
st.markdown(f"""
*Выручка* 
1. Самую высоку выручку приносит товар – 
    **«{top_10['item_name'].iloc[0]}»**: **{top_10['total_amount'].iloc[0]}₽**.
2. Основная выручка приходится на категорию **«{category_amount['category'].iloc[-1]}»**. 
    Доля от общей выручки составляет 
    **{(category_amount['total_amount'].iloc[-1] / category_amount['total_amount'].sum()) * 100:.1f}%**.
    В данной категории сделано {len(df[df['category'] == category_amount['category'].iloc[-1]])} заказов. 
    А также средний чек в этой категории выше, чем в остальных.  
3. Самая низкая выручка наблюдается в категории **«{category_amount['category'].iloc[0]}»**. 
    Доля от общей выручки составляет 
    **{(category_amount['total_amount'].iloc[0] / category_amount['total_amount'].sum()) * 100:.1f}%**. 
    Это можно связать с тем, что в данной категории совершено всего 
    {len(df[df['category'] == category_amount['category'].iloc[0]])} заказа. 
    А также цена за единицу товара значительно ниже, чем в категории «{category_amount['category'].iloc[-1]}».
4. Дата, в которую была сделана максимальная выручка – **{daily_amount['order_date'].iloc[0]}**, 
    сумма **{daily_amount['total_amount'].iloc[0]}₽**.
5. Дата, в которую была сделана самая маленькая выручка – **{daily_amount['order_date'].iloc[-1]}**, 
    сумма **{daily_amount['total_amount'].iloc[-1]}₽**.

*Заказы*
1. Наибольшее количество заказов наблюдается с четверга по субботу. 
    **{df_day_week.sort_values('order_id', ascending=False)['day_of_week_name'].iloc[0]}** – 
    пик недели по количеству заказов.
2. Наибольшее число заказов сделано из города **{df['city'].value_counts().reset_index()['city'].iloc[0]}**. 
3. Больше всего товара заказано у поставщика – **{top_supplier['supplier'].iloc[0]}**. 
    Количество **{top_supplier['quantity'].iloc[0]}**.

*Клиенты и товары*
1. Количество заказов и выручка по сегментам клиентов: 
    - сегмент – **{user_segments['user_segment'].iloc[0]}**, 
    количество заказов – **{user_segments['order_id'].iloc[0]}**, 
    выручка – **{user_segments['total_amount'].iloc[0]}**
    - сегмент – **{user_segments['user_segment'].iloc[1]}**, 
    количество заказов – **{user_segments['order_id'].iloc[1]}**, 
    выручка – **{user_segments['total_amount'].iloc[1]}**
    - сегмент – **{user_segments['user_segment'].iloc[2]}**, 
    количество заказов – **{user_segments['order_id'].iloc[2]}**, 
    выручка – **{user_segments['total_amount'].iloc[2]}**
    
    Можно сделать вывод, что выручка не зависит от сегмента клиентов, 
    так как она прямо пропорциональна количеству заказов.
2. Самые популярные товары – **{", ".join(top_items['item_name'].tolist())}**. 
    Количество заказов каждого равняется **{max_quantity}**.
""")
