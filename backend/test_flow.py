from db_main.database import get_connection, close_connection
from db_main.flow_repository import get_inheritance_count
conn = get_connection()

try:

   
    res = get_inheritance_count(2025, 10)
    print(res)

finally:
    # 3️⃣ DB / SSH 터널 종료
    close_connection(conn)


