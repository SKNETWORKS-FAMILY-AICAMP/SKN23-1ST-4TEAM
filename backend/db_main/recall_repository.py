from backend.utils.db_utils import fetch_all_dict


# ============================================================
# R001 - 최신 리콜 목록 조회
# ============================================================
def get_recall_list(limit=100, page_num=0, origin_type=None):
    offset = limit * page_num

    # 국내/해외 매핑 (국내 = 현대+기아)
    domestic_brands = ['기아 주식회사', '현대자동차(주)']

    query = """
        SELECT recall_id, car_name, remedy_method, recall_date, maker_name
        FROM fact_recall
        WHERE 1=1
    """
    params = []

    if origin_type == "국내":
        query += " AND maker_name IN (%s, %s)"
        params.extend(domestic_brands)

    elif origin_type == "해외":
        query += " AND maker_name NOT IN (%s, %s)"
        params.extend(domestic_brands)

    query += " ORDER BY recall_date DESC LIMIT %s OFFSET %s"
    params.extend([limit, offset])

    return fetch_all_dict(query, params)


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
def get_recall_monthly(limit=None,page_num=0):
    offset = limit * page_num
    """
    월별 리콜 건수 집계 (딕셔너리 리스트 반환)
    """
    query = """
        SELECT DATE_FORMAT(recall_date,'%Y-%m') AS month,
               COUNT(*) AS recall_count
        FROM fact_recall
        GROUP BY month
        ORDER BY month
    """

    # limit이 None이 아니면 LIMIT 추가
    if limit is not None:
        query += "LIMIT %s OFFSET %s"
        return fetch_all_dict(query, (limit,offset))

    # limit 미지정 → LIMIT 없음
    return fetch_all_dict(query)


# ============================================================
# R005 - 리콜 사유별 통계
# ============================================================
def get_recall_reason_count(limit=None):
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