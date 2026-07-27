import pandas as pd
import streamlit as st

@st.cache_data(ttl=3600)  # Кэш будет храниться 1 час
def load_all_data():
    """
    Загружает все три датасета, кэширует их в памяти и возвращает три отдельных DataFrame.
    """
    df_items = pd.read_csv('artifacts_csv/items.csv')
    df_orders = pd.read_csv('artifacts_csv/orders.csv')
    df_users = pd.read_csv('artifacts_csv/users.csv')

    return df_items, df_orders, df_users