import streamlit as st
import pandas as pd
import math

from backend.db_main.car_repository import get_vehicle_flow_summary_by_region

ROW_COUNT = 10
rows = {
    "등록년월": [],
    "지역": [],
    "차량종류": [],
    "등록대수": []
}

result = get_vehicle_flow_summary_by_region(ROW_COUNT)
year_set = []

for row in result:
    if row['year'] not in year_set:
        year_set.append(row['year'])

    rows['등록년월'].append(f"{row['flow_date']}")
    rows['지역'].append(row['sido_name'])
    rows['차량종류'].append(row['vehicle_kind'])
    rows['등록대수'].append(format(row['flow_count'], ','))

year_list = list(year_set)

TOTAL_PAGES = math.ceil(result[0]['flow_count'] / ROW_COUNT)

def call_registration(page_num):
    return get_vehicle_flow_summary_by_region(ROW_COUNT, page_num-1)

def search_filters(search_type, search_value, year, month, keyword):
    if search_type == "검색 유형 선택":
        search_type = None
        search_value = None
    if year == "등록 년 선택":
        year = None
        month = None
    if keyword == " ":
        keyword = None

        get_vehicle_flow_summary_by_region(ROW_COUNT, 0, search_type, search_value, year, month, keyword)

# Pagenation
if 'current_page' not in st.session_state:
    st.session_state['current_page'] = 1

def go_to_page(page_num):
    """현재 페이지 번호를 업데이트하는 콜백 함수"""
    st.session_state['current_page'] = page_num
    result = call_registration(page_num)

def go_to_prev():
    """이전 페이지로 이동"""
    if st.session_state['current_page'] > 1:
        page_num = st.session_state['current_page'] - 1
        st.session_state['current_page'] = page_num
        result = call_registration(page_num)

def go_to_next():
    """다음 페이지로 이동"""
    if st.session_state['current_page'] < TOTAL_PAGES:
        page_num = st.session_state['current_page'] + 1
        st.session_state['current_page'] = page_num
        result = call_registration(page_num)

def render_pagination_ui():
    MAX_BUTTONS = 5

    current_page = st.session_state['current_page']

    start_page = max(1, current_page - MAX_BUTTONS // 2)
    end_page = min(TOTAL_PAGES, start_page + MAX_BUTTONS - 1)

    if end_page - start_page < MAX_BUTTONS - 1:
        start_page = max(1, end_page - MAX_BUTTONS + 1)

    cols = st.columns([0.5] + [0.3] * (end_page - start_page + 1) + [0.5], border=False)

    # --- [이전] 버튼 ---
    with cols[0]:
        st.button(
            "← 이전",
            on_click=go_to_prev,
            disabled=(current_page == 1), # 첫 페이지에서는 비활성화
            key="btn_prev",
            type='tertiary'
        )
    # --- 페이지 번호 버튼 ---
    # 버튼이 들어갈 칼럼의 인덱스는 1부터 시작
    col_index = 1 
    for page in range(start_page, end_page + 1):
        with cols[col_index]:
            if page == current_page:
                st.button(
                    f"**{page}**", 
                    key=f"btn_page_{page}",
                    type='tertiary'
                )
            else:
                st.button(
                    f"{page}", 
                    on_click=go_to_page(page),
                    key=f"btn_page_{page}",
                    type='tertiary'
                )
        col_index += 1
    # --- [다음] 버튼 ---
    with cols[col_index]:
        st.button(
            "다음 →",
            on_click=go_to_next,
            disabled=(current_page == TOTAL_PAGES), # 마지막 페이지에서는 비활성화
            key="btn_next",
            type='tertiary'
        )

def render():
    # -------------------------
    # 기본 설정
    # -------------------------
    st.markdown("<h2>차량 등록 현황</h2>", unsafe_allow_html=True)
    st.markdown("<p class='text_gray'>차량 등록 정보를 상세하게 확인하세요</p>", unsafe_allow_html=True)

    # -------------------------
    # 검색 바 UI
    # -------------------------
    with st.form("search_form"):
        col1, col2, col3, col4, col5, col6 = st.columns([1.2, 1.2, 1.2, 1.2, 3, 1])

        with col1:
            search_type = st.selectbox(" ", ["검색 유형 선택", "지역", "차종"], label_visibility="collapsed")
        with col2:
            if search_type == "지역":
                search_value = st.selectbox(" ", ["광역시/도 선택"] + rows['지역'], label_visibility="collapsed")
            elif search_type == "차종":
                search_value = st.selectbox(" ", ["유형 값 선택", "승용", "승합", "화물", "특수"], label_visibility="collapsed")
            else:
                search_value = st.selectbox(" ", ["유형 값 선택"], label_visibility="collapsed", disabled=True)
        with col3:
            year = st.selectbox(" ", ["등록 년 선택"] + year_list, label_visibility="collapsed")
        with col4:
            if year == "등록 년 선택":
                month = st.selectbox(" ", ["등록 월 선택"], label_visibility="collapsed", disabled=True)
            else:
                month = st.selectbox(" ", ["등록 월 선택"] + [f"{i:02d}" for i in range(1, 13)], label_visibility="collapsed")
        with col5:
            keyword = st.text_input(
                " ",
                placeholder="차종 또는 지역 검색",
                label_visibility="collapsed"
            )
        with col6:
            st.form_submit_button("검색", on_click=search_filters(search_type, search_value, year, month, keyword))

    df = pd.DataFrame(rows)

    st.container(border=False, height=10)

    # -------------------------
    # 상단 요약 + 정렬
    # -------------------------
    left, right = st.columns([7, 2], vertical_alignment="center")

    with left:
        left.space("small")
        st.markdown(f"<p class='text_black'>총 <b>{format(result[0]['flow_count'], ',')}</b>건의 등록 정보</p>", unsafe_allow_html=True)

    with right:
        st.selectbox("정렬 기준 선택", ["등록일 최신순", "등록 대수 많은순"], label_visibility="collapsed")

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
    _, col_center, _ = st.columns([3, 4, 3])

    with col_center:
        render_pagination_ui()
