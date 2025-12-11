from backend.db_main.recall_repository import filter_domestic_recalls
from backend.utils.db_utils import get_connection, close_connection

def test_filter_domestic_recalls():
    conn = get_connection()

    try:
        result = filter_domestic_recalls(brand="기아")
        print(result)

    finally:
        close_connection(conn)

test_filter_domestic_recalls()