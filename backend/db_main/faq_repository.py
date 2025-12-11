from backend.utils.db_utils import fetch_all_dict

# ============================================================
#  Q001 - 모든 FAQ를 최신 업데이트순으로 조회
# ============================================================

def get_all_faq_latest(limit=30, offset=0):
    """
    전체 FAQ 최신 업데이트순으로 호출
    """
    query = """
        SELECT 
            brand,
            question,
            answer
        FROM faq
        ORDER BY updated_at DESC
        LIMIT %s OFFSET %s;
    """
    return fetch_all_dict(query, (limit, offset))
# ============================================================
#  Q002 - 브랜드, 질문 키워드 단독/조합 검색
# ============================================================

def search_faq_brand_keyword(brand=None, keyword=None):
    """
    브랜드 + 질문 키워드로 FAQ 검색
    - brand 만 검색 가능
    - keyword 만 검색 가능
    - brand + keyword 함께 검색 가능
    - 결과는 brand, question, answer만 딕셔너리로 반환
    """

    query = """
        SELECT brand, question, answer
        FROM faq
        WHERE 1=1
    """

    params = []

    # 브랜드 검색
    if brand:
        query += " AND brand = %s"
        params.append(brand)

    # 질문 키워드 검색
    if keyword:
        query += " AND question LIKE %s"
        params.append(f"%{keyword}%")

    # 최신순 정렬
    query += " ORDER BY updated_at DESC"

    return fetch_all_dict(query, tuple(params))