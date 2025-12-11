from decimal import Decimal
from backend.utils.db_utils import fetch_all_dict
from backend.utils.db_utils import fetch_one_dict

# ============================================================
# O001 - 연령대별 차량 소유자 수
# ============================================================
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



# ============================================================
# O002 성별 소유자 수 집계
# ============================================================


def get_owner_count_by_gender(year: int, month: int):
   

    query = """
        SELECT 
            gender,
            SUM(stock_count) AS count
        FROM fact_owner_demo_stock
        WHERE year = %s
          AND month = %s
        GROUP BY gender
        ORDER BY gender;
    """

    rows = fetch_all_dict(query, (year, month))

    # 숫자 변환
    return [
        {
            "gender": r["gender"],
            "count": int(r["count"])
        }
        for r in rows
    ]

# ============================================================
# O003 상속/증여 분석 
# ============================================================

def get_inheritance_gift_top3_regions():
    """
    O003 - 상속/증여 등록 특징 (TOP3 지역 자동 분석)
    - 최신 연/월 기준
    - 차량 등록량(flow_count)이 가장 큰 상위 3개 지역 자동 선택
    - 각 지역별 상속/증여 등록수, 전달 대비 증감률, 최빈 연령대 반환
    """
    # 1최신 연/월 조회
    latest_query = """
        SELECT year, month
        FROM fact_flow_count
        ORDER BY year DESC, month DESC
        LIMIT 1;
    """
    latest = fetch_one_dict(latest_query)
    if not latest:
        return []

    year = latest['year']
    month = latest['month']

    # 전달 year/month 계산
    prev_year = year if month > 1 else year - 1
    prev_month = month - 1 if month > 1 else 12

    # 전체 지역 중 flow_count TOP 3 지역 찾기
    top3_query = """
        SELECT 
            s.sido_name,
            SUM(f.flow_count) AS total_flow
        FROM fact_flow_count f
        LEFT JOIN dim_region_sido s ON f.sido_id = s.sido_id
        WHERE f.year = %s AND f.month = %s
        GROUP BY s.sido_name
        ORDER BY total_flow DESC
        LIMIT 3;
    """
    top_regions = fetch_all_dict(top3_query, (year, month))

    results = []

    #  TOP3 지역 각각 분석
    for region_row in top_regions:
        sido_name = region_row["sido_name"]

        # 현재월 상속/증여 등록수
        curr_query = """
            SELECT SUM(f.flow_count) AS cnt
            FROM fact_flow_count f
            LEFT JOIN dim_region_sido s ON f.sido_id = s.sido_id
            LEFT JOIN dim_flow_subtype d ON f.subtype_id = d.subtype_id
            WHERE f.year = %s AND f.month = %s
              AND s.sido_name = %s
              AND d.subtype_name IN ('상속', '증여')
        """
        curr = fetch_one_dict(curr_query, (year, month, sido_name))
        curr_count = int(curr["cnt"] or 0)

        # 전달 상속/증여 등록수
        prev_query = """
            SELECT SUM(f.flow_count) AS cnt
            FROM fact_flow_count f
            LEFT JOIN dim_region_sido s ON f.sido_id = s.sido_id
            LEFT JOIN dim_flow_subtype d ON f.subtype_id = d.subtype_id
            WHERE f.year = %s AND f.month = %s
              AND s.sido_name = %s
              AND d.subtype_name IN ('상속', '증여')
        """
        prev = fetch_one_dict(prev_query, (prev_year, prev_month, sido_name))
        prev_count = int(prev["cnt"] or 0)

        # 증감률 계산
        if prev_count == 0:
            rate = 0
        else:
            rate = round((curr_count - prev_count) / prev_count * 100, 1)

        

        # 결과 누적
        results.append({
            "region": sido_name,
            "count": curr_count,
            "rate": rate,
            
        })
    return results


# ============================================================
# O004 지역별 소유자 분포
# ============================================================

def get_owner_count_by_region(year: int, month: int):
    

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