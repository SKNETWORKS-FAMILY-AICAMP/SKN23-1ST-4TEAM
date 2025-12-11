from backend.utils.db_utils import fetch_all_dict


# ============================================================
# R001 - 최신 리콜 목록 조회
# ============================================================
def get_recall_filtered(brand=None, prod_year=None, reg_year=None, reg_month=None,
                        limit=30, offset=0):
    """
    통합 리콜 조회 필터
    - brand: 제조사 부분일치 검색 (예: "현대", "기아", "벤츠", "BMW")
    - prod_year: 생산년도 필터 (prod_start_date ~ prod_end_date 범위 포함)
    - reg_year: 리콜 발표 연도
    - reg_month: 리콜 발표 월
    - limit / offset: 페이징 처리
    """

    query = """
        SELECT 
            maker_name,
            car_name,
            target_count,
            remedy_method,
            recall_date
        FROM fact_recall
        WHERE 1=1
    """

    params = []

    # -------------------------------------------------
    # 브랜드 검색 (부분일치)
    # -------------------------------------------------
    if brand:
        query += " AND maker_name LIKE %s"
        params.append(f"%{brand}%")

    # -------------------------------------------------
    # 생산년도 필터 (포함 범위)
    # prod_start_date <= prod_year <= prod_end_date
    # -------------------------------------------------
    if prod_year:
        query += """
            AND YEAR(prod_start_date) <= %s
            AND YEAR(prod_end_date) >= %s
        """
        params.append(prod_year)
        params.append(prod_year)

    # -------------------------------------------------
    # 리콜 발표 연도
    # -------------------------------------------------
    if reg_year:
        query += " AND YEAR(recall_date) = %s"
        params.append(reg_year)

    # -------------------------------------------------
    # 리콜 발표 월
    # -------------------------------------------------
    if reg_month:
        query += " AND MONTH(recall_date) = %s"
        params.append(reg_month)

    # -------------------------------------------------
    # 최신순 정렬 + 페이징
    # -------------------------------------------------
    query += " ORDER BY recall_date DESC LIMIT %s OFFSET %s"
    params.extend([limit, offset])

    return fetch_all_dict(query, tuple(params))


# ============================================================
# R002 - 제조사별 리콜 건수
# ============================================================
def get_recall_count_by_maker(limit=None):
    """
    제조사별 리콜 건수 집계 (딕셔너리 리스트)
    """
    query = """
        SELECT maker_name, COUNT(*) AS recall_count
        FROM fact_recall
        GROUP BY maker_name
        ORDER BY recall_count DESC
    """

    if limit is not None:
        query += " LIMIT %s"
        return fetch_all_dict(query, (limit,))

    return fetch_all_dict(query)


# ============================================================
# R003 - 차량명별 리콜 건수
# ============================================================
def get_recall_by_car_name(limit=None):
    """
    차량명별 리콜 건수 집계 (딕셔너리 리스트 반환)
    """
    query = """
        SELECT car_name, COUNT(*) AS recall_count
        FROM fact_recall
        GROUP BY car_name
        ORDER BY recall_count DESC
    """

    params = ()
    if limit:
        query += " LIMIT %s"
        params = (limit,)

    return fetch_all_dict(query, params)


# ============================================================
# R004 - 월별 리콜 건수
# ============================================================
def get_recall_monthly(limit=None, offset=0):
    query = """
        SELECT 
            CONCAT(YEAR(recall_date), '-', LPAD(MONTH(recall_date),2,'0')) AS month,
            COUNT(*) AS recall_count
        FROM fact_recall
        GROUP BY month
        ORDER BY month
    """

    params = ()
    if limit is not None:
        query += " LIMIT %s OFFSET %s"
        params = (limit, offset)

    return fetch_all_dict(query, params)


# ============================================================
# R005 - 리콜 사유별 통계
# ============================================================
def get_recall_reason_count(limit=30):
    """
    리콜 사유별 발생 건수 집계 (딕셔너리 리스트 반환)
    """
    query = """
        SELECT remedy_method, COUNT(*) AS count
        FROM fact_recall
        GROUP BY remedy_method
        ORDER BY count DESC
    """

    params = ()
    if limit:
        query += " LIMIT %s"
        params = (limit,)

    return fetch_all_dict(query, params)


# ============================================================
# R006 - 리콜 증가율 계산 (딕셔너리 기반 처리)
# ============================================================
def calc_recall_growth_rate(rows):
    """
    월별 리콜 증가율 계산 (딕셔너리 리스트 기반)
    rows: get_recall_monthly() 결과 (list of dict)
    """
    result = []
    
    prev = None
    for row in rows:
        current = row['recall_count']

        if prev is None:
            growth = 0
        else:
            growth = ((current - prev) / prev * 100) if prev != 0 else 0

        new_row = row.copy()
        new_row['growth_percent'] = round(growth, 2)

        result.append(new_row)
        prev = current

    return result


# ============================================================
# R007 - TOP N 제조사
# ============================================================
def get_top_makers(rows, n=5):
    """
    제조사별 리콜 건수 Top N (딕셔너리 리스트 반환)
    """
    return sorted(rows, key=lambda x: x['recall_count'], reverse=True)[:n]


# ============================================================
# R008 - TOP N 리콜 사유
# ============================================================
def get_top_recall_reasons(rows, n=5):
    """
    리콜 사유별 발생 Top N (딕셔너리 리스트 반환)
    """
    return sorted(rows, key=lambda x: x['count'], reverse=True)[:n]




# ============================================================
# R009 - 리콜 필터 (국내)
# ============================================================
def filter_domestic_recalls(brand=None, prod_year=None, reg_year=None, reg_month=None):
    """
    국내 리콜 필터 검색 (현대/기아만 조회 가능)
    - brand: '현대', '기아' 만 허용
    """

    # --------------------------
    # 1) 브랜드 유효성 검사
    # --------------------------
    allowed_brands = ["현대", "기아"]

    if not brand:
        return []  # 브랜드 미입력 → 조회 불가

    # 입력한 브랜드가 allowed 에 없다면 무조건 빈 결과
    if brand not in allowed_brands:
        return []

    # --------------------------
    # 2) 기본 쿼리
    # --------------------------
    query = """
        SELECT 
            maker_name,
            car_name,
            target_count,
            remedy_method,
            recall_date
        FROM fact_recall
        WHERE 1=1
    """

    params = []

    # --------------------------
    # 3) 브랜드 필터 (LIKE)
    # --------------------------
    # maker_name 은 "현대자동차(주)" "기아 주식회사" 등이라 부분일치 필요
    query += " AND maker_name LIKE %s"
    params.append(f"%{brand}%")

    # --------------------------
    # 4) 생산년도 필터
    # --------------------------
    if prod_year:
        query += """
            AND YEAR(prod_start_date) <= %s
            AND YEAR(prod_end_date) >= %s
        """
        params.append(prod_year)
        params.append(prod_year)

    # --------------------------
    # 5) 리콜 연도
    # --------------------------
    if reg_year:
        query += " AND YEAR(recall_date) = %s"
        params.append(reg_year)

    # --------------------------
    # 6) 리콜 월
    # --------------------------
    if reg_month:
        query += " AND MONTH(recall_date) = %s"
        params.append(reg_month)

    # --------------------------
    # 7) 최신순
    # --------------------------
    query += " ORDER BY recall_date DESC"

    return fetch_all_dict(query, tuple(params))

# ============================================================
# R010 - 리콜 필터 (해외)
# ============================================================
def filter_foreign_recalls(prod_year=None, reg_year=None, reg_month=None):
    """
    해외 브랜드 리콜 필터 (현대/기아 제외)
    """

    domestic_brands = [
        "현대자동차(주)",
        "기아 주식회사"
    ]

    query = """
        SELECT 
            maker_name,
            car_name,
            target_count,
            remedy_method,
            recall_date
        FROM fact_recall
        WHERE maker_name NOT IN (%s, %s)
    """

    params = domestic_brands[:]  # 현대, 기아 제외 조건

    # 생산년도 필터
    if prod_year:
        query += """
            AND YEAR(prod_start_date) <= %s
            AND YEAR(prod_end_date) >= %s
        """
        params += [prod_year, prod_year]

    # 리콜 년도
    if reg_year:
        query += " AND YEAR(recall_date) = %s"
        params.append(reg_year)

    # 리콜 월
    if reg_month:
        query += " AND MONTH(recall_date) = %s"
        params.append(reg_month)

    query += " ORDER BY recall_date DESC"

    return fetch_all_dict(query, tuple(params))


# ============================================================
# R010 - 리콜 필터 (해외)
# ============================================================

def filter_all_recalls(brand=None, prod_year=None, reg_year=None, reg_month=None,
                       limit=30, offset=0):
    """
    전체 리콜 필터 (국내 + 해외)
    - brand: 제조사 검색 (부분일치)
    - prod_year: 생산년도 필터 (prod_start_date ~ prod_end_date 사이)
    - reg_year: 리콜 발표 연도
    - reg_month: 리콜 발표 월
    - limit / offset: 페이징
    """

    query = """
        SELECT 
            maker_name,
            car_name,
            target_count,
            remedy_method,
            recall_date
        FROM fact_recall
        WHERE 1=1
    """

    params = []

    # -------------------------------------------------------
    # 제조사명 (부분일치)
    # -------------------------------------------------------
    if brand:
        query += " AND maker_name LIKE %s"
        params.append(f"%{brand}%")

    # -------------------------------------------------------
    # 생산년도 필터
    # -------------------------------------------------------
    if prod_year:
        query += """
            AND YEAR(prod_start_date) <= %s
            AND YEAR(prod_end_date) >= %s
        """
        params.extend([prod_year, prod_year])

    # -------------------------------------------------------
    # 리콜 발표 연도 필터
    # -------------------------------------------------------
    if reg_year:
        query += " AND YEAR(recall_date) = %s"
        params.append(reg_year)

    # -------------------------------------------------------
    # 리콜 발표 월 필터
    # -------------------------------------------------------
    if reg_month:
        query += " AND MONTH(recall_date) = %s"
        params.append(reg_month)

    # -------------------------------------------------------
    # 최신순 정렬 + 페이징 적용
    # -------------------------------------------------------
    query += " ORDER BY recall_date DESC LIMIT %s OFFSET %s"
    params.extend([limit, offset])

    return fetch_all_dict(query, tuple(params))