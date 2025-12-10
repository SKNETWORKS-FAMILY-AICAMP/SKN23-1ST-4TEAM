import streamlit as st
import pandas as pd
import altair as alt
import plotly.express as px
import json
from backend.db_main.database import get_connection
from backend.db_main.recall_repository import get_recall_list, get_recall_monthly
from backend.db_main.car_repository import get_total_new_registrations, get_total_used_registrations, get_monthly_registration_trend, get_region_ranking

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

year = 2025
month = 10

# 신규 등록
def get_regist_monthly():
    global year, month

    sub = get_total_new_registrations(year, (month-1), year, (month-1))
    this = get_total_new_registrations(year, month, year, month)
    rate = calculate_growth_rate(sub['total_new'], this['total_new'])

    return [sub['total_new'], this['total_new'], rate]

# 중고 등록
def get_old_monthly():
    global year, month
    
    sub = get_total_used_registrations(year, (month-1), year, (month-1))
    this = get_total_used_registrations(year, month, year, month)
    rate = calculate_growth_rate(sub['total_used'], this['total_used'])

    return [sub['total_used'], this['total_used'], rate]

# 등록 차트
def make_regist_chart_data():
    global year

    new_result = get_monthly_registration_trend(get_connection(), year, "신규")
    old_result = get_monthly_registration_trend(get_connection(), year, "중고")

    all_records = []

    for item in new_result['items']:
        # new_rows.append(item['count'])
        all_records.append({
            '년도': year,
            '월': item['month'],
            '등록 유형': "신규",
            '등록 대수': item['count']
        })

    for item in old_result['items']:
        # old_rows.append(item['count'])
        all_records.append({
            '년도': year,
            '월': item['month'],
            '등록 유형': "중고",
            '등록 대수': item['count']
        })

    return all_records

def make_region_chart_data():
    global year, month

    new_rows = []
    old_rows = []

    new_result = get_region_ranking(get_connection(), year, month, "신규")
    old_result = get_region_ranking(get_connection(), year, month, "중고")

    regions = [item['sido_name'] for item in new_result['ranking']]
    new_rows = [item['count'] for item in new_result['ranking']]
    old_rows = [item['count'] for item in old_result['ranking']]

    return [regions, new_rows, old_rows]

# 이번달 등록 수
regist_result = get_regist_monthly()

# 중고 등록 수
old_result = get_old_monthly()

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

# 월별 등록 차트
monthly_chart_result = make_regist_chart_data()

# 광역시도별 지도 차트
region_map_data = {}
df = pd.DataFrame({
    "region": list(region_map_data.keys()),
    "value": list(region_map_data.values())
})

with open("./assets/korea_sido_wgs84.geojson", encoding="utf-8") as f:
    korea_geo = json.load(f)


# 지역별 등록 차트
region_chart_result = make_region_chart_data()

# 리콜 목록 조회
k_recall_result = get_recall_list(5, 1, '국내')
o_recall_result = get_recall_list(5, 1, '해외')

def render():
    st.markdown("<h2>2025년 12월 자동차 등록 현황</h2>", unsafe_allow_html=True)
    st.markdown("<p style='color:gray;'>지역별 신규 등록 트렌드와 리콜 정보를 한눈에 확인하세요.</p>", unsafe_allow_html=True)

    ## 1. 상단 요약 카드 (Summary Cards)
    col1, col2, col3 = st.columns(3)

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
        create_summary_card("이번 달 중고/이전 등록", old_result)

    with col3:
        create_summary_card("이번 달 리콜 등록", recall_data)

    ## 2. 차트
    chart_col1, chart_col2 = st.columns(2)

    ### 월별 신규 등록 추이
    with chart_col1:
        st.markdown("<h5 style='margin: 0; padding: 0;'>월별 신규 자동차 등록 추이</h5>", unsafe_allow_html=True)

        line_chart_df = pd.DataFrame(monthly_chart_result)

        # Altair 차트 정의
        line_chart = alt.Chart(line_chart_df).mark_line(point=True).encode(
            # X축: 월 (연속형, 월별 순서로)
            x=alt.X('월', axis=alt.Axis(tickMinStep=1, title='월')),
            
            # Y축: 등록 대수
            y=alt.Y('등록 대수', title='등록 대수'),
            
            # 색상: 등록 유형(신규/중고)에 따라 라인 분리
            color='등록 유형',
            
            # 툴팁 추가
            tooltip=['월', '등록 유형', '등록 대수']
        ).properties(
            title=f"{year}년 월별 등록 추이"
        ).interactive()

        # Streamlit에 Altair 차트 표시
        st.altair_chart(line_chart, use_container_width=True)

    ### 지역별 신규 등록 현황
    with chart_col2:
        fig = px.choropleth(
            df,
            geojson=korea_geo,
            locations="region",
            featureidkey="properties.CTP_KOR_NM",
            color="value",
            hover_name="region",
            hover_data={"value": True},
            color_continuous_scale="Blues"
        )

        fig.update_geos(fitbounds="locations", visible=True)

        # Streamlit에 표시
        st.plotly_chart(fig, use_container_width=True)



        # st.markdown("<h5 style='margin: 0; padding: 0;'>지역별 신규 등록 현황</h5>", unsafe_allow_html=True)

        # print(f"지역 리스트 길이: {len(region_chart_result[0])}")
        # print(f"신규 등록 리스트 길이: {len(region_chart_result[1])}")
        # print(f"중고 등록 리스트 길이: {len(region_chart_result[2])}")

        # regional_df = pd.DataFrame({
        #     '지역': region_chart_result[0],
        #     '신규 등록': region_chart_result[1],
        #     '중고 등록': region_chart_result[2]
        # })
        
        # long_df = pd.melt(
        #     regional_df,
        #     id_vars=['지역'],
        #     value_vars=['신규 등록', '중고 등록'],
        #     var_name='등록 구분',
        #     value_name='등록 대수'
        # )
        # base = alt.Chart(long_df).encode(
        #     x=alt.X('지역', sort=region_chart_result[0]), # 지역 순서 유지
        #     y=alt.Y('등록 대수', title='등록 대수'),
        #     color='등록 구분',
        #     tooltip=['지역', '등록 구분', '등록 대수']
        # )
        # chart = base.mark_bar().encode(
        #     x=alt.X('등록 구분', axis=None), # x축에는 등록 구분 이름을 숨깁니다.
        #     column=alt.Column('지역', header=alt.Header(titleOrient="bottom", labelOrient="bottom")), # 지역별로 분리
        # )

        # st.altair_chart(chart, use_container_width=True)

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
