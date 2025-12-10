import streamlit as st
import pandas as pd
import numpy as np

from backend.db_main.recall_repository import get_recall_list, get_recall_monthly
from backend.db_main.car_repository import get_total_new_registrations

# 증감 비율 구하기
def calculate_growth_rate(sub_month, month):
    # 0으로 나누는 오류 방지 (Division by Zero Error)
    if sub_month == 0:
        if month > 0:
            return 10000.0
        elif month < 0:
            return -10000.0
        else:
            # 두 값이 모두 0일 경우
            return 0.0

    growth_rate = ((month - sub_month) / sub_month) * 100
    
    return growth_rate

def get_regist_monthly():
    year = 2025
    month = 10

    sub = get_total_new_registrations(year, (month-1), year, (month-1))
    this = get_total_new_registrations(year, month, year, month)
    rate = calculate_growth_rate(sub['total_new'], this['total_new'])

    return [sub['total_new'], this['total_new'], rate]

# 이번달 등록 수
regist_result = get_regist_monthly()

# 이번달 리콜 수
recall_result = get_recall_monthly()

recall_data = []
for i in recall_result:
    if i['month'] == '2025-09':
        recall_data.append(i['recall_count'])
    elif i['month'] == '2025-10':
        recall_data.append(i['recall_count'])

rate = calculate_growth_rate(recall_data[0], recall_data[1])
recall_data.append(rate)

# 리콜 목록 조회
k_recall_result = get_recall_list(5, 1, '국내')
o_recall_result = get_recall_list(5, 1, '해외')

def render():
    st.markdown("<h2>2025년 12월 자동차 등록 현황</h2>", unsafe_allow_html=True)
    st.markdown("<p style='color:gray;'>지역별 신규 등록 트렌드와 리콜 정보를 한눈에 확인하세요.</p>", unsafe_allow_html=True)

    ## 1. 상단 요약 카드 (Summary Cards)
    col1, col2, _ = st.columns(3)

    def create_summary_card(title, data):
        change_color = "green" if data[2] > 0 else "red"
        
        st.markdown(
            f"""
            <div style="border: 1px solid #ddd; border-radius: 8px; padding: 20px; height: 120px; display: flex; flex-direction: column; justify-content: space-between;">
                <p style="margin: 0; font-size: 1em; color: #666;">{title}</p>
                <p style="margin: 5px 0 0 0; font-weight: bold;">{format(data[1], ',')}</p>
                <p style="margin: 5px 0 0 0; font-size: 0.9em; color: {change_color};">
                    {"📈 +" if change_color == "green" else "📉 -"} {round(data[2], 2)}%
                </p>
            </div>
            """,
            unsafe_allow_html=True
        )

    with col1:
        create_summary_card("이번 달 신규 등록", regist_result)

    with col2:
        create_summary_card("이번 달 리콜 수", recall_data)

    # with col3:
    #     create_summary_card("우리 지역 1위 차종", summary_data["우리 지역 1위 차종"])

    ## 2. 월별/지역별 등록 차트 (Charts)
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
    st.markdown("<p style='color:gray;'>지역별 상속/증여 차량 등록이 많은 지역과 연령대 분석</p>", unsafe_allow_html=True)

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
                        {data['region']}
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

    ## 3. 국내/해외 리콜 정보 (Domestic/Foreign Recall Information)
    def create_recall_card(row):
        st.markdown(
            f"""
            <div style="border: 1px solid #ddd; border-radius: 8px; padding: 15px; margin-bottom: 10px; line-height: 1.5;">
                <div>
                    <b style="margin: 0;">{row['maker_name']}</b>
                    <span style="float: right; margin-right: 6px;">시행일자: {row['fix_start_date']}</span>
                </div>
                <p style="margin: 5px 0 0 0; font-size: 0.9em; color: #555;">{row['car_name']}</p>
                <p style="margin: 5px 0 0 0; font-size: 0.9em; min-height: 43px; overflow: hidden;text-overflow: ellipsis;display: -webkit-box;-webkit-line-clamp: 2;-webkit-box-orient: vertical;">{row['remedy_method']}</p>
            </div>
            """,
            unsafe_allow_html=True
        )

    col_domestic, col_foreign = st.columns(2)

    # 국내 리콜 정보
    with col_domestic:
        st.markdown(
            """
            <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 10px;">
                <h5 style="margin: 0; padding: 0;">⚠️ 국내 리콜</h5>
                <a href="#" on_click={} style="text-decoration: none; color: #165DFB ;">전체 보기 →</a>
            </div>
            """,
            unsafe_allow_html=True
        )
        for data in k_recall_result:
            create_recall_card(data)

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
        for data in o_recall_result:
            create_recall_card(data)
