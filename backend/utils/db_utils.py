import pymysql
from backend.db_main.database import get_connection,close_connection

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
import pymysql

import pandas as pd


def fetch_one_dict(query, params=None):
    conn = get_connection()
    try:
        with conn.cursor(pymysql.cursors.DictCursor) as cursor:
            cursor.execute(query, params)
            row = cursor.fetchone()
            return row
    finally:
        close_connection(conn)


def fetch_all_dict(query, params=None):
    conn = get_connection()
    try:
        with conn.cursor(pymysql.cursors.DictCursor) as cursor:
            cursor.execute(query, params)
            rows = cursor.fetchall()
            return rows
    finally:
        close_connection(conn)


# -------------------------------
# 새로 추가! DataFrame 반환 함수
# -------------------------------
def fetch_dataframe(query, params=None):
    conn = get_connection()
    try:
        with conn.cursor() as cursor:
            cursor.execute(query, params)
            rows = cursor.fetchall()

            if not rows:
                return pd.DataFrame()

            columns = [col[0] for col in cursor.description]
            return pd.DataFrame(rows, columns=columns)

    finally:
        close_connection(conn)