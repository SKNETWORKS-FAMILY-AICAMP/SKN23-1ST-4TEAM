# FAQ DB 불러오기
def get_all_faq(limit=300):
    query = """
        SELECT *
        FROM fact_faq
        LIMIT %s
    """
    return fetch_dataframe(query, (limit,))
#회사별 FAQ
def get_faq_by_company(company_id):
    query = """
        SELECT f.*
        FROM fact_faq f
        JOIN dim_company c
            ON f.company_id = c.company_id
        WHERE c.company_id = %s
    """
    return fetch_dataframe(query, (company_id,))
#카테고리 별 각회사 FAQ
def get_faq_by_category(category_id):
    query = """
        SELECT f.*
        FROM fact_faq f
        JOIN dim_category cat
            ON f.category_id = cat.category_id
        WHERE cat.category_id = %s
    """
    
    return fetch_dataframe(query, (category_id,))

# 회사 + 카테고리 
def get_faq_company_category(company_id, category_id):
    query = """
        SELECT f.*
        FROM fact_faq f
        WHERE f.company_id = %s
          AND f.category_id = %s
    """
    return fetch_dataframe(query, (company_id, category_id))


#키워드 검색 FAQ
def search_faq(keyword):
    query = """
        SELECT *
        FROM fact_faq
        WHERE question LIKE %s
           OR answer LIKE %s
    """
    like = f"%{keyword}%"
    return fetch_dataframe(query, (like, like))
#회사별 질문 개수 
def count_faq_by_company(df):
    return df.groupby("company_name")["question"].count().reset_index()
#카테고리 분포 
def faq_category_distribution(df):
    return df.groupby("category_name")["question"].count().reset_index()

