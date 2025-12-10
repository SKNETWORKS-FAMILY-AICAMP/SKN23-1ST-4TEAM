from db_main.flow_repository import get_inheritance_gift_count
from db_main.database import get_connection, close_connection

conn = get_connection()

try:
    res = get_inheritance_gift_count(2024, 10)
    print(res)
finally:
    close_connection(conn)