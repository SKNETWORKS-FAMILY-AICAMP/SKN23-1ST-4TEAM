from backend.db_main.car_repository import get_monthly_registration_trend
from backend.utils.db_utils import get_connection, close_connection

conn = get_connection()

try:
    res = get_monthly_registration_trend(conn,2025,"중고")

    print(res)
finally:
    close_connection(conn)