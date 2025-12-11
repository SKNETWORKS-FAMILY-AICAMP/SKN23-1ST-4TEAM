from backend.utils.db_utils import fetch_all_dict

# ============================================================
#  Q001 - 모든 FAQ를 최신 업데이트순으로 조회 (필터 추가 )
# ============================================================
def get_all_faq_latest(limit=30, offset=0,brand=None, keyword=None):
    """
    Q001 + Q002 통합 FAQ 조회
    - 조건 없음 → 최신순 전체 FAQ 조회 (Q001)
    - brand 또는 keyword 조건 있으면 → 필터 조회 (Q002)
    - 최신순 정렬 + limit & offset 지원
    """

    query = """
        SELECT 
            brand,
            question,
            answer
        FROM faq
        WHERE 1=1
    """

    params = []

    # -------------------------------------------------------
    # 브랜드 필터
    # -------------------------------------------------------
    if brand:
        query += " AND brand = %s"
        params.append(brand)

    # -------------------------------------------------------
    # 질문 키워드 필터
    # -------------------------------------------------------
    if keyword:
        query += " AND question LIKE %s"
        params.append(f"%{keyword}%")

    # -------------------------------------------------------
    # 최신순 정렬 + limit, offset 적용
    # -------------------------------------------------------
    query += " ORDER BY updated_at DESC LIMIT %s OFFSET %s"
    params.extend([limit, offset])

    return fetch_all_dict(query, tuple(params))