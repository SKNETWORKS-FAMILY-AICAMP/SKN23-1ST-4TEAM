# backend/utils/db_utils.py

import pymysql
from backend.db_main.database import get_connection, close_connection


# -------------------------------------------------------
# fetch ONE (dict)
# -------------------------------------------------------
def fetch_one_dict(query, params=None):
    """
    단일 Row 반환 (Dict 형태)
    """
    conn = get_connection()
    cursor = None

    try:
        cursor = conn.cursor(pymysql.cursors.DictCursor)
        cursor.execute(query, params)
        row = cursor.fetchone()
        return row if row else None

    finally:
        if cursor:
            cursor.close()
        # ❗ 여기서는 connection 닫지 않음 (터널 유지)
        # close_connection(conn)  ← 절대 금지


# -------------------------------------------------------
# fetch ALL (list of dict)
# -------------------------------------------------------
def fetch_all_dict(query, params=None):
    """
    여러 Row 반환 (List of Dict)
    """
    conn = get_connection()
    cursor = None

    try:
        cursor = conn.cursor(pymysql.cursors.DictCursor)
        cursor.execute(query, params)
        rows = cursor.fetchall()
        return rows

    finally:
        if cursor:
            cursor.close()
        # ❗ 여기서 connection 닫으면 → SSH 터널 끊김
        # conn.close() 절대 금지


# -------------------------------------------------------
# fetch as Pandas DataFrame
# -------------------------------------------------------
import pandas as pd

def fetch_dataframe(query, params=None):
    """
    Pandas DataFrame 반환
    """
    conn = get_connection()

    try:
        df = pd.read_sql(query, conn, params=params)
        return df

    finally:
        # ❗ 여기서도 닫으면 안됨
        pass