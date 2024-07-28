from datetime import date, datetime#, timedelta
import os
import sqlite3

from config import Config


def get_item_id(table, column, name):
    with sqlite3.connect(Config.DATABASE_URI) as conn:
        cursor = conn.cursor()
        cursor.execute(
            f"SELECT * FROM {table} WHERE LOWER ({column}) LIKE LOWER (?)", (name,)
        )
        result = cursor.fetchone()
        return result[0] if result else 1


def get_items(table):
    with sqlite3.connect(Config.DATABASE_URI) as conn:
        cursor = conn.cursor()
        cursor.execute(f"SELECT * FROM {table}")
        return dict(cursor.fetchall())


def normalize_name(fullname: str) -> str:
    return " ".join(filter(None, map(str.strip, fullname.split()))).upper()


def get_file_timestamp(file):
    return date.fromtimestamp(os.path.getmtime(file))


def check_date(data):
    if data and isinstance(data, datetime):
        return data.date() == date.today()# - timedelta(days=1)


def check_birthday(data: datetime):
    return data.date() if check_date(data) else date.today()
