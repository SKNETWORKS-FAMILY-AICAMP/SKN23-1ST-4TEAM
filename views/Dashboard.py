import streamlit as st
import pandas as pd
import numpy as np

def render():
    st.markdown("<h2>2025년 12월 자동차 등록 현황</h2>", unsafe_allow_html=True)
    st.markdown("<p style='color:gray;'>지역별 신규 등록 트렌드와 리콜 정보를 한눈에 확인하세요.</p>", unsafe_allow_html=True)

    ## 1. 상단 요약 카드 (Summary Cards)
    # 3개의 컬럼 생성
    col1, col2, col3 = st.columns(3)

    # 요약 데이터 (더미)
    summary_data = {
        "신규 등록": {"value": "24,567대", "change": "+12.3%"},
        "상속/증여 비중": {"value": "8.2%", "change": "+1.5%"},
        "우리 지역 1위 차종": {"value": "현대 그랜저", "change": "전월 대비 +450대"},
    }

    def create_summary_card(title, data):
        """요약 정보를 표시하는 카드 형태의 마크다운"""
        change_color = "green" if data['change'].startswith('+') else "red"
        
        # 폰트 크기와 아이콘을 이미지와 유사하게 조정
        st.markdown(
            f"""
            <div style="border: 1px solid #ddd; border-radius: 8px; padding: 20px; height: 120px; display: flex; flex-direction: column; justify-content: space-between;">
                <p style="margin: 0; font-size: 1em; color: #666;">{title}</p>
                <p style="margin: 5px 0 0 0; font-weight: bold;">{data['value']}</p>
                <p style="margin: 5px 0 0 0; font-size: 0.9em; color: {change_color};">
                    {"📈" if change_color == "green" else "📉"} {data['change']}
                </p>
            </div>
            """,
            unsafe_allow_html=True
        )

    with col1:
        create_summary_card("이번 달 신규 등록", summary_data["신규 등록"])

    with col2:
        create_summary_card("상속/증여 비중", summary_data["상속/증여 비중"])

    with col3:
        create_summary_card("우리 지역 1위 차종", summary_data["우리 지역 1위 차종"])

    # st.empty()
    
    ## 2. 월별/지역별 등록 차트 (Charts)
    # 2개의 컬럼 생성 (차트용)
    chart_col1, chart_col2 = st.columns(2)

    ### 📈 월별 신규 등록 추이
    with chart_col1:
        st.markdown("<h5 style='margin: 0; padding: 0;'>월별 신규 자동차 등록 추이</h5>", unsafe_allow_html=True)
        
        # 더미 데이터 생성 (pandas 사용)
        months = [f"{i}월" for i in range(1, 13)]
        
        # 전체 등록 (20,000대 근처)
        np.random.seed(42)
        base_registrations = np.random.randint(18000, 24000, size=12)
        # 상속/증여 (300~1000대)
        inheritance_registrations = np.random.randint(300, 1000, size=12)
        
        monthly_df = pd.DataFrame({
            '월': months,
            '전체 등록': base_registrations,
            '상속/증여': inheritance_registrations
        })
        
        # 월별 추이 차트 표시
        # '월' 컬럼을 인덱스로 설정하여 차트 생성
        monthly_df = monthly_df.set_index('월')
        
        # Streamlit line chart 사용
        st.line_chart(monthly_df, height=300)

    ### 📊 지역별 신규 등록 현황
    with chart_col2:
        st.markdown("<h5 style='margin: 0; padding: 0;'>지역별 신규 등록 현황</h5>", unsafe_allow_html=True)
        
        # 더미 데이터 생성 (pandas 사용)
        regions = ['서울', '경기', '인천', '부산', '대구', '광주', '대전', '울산']
        # 등록 대수 (경기 9000 근처, 서울 5000 근처, 나머지는 2000 근처)
        registration_counts = [5100, 9200, 2100, 2300, 1900, 1500, 1300, 800]
        
        regional_df = pd.DataFrame({
            '지역': regions,
            '등록 대수': registration_counts
        })
        
        # Streamlit bar chart 사용 (x축: 지역, y축: 등록 대수)
        st.bar_chart(regional_df.set_index('지역'), height=300)

    ## 3. 상속/증여 등록 특징 (Inheritance/Gift Registration Features)

    st.markdown("<h5 style='margin: 0; padding: 0;'>🧑‍💻 상속/증여 등록 특징</h5>", unsafe_allow_html=True)
    st.markdown("<p style='color:gray;'>지역별 상속/증여 차량 등록이 많은 지역과 연령대 분석.</p>", unsafe_allow_html=True)

    # 3개의 컬럼 생성 (특징 카드용)
    feature_col1, feature_col2, feature_col3 = st.columns(3)

    # 특징 데이터 (더미)
    features = [
        {"region": "서울특별시", "count": "5,234대", "ratio": "9.2%", "age": "45세"},
        {"region": "경기도", "count": "8,921대", "ratio": "7.8%", "age": "42세"},
        {"region": "부산광역시", "count": "2,156대", "ratio": "10.1%", "age": "48세"},
    ]

    def create_feature_box(data, column):
        """상속/증여 특징 정보를 표시하는 박스"""
        with column:
            st.markdown(
                f"""
                <div style="border: 1px solid #eee; border-radius: 8px; padding: 15px; background-color: #f9f9f9;">
                    <p style="margin: 0; font-weight: bold; font-size: 1.1em;">
                        • {data['region']}
                    </p>
                    <ul style="list-style: none; padding: 0; margin-top: 10px;">
                        <li style="margin-bottom: 5px;">등록 대수: <strong>{data['count']}</strong></li>
                        <li style="margin-bottom: 5px;">상속/증여: <strong>{data['ratio']}</strong></li>
                        <li>평균 연령: <strong>{data['age']}</strong></li>
                    </ul>
                </div>
                """,
                unsafe_allow_html=True
            )

    # 각 컬럼에 특징 박스 생성
    create_feature_box(features[0], feature_col1)
    create_feature_box(features[1], feature_col2)
    create_feature_box(features[2], feature_col3)


    
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
