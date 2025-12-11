from backend.db_main.recall_repository import get_recall_list
from backend.utils.db_utils import get_connection, close_connection

conn = get_connection()

try:
        result = get_recall_list(origin_type="국내",search_keyword = "기아")
        print(result)

finally:
        close_connection(conn)

