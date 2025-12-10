from backend.db_main.flow_repository import get_inheritance_gift_top3_regions
from backend.db_main.database import get_connection, close_connection

conn = get_connection()

try:
    res = get_inheritance_gift_top3_regions()
    print(res)
finally:
    close_connection(conn)

    