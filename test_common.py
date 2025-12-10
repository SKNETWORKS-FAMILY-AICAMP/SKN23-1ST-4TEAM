from backend.db_main.common_repository import get_sido_list
from backend.db_main.database import get_connection, close_connection

conn = get_connection()
try:
    res = get_sido_list()
    print(res)
finally:
    close_connection(conn)