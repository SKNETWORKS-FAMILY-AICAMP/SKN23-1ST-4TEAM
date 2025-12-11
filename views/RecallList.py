import streamlit as st

from backend.db_main.recall_repository import get_recall_list

page = 0
list_count = 10

recall_result = get_recall_list(list_count, page)

def search_filters(search_type, search_value, year, month, keyword):
    global list_count, page, recall_result
    recall_result = get_recall_list(list_count, page, None, search_type, search_value, year, month, keyword)

# 더보기
def click_more_btn():
    global page, list_count, recall_result

    page += 1
    add_data = get_recall_list(list_count, page)
    recall_result.extend(add_data)


def render():
    global recall_result
    st.markdown("<h2>리콜 목록</h2>", unsafe_allow_html=True)
    st.markdown("<p class='text_gray'>리콜 정보를 확인하고 조치 방법을 안내받으세요.</p>", unsafe_allow_html=True)

    # 검색 바 UI -------------------------
    with st.form("search_form"):
        col1, col3, col4, col5, col6 = st.columns([1.6, 1.6, 1.6, 3, 1])
        search_value = None

        with col1:
            search_type = st.selectbox(" ", ["브랜드 선택","(주)볼보자동차코리아","기아 주식회사","르노코리아(주)","메르세데스벤츠코리아(주)","비엠더블유코리아(주)","포르쉐코리아 주식회사","현대자동차(주)"], label_visibility="collapsed")
        # with col2:
        #     search_value = st.number_input(placeholder="생산 년도 입력")
        with col3:
            year = st.selectbox(" ", ["등록 년 선택"] + [f"{i:02d}" for i in range(2025, 2020, -1)], label_visibility="collapsed")
        with col4:
            month = st.selectbox(" ", ["등록 월 선택"] + [f"{i:02d}" for i in range(1, 13)], label_visibility="collapsed")
        with col5:
            keyword = st.text_input(
                " ",
                placeholder="차종 또는 단어 검색",
                label_visibility="collapsed"
            )
        with col6:
            st.form_submit_button("검색", on_click=search_filters(search_type, search_value, year, month, keyword))

    # -------------------------
    # 상단 요약 + 정렬
    # -------------------------
    _, right = st.columns([7, 2])

    # with left:
        # st.markdown(f"<p class='text_black'>총 <b>{len(recall_result)}</b>건의 리콜 정보</p>", unsafe_allow_html=True)

    with right:
        sort_opt = st.selectbox(" ", ["정렬 기준 선택", "등록일 최신순", "등록 대수 많은순"], label_visibility="collapsed")

    # 리콜 카드 생성 함수
    def create_recall_card(row):
        st.markdown(
            f"""
            <div class='text_black' style="border: 1px solid #D7D7D7; border-radius: 8px; padding: 15px; margin-bottom: 10px; line-height: 1.5;">
                <div>
                    <b style="margin: 0;">{row['maker_name']}</b>
                    <span style="float: right; margin-right: 6px; font-size: 0.9em; color: #555;">시행일자: {row['fix_start_date']}</span>
                </div>
                <p style="margin: 5px 0 0 0; font-size: 0.9em; color: #555;">{row['car_name']}</p>
                <p style="margin: 5px 0 0 0; font-size: 0.9em;">{row['remedy_method']}</p>
            </div>
            """,
            unsafe_allow_html=True
        )

    recall_result = get_recall_list(list_count, page)   

    for row in recall_result:
        print(row)
        create_recall_card(row)

    # 더보기 버튼
    st.button("더보기", on_click=click_more_btn)
