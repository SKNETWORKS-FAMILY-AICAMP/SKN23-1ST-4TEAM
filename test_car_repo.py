from backend.db_main.car_repository import get_total_new_registrations
from backend.utils.db_utils import get_connection, close_connection

conn = get_connection()

try:
    res = get_total_new_registrations(2025,11,2025,10)
    print(res)
finally:
    close_connection(conn)