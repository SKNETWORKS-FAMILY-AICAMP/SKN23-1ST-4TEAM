from backend.db_main.car_repository import get_vehicle_flow_summary_by_region
from backend.utils.db_utils import get_connection, close_connection

conn = get_connection()

try:
    res = get_vehicle_flow_summary_by_region(search_input="서울")

    print(res)
finally:
    close_connection(conn)

