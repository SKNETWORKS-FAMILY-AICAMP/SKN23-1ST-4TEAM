from backend.db_main.faq_repository import get_all_faq_latest
from backend.db_main.database import get_connection, close_connection

conn = get_connection()
try:
    rows = get_all_faq_latest(brand = "bmw")
    print(rows)

finally:
    close_connection(conn)