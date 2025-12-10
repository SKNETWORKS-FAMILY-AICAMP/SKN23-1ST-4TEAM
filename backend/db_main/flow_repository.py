#등록 변동
from decimal import Decimal
from backend.utils.db_utils import fetch_one_dict
from backend.utils.db_utils import fetch_all_dict

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



"""-----------------------------------------------------"""
def get_vehicle_flow_summary_by_region(limit=100, offset=0):
    """
    V008 - 지역별 연월 차량 등록 현황 요약
    + 전체 데이터 개수(total_count) 포함
    """

    # 1) LIMIT/OFFSET 데이터 조회
    query = """
        SELECT 
            f.year,
            f.month,
            s.sido_name,
            f.vehicle_kind,
            SUM(f.flow_count) AS total_flow_count
        FROM fact_flow_count f
        LEFT JOIN dim_region_sido s
            ON f.sido_id = s.sido_id
        WHERE f.vehicle_kind NOT IN ('None', '합계', 'nan')
        GROUP BY f.year, f.month, s.sido_name, f.vehicle_kind
        ORDER BY f.year DESC, f.month DESC, s.sido_name, total_flow_count DESC
        LIMIT %s OFFSET %s;
    """

    rows = fetch_all_dict(query, (limit, offset))

    for r in rows:
        r["total_flow_count"] = int(r["total_flow_count"])

    # 2) 전체 row 개수 조회
    count_query = """
        SELECT COUNT(*) AS total
        FROM fact_flow_count f
        LEFT JOIN dim_region_sido s
            ON f.sido_id = s.sido_id
        WHERE f.vehicle_kind NOT IN ('None', '합계', 'nan');
    """

    total = fetch_one_dict(count_query)["total"]

    return {
        "total_count": int(total),   # 전체 데이터 개수
        "rows": rows                 # LIMIT/OFFSET된 데이터
    }