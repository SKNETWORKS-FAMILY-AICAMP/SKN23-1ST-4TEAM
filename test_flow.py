from backend.db_main.flow_repository import get_region_total_flow
from backend.db_main.database import get_connection, close_connection

conn = get_connection()

try:
    res = get_region_total_flow(2025, 10)
    print(res)
finally:
    close_connection(conn)

    