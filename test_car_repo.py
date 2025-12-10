from backend.db_main.car_repository import get_vehicle_count_by_category
from backend.utils.db_utils import get_connection, close_connection

conn = get_connection()

try:
    res = get_vehicle_count_by_category(2025, 10)
    for r in res:
        print(r)
finally:
    close_connection(conn)