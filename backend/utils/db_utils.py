import pymysql
from db_main.database import get_connection

def fetch_one_dict(query, params=None):
    """SQL 실행 후 단일 row를 dict 형태로 반환"""
    conn = get_connection()
    cursor = None
    
    try:
        cursor = conn.cursor(pymysql.cursors.DictCursor)  # 🔥 PyMySQL 딕셔너리 커서
        cursor.execute(query, params)
        row = cursor.fetchone()
        return row if row else {}
    finally:
        if cursor:
            cursor.close()
        conn.close()

def fetch_all_dict(query, params=None):
    from db_main.database import get_connection

    conn = get_connection()
    try:
        with conn.cursor() as cursor:
            cursor.execute(query, params)
            rows = cursor.fetchall()
            return rows  # list of dict
    finally:
        conn.close()