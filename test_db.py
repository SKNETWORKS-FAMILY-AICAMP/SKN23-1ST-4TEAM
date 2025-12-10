from backend.db_main.database import get_connection, close_connection

conn = get_connection()
print("connected:", conn is not None)
close_connection(conn)
