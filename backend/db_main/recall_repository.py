from utils.db_utils import fetch_all_dict, fetch_dataframe


# ============================================================
# R001 - 최신 리콜 목록 조회
# ============================================================
def get_recall_list(limit=100):
    """
    최신 리콜 목록 조회
    주요 컬럼만 반환: recall_id, car_name, remedy_method, recall_date
    """
    query = """
        SELECT 
            recall_id,
            car_name,
            remedy_method,
            recall_date
        FROM fact_recall
        ORDER BY recall_date DESC
        LIMIT %s;
    """
    return fetch_dataframe(query, (limit,))

# ============================================================
# R002 - 제조사별 리콜 건수
# ============================================================
def get_recall_count_by_maker(limit=None):
    """
    제조사별 리콜 건수 집계
    """
    query = """
        SELECT maker_name, COUNT(*) AS recall_count
        FROM fact_recall
        GROUP BY maker_name
        ORDER BY recall_count DESC
    """

    if limit:
        query += " LIMIT %s"
        return fetch_dataframe(query, (limit,))

    return fetch_dataframe(query)


# ============================================================
# R003 - 차량명별 리콜 건수
# ============================================================
def get_recall_by_car_name(limit=None):
    """
    차량명별 리콜 건수 집계
    """
    query = """
        SELECT car_name, COUNT(*) AS recall_count
        FROM fact_recall
        GROUP BY car_name
        ORDER BY recall_count DESC
    """

    if limit:
        query += " LIMIT %s"
        return fetch_dataframe(query, (limit,))

    return fetch_dataframe(query)


# ============================================================
# R004 - 월별 리콜 건수
# ============================================================
def get_recall_monthly(limit=None):
    """
    월별 리콜 건수 집계
    """
    query = """
        SELECT DATE_FORMAT(recall_date,'%Y-%m') AS month,
               COUNT(*) AS recall_count
        FROM fact_recall
        GROUP BY month
        ORDER BY month
    """

    if limit:
        query += " LIMIT %s"
        return fetch_dataframe(query, (limit,))

    return fetch_dataframe(query)


# ============================================================
# R005 - 리콜 사유별 통계
# ============================================================
def get_recall_reason_count(limit=None):
    """
    리콜 사유별 발생 건수 집계
    """
    query = """
        SELECT remedy_method, COUNT(*) AS count
        FROM fact_recall
        GROUP BY remedy_method
        ORDER BY count DESC
    """

    if limit:
        query += " LIMIT %s"
        return fetch_dataframe(query, (limit,))

    return fetch_dataframe(query)


# ============================================================
# R006 - 리콜 증가율 계산 (Pandas 활용)
# ============================================================
def calc_recall_growth_rate(df):
    """
    월별 리콜 증가율 계산
    df: get_recall_monthly() 결과 DataFrame
    """
    df['prev'] = df['recall_count'].shift(1)
    df['growth(%)'] = ((df['recall_count'] - df['prev']) / df['prev']) * 100
    df['growth(%)'] = df['growth(%)'].fillna(0)
    return df


# ============================================================
# R007 - TOP N 제조사
# ============================================================
def get_top_makers(df, n=5):
    """
    제조사별 리콜 건수 상위 N개
    """
    return df.sort_values("recall_count", ascending=False).head(n)


# ============================================================
# R008 - TOP N 리콜 사유
# ============================================================
def get_top_recall_reasons(df, n=5):
    """
    가장 많이 발생한 리콜 사유 상위 N개
    """
    return df.sort_values("count", ascending=False).head(n)