from db_main.database import get_connection, close_connection
from db_main.car_repository import get_vehicle_list
conn = get_connection()

try:

    res = get_vehicle_list("region", "신규", 2025, 10)
    print(res)

finally:
    # 3️⃣ DB / SSH 터널 종료
    close_connection(conn)

