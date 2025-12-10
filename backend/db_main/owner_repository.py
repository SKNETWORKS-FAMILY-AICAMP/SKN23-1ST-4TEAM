from decimal import Decimal
from backend.utils.db_utils import fetch_all_dict

def get_owner_count_by_age(conn, year: int, month: int):
    query = """
        SELECT
            
            ag.age_group,
            SUM(f.stock_count) AS count
        FROM fact_owner_demo_stock f
        JOIN dim_age_group ag
            ON f.age_group_id = ag.age_group_id
        WHERE f.year = %s
          AND f.month = %s
        GROUP BY ag.age_group, ag.sort_order
        ORDER BY ag.sort_order;
    """
    with conn.cursor() as cursor:
        cursor.execute(query, (year, month))
        rows = cursor.fetchall()  # pymysql DictCursor라면 dict list 가 옴

    total = 0
    processed = []
    for r in rows:
        cnt = r.get("count", 0)
        if cnt is None:
            cnt = 0
        elif isinstance(cnt, Decimal):
            cnt = int(cnt)
        else:
            try:
                cnt = int(cnt)
            except Exception:
                cnt = 0
        r["count"] = cnt
        processed.append(r)
        total += cnt

    return {"year": year, "month": month, "items": processed, "total": total}

"""--------------------------------------------------"""



def get_owner_count_by_region(year: int, month: int):
    """
    O004 – 지역별 소유자 분포
    """

    query = """
        SELECT 
            s.sido_name AS region,
            COUNT(*) AS owner_count
        FROM fact_owner_demo_stock f
        JOIN dim_region_sido s
            ON f.sido_id = s.sido_id
        WHERE f.year = %s
          AND f.month = %s
        GROUP BY s.sido_name
        ORDER BY owner_count DESC;
    """

    rows = fetch_all_dict(query, (year, month))

    return [
        {"region": r["region"], "count": int(r["owner_count"])}
        for r in rows
    ]