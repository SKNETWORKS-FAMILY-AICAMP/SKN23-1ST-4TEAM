from backend.db_main.flow_repository import get_vehicle_flow_summary_by_region
from backend.db_main.database import get_connection, close_connection

conn = get_connection()

try:
    res = get_vehicle_flow_summary_by_region()
    print(res)
finally:
    close_connection(conn)