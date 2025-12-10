from backend.db_main.faq_repository import search_faq_brand_keyword
from backend.db_main.database import get_connection, close_connection

conn = get_connection()
try:
    rows = search_faq_brand_keyword()
    print(rows)

finally:
    close_connection(conn)