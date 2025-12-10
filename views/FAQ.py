import streamlit as st

result = []

def render():
    # -------------------------
    # 기본 설정
    # -------------------------
    st.markdown("<h2>FAQ</h2>", unsafe_allow_html=True)
    st.markdown("<p style='color:gray;'>자동차에 관한 궁금증을 해결하세요.</p>", unsafe_allow_html=True)

    # -------------------------
    # 검색 바 UI
    # -------------------------
    with st.form("search_form"):
        col1, col2, col3 = st.columns([3.5, 4.5, 2])

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
    expander_title = f"{item['question']}"
    # expander_title = f"**{item['category']}** | {item['question']}"
    
    # st.expander를 사용하여 클릭 시 내용이 펼쳐지도록 구현
    with st.expander(expander_title):
        st.info(item['answer'])
