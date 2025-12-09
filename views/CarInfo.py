import streamlit as st
import pandas as pd

def render():
    st.markdown("<h2>자동차 정보</h2>", unsafe_allow_html=True)
    st.markdown("<p style='color:gray;'>차량 등록 현황 및 리콜 정보를 확인하세요.</p>", unsafe_allow_html=True)
    
    with st.container():
        st.markdown(
            """
            <div style="display: flex; justify-content: space-between; align-items: center;">
                <h5 style="margin: 0; padding: 0;">최근 차량 등록 현황</h5>
                <a href="#" style="text-decoration: none; color: #165DFB ;">전체 보기 →</a>
            </div>
            """,
            unsafe_allow_html=True
        )

        # 데이터 준비 (이미지에 맞게 더미 데이터 생성)
        data = {
            '지역': ['서울특별시', '경기도', '부산광역시', '인천광역시', '대구광역시'],
            '차종': ['현대 그랜저', '기아 K3', '현대 소나타', 'BMW 5시리즈', '기아 스포티지'],
            '등록유형': ['신규', '이전', '상속', '신규', '증여'],
            '날짜': ['2025-12-07', '2025-12-07', '2025-12-06', '2025-12-06', '2025-12-05'],
            '대수': ['145대', '234대', '23대', '67대', '18대']
        }
        df = pd.DataFrame(data)

        # Streamlit 데이터프레임/테이블 표시
        # 이미지와 유사하게 인덱스 없이 깔끔하게 표시
        st.dataframe(df, hide_index=True, use_container_width=True)

    ## 2. 국내/해외 리콜 정보 (Domestic/Foreign Recall Information)

    # 리콜 정보 데이터 (더미)
    domestic_recalls = [
        {'제조사': '현대자동차', '모델': '그랜저 IG', '결함': '에어백 전개 불량', '상태': '완료'},
        {'제조사': '기아자동차', '모델': 'K3 DL3', '결함': '브레이크 오일 누유', '상태': '완료'},
        {'제조사': '쌍용자동차', '모델': '티볼리', '결함': '연료펌프 결함', '상태': '진행'},
        {'제조사': '현대자동차', '모델': '소나타 DN8', '결함': '파워 스티어링 결함', '상태': '진행'},
    ]

    foreign_recalls = [
        {'제조사': 'Tesla', '모델': 'Model Y', '결함': '자율주행 소프트웨어 오류', '상태': '완료'},
        {'제조사': 'BMW', '모델': 'X5', '결함': '냉각수 누수', '상태': '진행'},
        {'제조사': 'Mercedes-Benz', '모델': 'E-Class', '결함': '변속기 결함', '상태': '완료'},
        {'제조사': 'TOYOTA', '모델': 'Camry', '결함': '연료 탱크 균열', '상태': '진행'},
    ]

    # 리콜 카드 생성 함수
    def create_recall_card(manufacturer, model, defect):
        
        st.markdown(
            f"""
            <div style="border: 1px solid #ddd; border-radius: 8px; padding: 15px; margin-bottom: 10px; line-height: 1.5;">
                <p style="margin: 0; font-weight: bold;">{manufacturer}</p>
                <p style="margin: 5px 0 0 0; font-size: 0.9em; color: #555;">{model}</p>
                <p style="margin: 5px 0 0 0; font-size: 0.9em;">{defect}</p>
            </div>
            """,
            unsafe_allow_html=True
        )

    # 2-컬럼 레이아웃 생성
    col_domestic, col_foreign = st.columns(2)

    # 국내 리콜 정보
    with col_domestic:
        st.markdown(
            """
            <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 10px;">
                <h5 style="margin: 0; padding: 0;">⚠️ 국내 리콜</h5>
                <a href="#" style="text-decoration: none; color: #165DFB ;">전체 보기 →</a>
            </div>
            """,
            unsafe_allow_html=True
        )
        for recall in domestic_recalls:
            create_recall_card(recall['제조사'], recall['모델'], recall['결함'])

    # 해외 리콜 정보
    with col_foreign:
        st.markdown(
            """
            <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 10px;">
                <h5 style="margin: 0; padding: 0;">⚠️ 해외 리콜</h5>
                <a href="#" style="text-decoration: none; color: #165DFB ;">전체 보기 →</a>
            </div>
            """,
            unsafe_allow_html=True
        )
        for recall in foreign_recalls:
            create_recall_card(recall['제조사'], recall['모델'], recall['결함'])
