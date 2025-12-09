from decimal import Decimal
from utils.db_utils import fetch_one_dict
from utils.db_utils import fetch_all_dict

"""---------------------------------------------------"""
#해당 연월의 신규 등록 합계
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
"""---------------------------------------------------"""
#차종별 보유수 
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
"""-----------------------------------"""

def get_monthly_registration_trend(conn, year, flow_type):
    # flow_type -> DB flow_type 매핑
    if flow_type == "신규":
        flow_list = ["신규"]
    elif flow_type == "중고":
        flow_list = ["이전", "변경"]  # 말소(X)
    else:
        raise ValueError("flow_type must be '신규' or '중고'")

    # SQL IN (%s, %s…) 만들기
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

    with conn.cursor() as cursor:
        cursor.execute(query, params)
        rows = cursor.fetchall()

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

"""-------------------------------------------------"""

def get_region_ranking(conn, year, month, flow_type, top_n=10):
    """
    지역별 신규/중고 등록 수 TOP N 조회
    """

    # flow_type 분리
    if flow_type == "신규":
        flow_filter = ["신규"]
    elif flow_type == "중고":
        flow_filter = ["이전", "변경"]
    else:
        raise ValueError("flow_type must be '신규' or '중고'")

    # (%s,%s) 자동 생성
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

    with conn.cursor() as cursor:
        cursor.execute(query, params)
        rows = cursor.fetchall()

    # 결과 변환
    ranking = [
        {"sido_name": row["sido_name"], "count": int(row["count"])}
        for row in rows
    ]

    return {
        "year": year,
        "month": month,
        "flow_type": flow_type,
        "top_n": top_n,
        "ranking": ranking
    }
"""----------------------------------"""
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
"""---------------------------------------"""
def get_vehicle_count_by_region(year, month, region_name=None):
    
    # ======================================
    # 1) region_name 없으면 전체 조회
    # ======================================
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

"""---------------------------------------"""

def get_vehicle_list(search_type, flow_type, year, month, vehicle=None, region=None):
    query = """
        SELECT
            s.sido_name AS region,
            v.vehicle_kind,
            f.flow_type,
            f.year,
            f.month,
            f.flow_count AS count
        FROM fact_flow_count f
        JOIN dim_region_sido s ON f.sido_id = s.sido_id
        JOIN dim_vehicle_kind v ON f.vehicle_kind_id = v.vehicle_kind_id
        WHERE f.year = %s
          AND f.month = %s
          AND f.flow_type = %s
    """
    
    params = [year, month, flow_type]

    # 🔹 차량 종류 필터
    if vehicle:
        if isinstance(vehicle, list):
            query += " AND v.vehicle_kind IN (" + ",".join(["%s"] * len(vehicle)) + ")"
            params.extend(vehicle)
        else:
            query += " AND v.vehicle_kind = %s"
            params.append(vehicle)

    # 🔹 지역 필터
    if region:
        if isinstance(region, list):
            query += " AND s.sido_name IN (" + ",".join(["%s"] * len(region)) + ")"
            params.extend(region)
        else:
            query += " AND s.sido_name = %s"
            params.append(region)

    # 🔹 목록 타입 결정
    if search_type == "region":
        query += " ORDER BY s.sido_name, v.vehicle_kind"
    elif search_type == "vehicle_kind":
        query += " ORDER BY v.vehicle_kind, s.sido_name"
    else:
        raise ValueError("search_type must be 'region' or 'vehicle_kind'")

    rows = fetch_all_dict(query, params)

    # 숫자 변환
    for row in rows:
        row["count"] = int(row["count"])

    return {
        "year": year,
        "month": month,
        "search_type": search_type,
        "items": rows
    }


"""---------------------------------------"""