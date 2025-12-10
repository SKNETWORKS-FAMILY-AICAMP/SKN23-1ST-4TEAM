from backend.db_main.car_repository import get_region_ranking
from backend.utils.db_utils import get_connection, close_connection

conn = get_connection()

try:
    res = get_region_ranking(2025,10,"중고")

    print(res)
finally:
    close_connection(conn)

