# 리콜목록 조회 
def get_recall_list(limit=100):
    query = """
        SELECT *
        FROM fact_recall
        ORDER BY recall_date DESC
        LIMIT %s
    """
    return fetch_dataframe(query, (limit,))
#제조사별 리콜 건수
def get_recall_count_by_maker():
    query = """
        SELECT maker_name, COUNT(*) AS recall_count
        FROM fact_recall
        GROUP BY maker_name
        ORDER BY recall_count DESC
    """
    return fetch_dataframe(query)


#차량 별 리콜 건수 
def get_recall_by_car_type():
    query = """
        SELECT car_type, COUNT(*) AS recall_count
        FROM fact_recall
        GROUP BY car_type
        ORDER BY recall_count DESC
    """
    return fetch_dataframe(query)

#월별 리콜 수 
def get_recall_monthly():
    query = """
        SELECT DATE_FORMAT(recall_date,'%Y-%m') AS month,
               COUNT(*) AS recall_count
        FROM fact_recall
        GROUP BY month
        ORDER BY month
    """
    return fetch_dataframe(query)
리콜 사유별 통계
def get_recall_reason_count():
    query = """
        SELECT recall_reason, COUNT(*) AS count
        FROM fact_recall
        GROUP BY recall_reason
        ORDER BY count DESC
    """
    return fetch_dataframe(query)

#리콜 증가율 
def recall_growth_rate(df):
    df['prev'] = df['recall_count'].shift(1)
    df['growth(%)'] = (df['recall_count'] - df['prev']) / df['prev'] * 100
    return df

#탑N 제조사 
def top_makers(df, n=5):
    return df.head(n)
# 가장 많은 리콜 사유 
def top_recall_reasons(df, n=5):
    return df.sort_values("count", ascending=False).head(n)

#제조사별 리콜 
df = get_recall_count_by_maker()
st.bar_chart(df, x="maker_name", y="recall_count")