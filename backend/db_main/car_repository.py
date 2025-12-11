from decimal import Decimal
from backend.utils.db_utils import fetch_one_dict
from backend.utils.db_utils import fetch_all_dict


# ============================================================
#  V001 - 전국)해당 연월의 신규 등록 합계
# ============================================================

def get_new_vehicle_count(year, month):
    query = """
        SELECT 
            SUM(flow_count) AS new_vehicle_count
        FROM fact_flow_count
        WHERE 
            year = %s
            AND month = %s
            AND flow_type = '신규';
    """

    result = fetch_one_dict(query, (year, month))

    value = result["new_vehicle_count"]

    # 🔥 Decimal → int 변환
    if isinstance(value, Decimal):
        value = int(value)

    return value

# ============================================================
#  V004-지역->전국:차종별 보유수(승용/승합/화물 등)
# ============================================================
 
def get_vehicle_count_by_type(conn, year, month):
    
    # ------------------------------
    # 1) 시도별 차종별 보유수
    # ------------------------------
    query_region = """
        SELECT 
            ds.sido_name,
            fs.vehicle_kind,
            SUM(fs.stock_count) AS stock_count
        FROM fact_vehicle_stock fs
        JOIN dim_region_sido ds ON fs.sido_id = ds.sido_id
        WHERE 
            fs.year = %s 
            AND fs.month = %s
        GROUP BY 
            ds.sido_name, fs.vehicle_kind
        ORDER BY 
            ds.sido_name ASC, fs.vehicle_kind ASC;
    """

    with conn.cursor() as cursor:
        cursor.execute(query_region, (year, month))
        region_rows = cursor.fetchall()

    # Decimal → int 변환
    for row in region_rows:
        row["stock_count"] = int(row["stock_count"])


    # ------------------------------
    # 2) 전국 차량종류별 총합
    # ------------------------------
    query_total = """
        SELECT 
            vehicle_kind,
            SUM(stock_count) AS total_count
        FROM fact_vehicle_stock
        WHERE 
            year = %s 
            AND month = %s
        GROUP BY vehicle_kind;
    """

    with conn.cursor() as cursor:
        cursor.execute(query_total, (year, month))
        total_rows = cursor.fetchall()

    for row in total_rows:
        row["total_count"] = int(row["total_count"])


    # 3) 최종 데이터 구조
    return {
        "year": year,
        "month": month,
        "items": region_rows,   # 시도별 차종별 보유수
        "total": total_rows     # 전국 차종별 총합
    }
# ============================================================
#  D004 - 연간 월별 등록 추이(신규/중고)
# ============================================================
 

def get_monthly_registration_trend(year, flow_type):
    """
    월별 신규/중고 등록 수 조회 
    """

    # flow_type 매핑
    if flow_type == "신규":
        flow_list = ["신규"]
    elif flow_type == "중고":
        flow_list = ["이전", "변경"]    # 말소 제외
    else:
        raise ValueError("flow_type must be '신규' or '중고'")

    # SQL IN (%s,%s)
    placeholders = ",".join(["%s"] * len(flow_list))

    query = f"""
        SELECT 
            month,
            SUM(flow_count) AS count
        FROM fact_flow_count
        WHERE 
            year = %s
            AND flow_type IN ({placeholders})
        GROUP BY month
        ORDER BY month;
    """

    params = [year] + flow_list
    rows = fetch_all_dict(query, params)

    # 결과 정리
    monthly_list = []
    total = 0

    for row in rows:
        count = int(row["count"]) if row["count"] else 0
        monthly_list.append({
            "month": row["month"],
            "count": count
        })
        total += count

    return {
        "year": year,
        "flow_type": flow_type,
        "items": monthly_list,
        "total": total
    }

# ============================================================
#  D005 - 지역별 등록 상위 N개(신규/중고)
# ============================================================
 

def get_region_ranking(year, month, flow_type, top_n=10):

    # flow_type 분리
    if flow_type == "신규":
        flow_filter = ["신규"]
    elif flow_type == "중고":
        flow_filter = ["이전", "변경"]
    else:
        raise ValueError("flow_type must be '신규' or '중고'")
    placeholders = ",".join(["%s"] * len(flow_filter))

    query = f"""
        SELECT 
            r.sido_name,
            SUM(f.flow_count) AS count
        FROM fact_flow_count f
        JOIN dim_region_sido r ON f.sido_id = r.sido_id
        WHERE 
            f.year = %s
            AND f.month = %s
            AND f.flow_type IN ({placeholders})
        GROUP BY r.sido_name
        ORDER BY count DESC
        LIMIT %s;
    """

    params = [year, month] + flow_filter + [top_n]

    rows = fetch_all_dict(query, params)

    # int 변환
    for row in rows:
        row["count"] = int(row["count"])

    return {
        "year": year,
        "month": month,
        "flow_type": flow_type,
        "top_n": top_n,
        "ranking": rows
    }
# ============================================================
#  V005 - 연료별 보유수(전기/휘발유 등)
# ============================================================
 

def get_vehicle_count_by_fuel(year, month):
    query = """
        SELECT 
            f.year,
            f.month,
            d.fuel_name,
            SUM(f.stock_count) AS stock_count
        FROM fact_fuel_stock f
        JOIN dim_fuel d ON f.fuel_id = d.fuel_id
        WHERE f.year = %s
          AND f.month = %s
        GROUP BY f.year, f.month, d.fuel_name
        ORDER BY d.fuel_name;
    """

    rows = fetch_all_dict(query, (year, month))

    # Decimal → int 변환
    for row in rows:
        if row["stock_count"] is not None:
            row["stock_count"] = int(row["stock_count"])

    return {
        "year": year,
        "month": month,
        "items": rows
    }
# ============================================================
#  V006 - 지역별 보유수(지역 검색 가능)
# ============================================================
 
def get_vehicle_count_by_region(year, month, region_name=None):
    
    # 1) region_name 없으면 전체 조회 
    if region_name is None:
        query = """
            SELECT 
                s.sido_name,
                SUM(f.stock_count) AS stock_count
            FROM fact_vehicle_stock f
            JOIN dim_region_sido s ON f.sido_id = s.sido_id
            WHERE f.year = %s
              AND f.month = %s
            GROUP BY s.sido_name
            ORDER BY s.sido_name;
        """
        rows = fetch_all_dict(query, (year, month))

        for row in rows:
            row["stock_count"] = int(row["stock_count"]) if row["stock_count"] else 0

        return {
            "year": year,
            "month": month,
            "items": rows
        }

    # ======================================
    # 2) region_name 있을 때 특정 지역만 조회
    # ======================================
    query = """
        SELECT 
            s.sido_name,
            SUM(f.stock_count) AS stock_count
        FROM fact_vehicle_stock f
        JOIN dim_region_sido s ON f.sido_id = s.sido_id
        WHERE f.year = %s
          AND f.month = %s
          AND LOWER(s.sido_name) = LOWER(%s)
        GROUP BY s.sido_name;
    """

    result = fetch_one_dict(query, (year, month, region_name))

    if not result:
        return None

    result["stock_count"] = int(result["stock_count"]) if result["stock_count"] else 0

    return {
        "year": year,
        "month": month,
        "item": result
    }
# ============================================================
#  D001 - 해당 기간 신규 등록 차량 합계
# ============================================================
 
def get_total_new_registrations(start_year, start_month, end_year, end_month):
    """
    D001 - 기간별 신규 등록 총합 조회
    기간(start_year/start_month) ~ (end_year/end_month)
    """
    query = """
        SELECT 
            SUM(flow_count) AS total_new
        FROM fact_flow_count
        WHERE 
            flow_type = '신규'
            AND (year > %s OR (year = %s AND month >= %s))
            AND (year < %s OR (year = %s AND month <= %s));
    """

    params = (
        start_year, start_year, start_month,
        end_year, end_year, end_month
    )

    result = fetch_one_dict(query, params)
    value = result["total_new"]

    if isinstance(value, Decimal):
        value = int(value)

    return {
        "start": f"{start_year}-{start_month}",
        "end": f"{end_year}-{end_month}",
        "total_new": value
    }

# ============================================================
#  D002 - 해당 기간 중고(이전) 등록 합계
# ============================================================
 
def get_total_used_registrations(start_year, start_month, end_year, end_month):
    """
    D002 - 기간별 중고(이전) 등록 합계 조회
    신규/말소 제외 = 모두 중고
    """
    
    query = """
        SELECT 
            SUM(flow_count) AS total_used
        FROM fact_flow_count
        WHERE 
            flow_type NOT IN ('신규', '말소')
            AND (year > %s OR (year = %s AND month >= %s))
            AND (year < %s OR (year = %s AND month <= %s));
    """

    params = (
        start_year, start_year, start_month,
        end_year, end_year, end_month
    )

    row = fetch_one_dict(query, params)
    value = row["total_used"]

    if value is None:
        value = 0

    if isinstance(value, Decimal):
        value = int(value)

    return {
        "start": f"{start_year}-{start_month}",
        "end": f"{end_year}-{end_month}",
        "total_used": value
    }


# ============================================================
#  V007 - 용도(관용/ 자가용/ 영업용)별 집계
# ============================================================
 
def get_vehicle_count_by_category(year: int, month: int):
    """
    V007 - 용도별 차량 보유대 집계 (관용/자가용/영업용)
    count 값을 int로 변환해서 반환
    """

    query = """
        SELECT 
            usage_type,
            SUM(stock_count) AS count
        FROM fact_vehicle_stock
        WHERE year = %s
          AND month = %s
        GROUP BY usage_type
        ORDER BY count DESC;
    """

    rows = fetch_all_dict(query, (year, month))

    # Decimal → int 변환
    return [
        {
            "usage_type": r["usage_type"],
            "count": int(r["count"]) if r["count"] is not None else 0
        }
        for r in rows
    ]
# ============================================================
# V008 차량 등록 건수 
# ============================================================
def get_region_total_flow(
    search_type=None,      # "지역" 또는 "차종"
    search_value=None,     # 시도명 또는 vehicle_kind
    year=None, 
    month=None,
    search_input=None,     # 자유 검색(지역명/차종명)
    limit=30, 
    offset=0
):
    """
    차량 등록 현황 필터 검색 (자유검색 포함)
    - search_type: "지역" 또는 "차종"
    - search_value: 선택값 (지역명 또는 차량유형)
    - search_input: 입력창에서 검색한 문자열 (지역명 OR 차량유형 부분일치)
    - year: 등록 연도
    - month: 등록 월
    """

    query = """
        SELECT 
            s.sido_name,
            f.vehicle_kind,
            f.flow_type,
            CONCAT(f.year, '-', LPAD(f.month, 2, '0')) AS flow_date,
            SUM(f.flow_count) AS flow_count
        FROM fact_flow_count f
        JOIN dim_region_sido s ON f.sido_id = s.sido_id
        JOIN dim_flow_subtype d ON f.subtype_id = d.subtype_id
        WHERE f.vehicle_kind NOT IN ('None', '합계', 'nan')
    """

    params = []

    # ---------------------------
    # 1) 검색 유형: 지역
    # ---------------------------
    if search_type == "지역" and search_value:
        query += " AND s.sido_name = %s"
        params.append(search_value)

    # ---------------------------
    # 2) 검색 유형: 차종
    # ---------------------------
    if search_type == "차종" and search_value:
        query += " AND f.vehicle_kind = %s"
        params.append(search_value)

    # ---------------------------
    # 3) 자유 검색 (지역명 / 차종 부분검색)
    # ---------------------------
    if search_input:
        query += " AND (s.sido_name LIKE %s OR f.vehicle_kind LIKE %s)"
        params.append(f"%{search_input}%")
        params.append(f"%{search_input}%")

    # ---------------------------
    # 4) 등록 연도
    # ---------------------------
    if year:
        query += " AND f.year = %s"
        params.append(year)

    # ---------------------------
    # 5) 등록 월
    # ---------------------------
    if month:
        query += " AND f.month = %s"
        params.append(month)

    # ---------------------------
    # GROUP BY + 정렬 + 페이징
    # ---------------------------
    query += """
        GROUP BY f.year, f.month, s.sido_name, f.vehicle_kind, f.flow_type
        ORDER BY f.year DESC, f.month DESC
        LIMIT %s OFFSET %s
    """
    params.extend([limit, offset])

    return fetch_all_dict(query, tuple(params))

# ============================================================
#  V011 - 차량 상세 검색
# ============================================================
 
def get_vehicle_stock_search(
    year=None,
    month=None,
    origin_type=None,
    sido_id=None,
    vehicle_kind=None,
    usage_type=None,
    limit=30,
    offset=0
):
    """
    V011 - 차량 보유대 검색
    조건이 하나도 없을 때 → 전체 목록 전부 반환 (딕셔너리 형태)

    """

    # ★ 조건이 하나도 없으면 전체 데이터 반환
    if not any([year, month, origin_type, sido_id, vehicle_kind, usage_type]):
        all_query = """
            SELECT 
                f.year,
                f.month,
                f.origin_type,
                s.sido_name,
                f.vehicle_kind,
                f.usage_type,
                f.stock_count
            FROM fact_vehicle_stock f
            LEFT JOIN dim_region_sido s
                ON f.sido_id = s.sido_id
            ORDER BY f.year DESC, f.month DESC, s.sido_name
        """
        return fetch_all_dict(all_query)   # ← DataFrame 대신 dict 반환

    # ===========================
    # ▼ 조건 검색
    # ===========================

    query = """                                     
        SELECT 
            f.year,
            f.month,
            f.origin_type,
            s.sido_name,
            f.vehicle_kind,
            f.usage_type,
            f.stock_count
        FROM fact_vehicle_stock f
        LEFT JOIN dim_region_sido s
            ON f.sido_id = s.sido_id
        WHERE 1=1
    """

    params = []

    if year:
        query += " AND f.year = %s"
        params.append(year)

    if month:
        query += " AND f.month = %s"
        params.append(month)

    if origin_type:
        query += " AND f.origin_type = %s"
        params.append(origin_type)

    if sido_id:
        query += " AND f.sido_id = %s"
        params.append(sido_id)

    if vehicle_kind:
        query += " AND f.vehicle_kind = %s"
        params.append(vehicle_kind)

    if usage_type:
        query += " AND f.usage_type = %s"
        params.append(usage_type)

    query += " ORDER BY f.year DESC, f.month DESC LIMIT %s OFFSET %s"
    params.extend([limit, offset])

    return fetch_all_dict(query, params)

