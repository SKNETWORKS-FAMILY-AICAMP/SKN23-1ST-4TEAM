import streamlit as st
import pandas as pd

def render():
    # -------------------------
    # 기본 설정
    # -------------------------
    st.markdown("<h2>자동차 정보</h2>", unsafe_allow_html=True)
    st.markdown("<p style='color:gray;'>차량 등록 현황 및 리콜 정보를 확인하세요.</p>", unsafe_allow_html=True)
    
    with st.container():
        st.write("최근 차량 등록 현황")

        confusion_matrix = pd.DataFrame(
            {
                "지역": [85, 3, 2, 1],
                "차종": [2, 78, 4, 0],
                "등록유형": [1, 5, 72, 3],
                "날짜": [0, 2, 1, 89],
                "대수": [1, 1, 1, 1]
            }
        )
        st.table(confusion_matrix)

    recall = []

    left, right = st.columns(2)

    with left:
        st.write("최근 국내 리콜 목록")
        for data in range(3):
            with st.container():
                st.write('현대자동차')
                st.text('그랜저')
                st.text('에어백 불량')

    with right:
        st.write("최근 해외 리콜 목록")
