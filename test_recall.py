from backend.db_main.recall_repository import get_recall_filtered
from backend.utils.db_utils import get_connection, close_connection

conn = get_connection()

try:
        result = get_recall_filtered(brand = "기아")
        print(result)

finally:
        close_connection(conn)

