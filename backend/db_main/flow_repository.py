#등록 변동
from decimal import Decimal
from utils.db_utils import fetch_one_dict
from utils.db_utils import fetch_all_dict

def get_flow_count_by_subtype(year, month):
    query = """
        SELECT 
            d.subtype_name AS subtype,
            SUM(f.flow_count) AS count
        FROM fact_flow_count f
        JOIN dim_flow_subtype d 
            ON f.flow_id = d.subtype_id     -- 핵심 조인!!
        WHERE 
            f.year = %s
            AND f.month = %s
        GROUP BY d.subtype_name
        ORDER BY count DESC;
    """

    rows = fetch_all_dict(query, (year, month))

    # Decimal → int 변환
    for row in rows:
        if row["count"] is not None:
            row["count"] = int(row["count"])

    return {
        "year": year,
        "month": month,
        "items": rows
    }
"""-----------------------------------------------------"""


def get_inheritance_gift_count(year: int, month: int, region: str = None):
    """
    지역별 상속/증여 등록 건수 조회
    """
    query = """
        SELECT 
            r.sido_name AS region,
            SUM(f.flow_count) AS count
        FROM fact_flow_count f
        JOIN dim_flow_subtype s ON f.subtype_id = s.subtype_id
        JOIN dim_region_sido r ON f.sido_id = r.sido_id
        WHERE f.year = %s
          AND f.month = %s
          AND s.subtype_name IN ('상속', '증여')
          AND (%s IS NULL OR r.sido_name = %s)
        GROUP BY r.sido_name
        ORDER BY count DESC;
    """

    params = (year, month, region, region)
    rows = fetch_all_dict(query, params)

    # 🔥 Decimal → int 변환
    for row in rows:
        if row["count"] is not None:
            row["count"] = int(row["count"])

    return rows