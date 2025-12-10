from backend.db_main.car_repository import get_vehicle_stock_search
from backend.utils.db_utils import get_connection, close_connection

conn = get_connection()

try:
    res = get_vehicle_stock_search() # 조건 없음 → 전체 데이터# 일부만 출력
    print(res)                    # 전체 몇 row인지 확인
finally:
    close_connection(conn)