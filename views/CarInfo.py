import streamlit as st
import pandas as pd

from backend.db_main.recall_repository import get_recall_list
from backend.db_main.flow_repository import get_vehicle_flow_summary_by_region

# 등록현황
rows = {
    "등록년월": [],
    "지역": [],
    "차량종류": [],
    "등록대수": []
}

result = get_vehicle_flow_summary_by_region(5)

for row in result['rows']:
    rows['등록년월'].append(f"{row['year']}년 {row['month']}월")
    rows['지역'].append(row['sido_name'])
    rows['차량종류'].append(row['vehicle_kind'])
    rows['등록대수'].append(format(row['total_flow_count'], ','))

# 리콜
k_recall_result = get_recall_list(5, 1, '국내')
o_recall_result = get_recall_list(5, 1, '해외')

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

        df = pd.DataFrame(rows)

        # Streamlit 데이터프레임/테이블 표시
        # 이미지와 유사하게 인덱스 없이 깔끔하게 표시
        st.dataframe(df, hide_index=True, use_container_width=True)

    ## 2. 국내/해외 리콜 정보 (Domestic/Foreign Recall Information)
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
