import pandas as pd
from src.data_loader import load_all_data


def data_cleaner():
    """
    Исследует данные и проводит очистку. Возвращает готовый к работе датафрейм
    """
    df_items, df_orders, df_users = load_all_data()

    orders_users = pd.merge(df_orders, df_users, on="user_id", how="left")
    df = pd.merge(orders_users, df_items, on="item_id", how="left")

    print("=== Статистическое описание ===")
    print("\nОбщая информация:")
    print(df.info())
    print("\nОсновные статистические показатели:")
    print(df.describe().round(2))
    print("\nНаличие пропусков:")
    print(df.isnull().sum())
    print("\nНаличие дубликатов:", df.duplicated().sum())

    # Приведение типов
    df['order_date'] = pd.to_datetime(df['order_date'], errors="coerce")
    df['registration_date'] = pd.to_datetime(df['registration_date'], errors="coerce")
    print("\nТипы данных после приведения:")
    print(df.info())

    return df
