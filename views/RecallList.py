import streamlit as st
import pandas as pd

def render():
    # -------------------------
    # 기본 설정
    # -------------------------
    st.markdown("<h2>리콜 목록</h2>", unsafe_allow_html=True)
    st.markdown("<p style='color:gray;'>리콜 정보를 확인하고 조치 방법을 안내받으세요.</p>", unsafe_allow_html=True)

    # -------------------------
    # 검색 바 UI
    # -------------------------
    with st.form("search_form"):
        col1, col2, col3, col4, col5, col6 = st.columns([1.2, 1.2, 1.2, 1.2, 3, 1])

        with col1:
            search_type = st.selectbox(" ", ["브랜드 선택", "현대", "기아", "BMW", "벤츠"], label_visibility="collapsed")
        with col2:
            search_value = st.selectbox(" ", ["생산년도 선택", "2025", "2024", "2023"], label_visibility="collapsed")
        with col3:
            year = st.selectbox(" ", ["등록 년 선택", "2025", "2024", "2023"], label_visibility="collapsed")
        with col4:
            month = st.selectbox(" ", ["등록 월 선택"] + [f"{i:02d}" for i in range(1, 13)], label_visibility="collapsed")
        with col5:
            keyword = st.text_input(
                " ",
                placeholder="차종 또는 단어 검색",
                label_visibility="collapsed"
            )
        with col6:
            submit_btn = st.form_submit_button("검색")

    # st.divider()

    # -------------------------
    # 더미 데이터
    # -------------------------
    data = {
        "번호": list(range(1, 51)),
        "지역": ["서울특별시", "경기도", "부산광역시", "인천광역시", "대구광역시"] * 10,
        "차종": ["현대 그랜저", "기아 K5", "현대 소나타", "BMW 5시리즈", "기아 스포티지"] * 10,
        "등록유형": ["신규", "이전", "상속", "증여", "신규"] * 10,
        "등록일": ["2025-12-07"] * 50,
        "등록 대수": [177,193,22,161,34,90,27,179,128,159] * 5
    }

    df = pd.DataFrame(data)

    # -------------------------
    # 상단 요약 + 정렬
    # -------------------------
    left, right = st.columns([7, 2])

    with left:
        st.markdown(f"<p>총 <b>{len(df)}</b>건의 리콜 정보</p>", unsafe_allow_html=True)

    with right:
        sort_opt = st.selectbox(" ", ["정렬 기준 선택", "등록일 최신순", "등록 대수 많은순"], label_visibility="collapsed")

    # -------------------------
    # 테이블 출력
    # -------------------------
    st.dataframe(
        df,
        use_container_width=True,
        hide_index=True
    )

    # -------------------------
    # 페이지네이션 UI
    # -------------------------
    st.markdown(
        """
        <div style='text-align:center; margin-top:20px;'>
            <button style='padding: 4px 12px;border-radius: 4px;border: 1px solid #F7F7F7;background-color: #fff;'>‹</button>
            <button style='padding: 4px 12px;border-radius: 4px;border: 1px solid #F7F7F7;background-color: #fff;'>1</button>
            <button style='padding: 4px 12px;border-radius: 4px;border: 1px solid #F7F7F7;background-color: #fff;'>2</button>
            <button style='padding: 4px 12px;border-radius: 4px;border: 1px solid #F7F7F7;background-color: #fff;'>3</button>
            <button style='padding: 4px 12px;border-radius: 4px;border: 1px solid #F7F7F7;background-color: #fff;'>4</button>
            <button style='padding: 4px 12px;border-radius: 4px;border: 1px solid #F7F7F7;background-color: #fff;'>5</button>
            <button style='padding: 4px 12px;border-radius: 4px;border: 1px solid #F7F7F7;background-color: #fff;'>›</button>
        </div>
        """,
        unsafe_allow_html=True
    )
