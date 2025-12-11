from backend.db_main.car_repository import get_region_total_flow
from backend.utils.db_utils import get_connection, close_connection

conn = get_connection()

try:
    res = get_region_total_flow(search_input="서울")

    print(res)
finally:
    close_connection(conn)

ㄴ