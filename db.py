# db.py
import pymysql

# Конфигурация подключения
DB_CONFIG = {
    'host': 'localhost',
    'port': 3306,
    'user': 'root',
    'password': 'Mrgruzh24680mrgruzh',
    'database': 'mydb',
    'charset': 'utf8mb4',
    'autocommit': True
}

connection = None


def init_db_connection():
    global connection
    try:
        connection = pymysql.connect(**DB_CONFIG)
        print("Подключение к базе данных успешно.")
        return True
    except pymysql.MySQLError as e:
        print(f"Ошибка подключения к базе данных: {e}")
        return False


def get_connection():
    global connection
    if not connection or not connection.open:
        init_db_connection()
    return connection


def execute_query(query, params=None):
    conn = get_connection()
    with conn.cursor() as cursor:
        cursor.execute(query, params)
        return cursor.fetchall()


def execute_non_query(query, params=None):
    conn = get_connection()
    with conn.cursor() as cursor:
        cursor.execute(query, params)
    conn.commit()


def execute_insert(query, params=None):
    conn = get_connection()
    with conn.cursor() as cursor:
        cursor.execute(query, params)
        conn.commit()
        return cursor.lastrowid

