from backend.db_main.car_repository import get_vehicle_registration_filtered
from backend.utils.db_utils import get_connection, close_connection

conn = get_connection()

try:
    res = get_vehicle_registration_filtered()

    print(res)
finally:
    close_connection(conn)

