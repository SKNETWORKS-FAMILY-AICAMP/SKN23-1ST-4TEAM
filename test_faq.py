from backend.db_main.faq_repository import get_faq_filtered
from backend.db_main.database import get_connection, close_connection

conn = get_connection()
try:
    rows = get_faq_filtered(brand = "bmw")
    print(rows)

finally:
    close_connection(conn)