# db_main/database.py
import pymysql
from sshtunnel import SSHTunnelForwarder

SSH_HOST = "ec2-13-61-174-247.eu-north-1.compute.amazonaws.com"
SSH_USER = "ec2-user"
SSH_KEY = "/Users/jy/.ssh/SKN.pem"

RDS_HOST = "skn23-1st-4team.cr6u26mg6lbq.eu-north-1.rds.amazonaws.com"
RDS_PORT = 3306
RDS_USER = "admin"
RDS_PASSWORD = "vmfhwprxm"
RDS_DB = "SKN23"

# ---- 전역 싱글톤 ----
_global_conn = None

def get_connection():
    global _global_conn

    # 이미 연결돼 있으면 그대로 사용
    if _global_conn is not None:
        try:
            with _global_conn.cursor() as cursor:
                cursor.execute("SELECT 1;")
            return _global_conn
        except:
            # 연결이 죽었으면 다시 연결 시작
            pass

    # 새 연결 생성
    tunnel = SSHTunnelForwarder(
        (SSH_HOST, 22),
        ssh_username=SSH_USER,
        ssh_pkey=SSH_KEY,
        remote_bind_address=(RDS_HOST, RDS_PORT),
        local_bind_address=("127.0.0.1", 3307)
    )

    tunnel.start()
    print("🔐 SSH Tunnel Opened (NEW)")

    conn = pymysql.connect(
        host="127.0.0.1",
        port=3307,
        user=RDS_USER,
        password=RDS_PASSWORD,
        database=RDS_DB,
        cursorclass=pymysql.cursors.DictCursor,
    )

    conn.tunnel = tunnel
    _global_conn = conn
    return conn


def close_connection(conn):
    """ DB + SSH 터널 종료 """
    try:
        conn.close()
        conn.tunnel.stop()
        print("🔒 SSH Tunnel Closed")
    except:
        pass