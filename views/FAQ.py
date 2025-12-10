import streamlit as st
from backend.db_main.faq_repository import get_all_faq_latest

page = 0

result = get_all_faq_latest()

def filter_brand(name):
    match name:
        case '현대':
            return '현대'
        case 'KIA':
            return '기아'
        case 'BMW':
            return 'BMW'
        case 'benz':
            return '벤츠'

# 더보기
def click_more_btn():
    global page

    page += 1
    add_data = get_all_faq_latest(10, page)
    result.extend(add_data)


def render():
    # -------------------------
    # 기본 설정
    # -------------------------
    st.markdown("<h2>FAQ</h2>", unsafe_allow_html=True)
    st.markdown("<p style='color:#BDBDBD;'>자동차에 관한 궁금증을 해결하세요.</p>", unsafe_allow_html=True)

    # -------------------------
    # 검색 바 UI
    # -------------------------
    with st.form("search_form"):
        col1, col2, col3 = st.columns([3.5, 5.5, 1])

        with col1:
            search_type = st.selectbox(" ", ["브랜드 선택", "현대", "기아", "BMW", "벤츠"], label_visibility="collapsed")
        with col2:
            keyword = st.text_input(
                " ",
                placeholder="차종 또는 단어 검색",
                label_visibility="collapsed"
            )
        with col3:
            submit_btn = st.form_submit_button("검색")

    for item in result:
        expander_title = f"[ {filter_brand(item['brand'])} ] {item['question']}"
        
        with st.expander(expander_title):
            st.info(item['answer'])

    # 더보기 버튼
    st.button("더보기", on_click=click_more_btn)
