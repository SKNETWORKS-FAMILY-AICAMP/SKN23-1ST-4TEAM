import streamlit as st
from views import Dashboard, CarInfo, CarRegistrationList, RecallList, FAQ

st.set_page_config(layout="wide")

# 1. 페이지 상태 초기화 및 이동 함수 정의
if 'page' not in st.session_state:
    st.session_state['page'] = 'dashboard'

def move_page(target_page):
    """세션 상태의 'page' 값을 변경하여 페이지를 이동합니다."""
    st.session_state['page'] = target_page

# 2. 버튼 스타일 변경을 위한 CSS 주입
# CSS를 사용하여 st.button의 배경, 테두리, 그림자 등을 제거합니다.
# !important 를 사용하여 Streamlit의 기본 스타일보다 우선순위를 높입니다.
st.markdown("""
    <style>
    /* 폰트 및 제목 스타일 (사이드바의 "차량 정보 시스템"에 적용) */
    .title-text {
        font-size: 24px;
        font-weight: bold;
        margin-bottom: 20px;
    }

    /* 모든 Streamlit 버튼의 기본 스타일을 재정의 */
    /* 사이드바 내 버튼을 대상으로 지정할 경우 div.stSidebar div.stButton > button 사용 */
    div.stSidebar div.stButton > button {
        background-color: transparent !important; /* 배경색 투명 */
        border: none !important; /* 테두리 제거 */
        box-shadow: none !important; /* 그림자 제거 */
        color: black !important; /* 텍스트 색상 */
        padding: 0px 0px 0px 0px !important; /* 패딩 제거 */
        margin: 5px 0px 5px 0px !important; /* 상하 마진으로 항목 간격 조정 */
        width: 100%; /* 너비를 최대로 설정하여 클릭 영역 확보 */
        text-align: left !important; /* 텍스트를 왼쪽 정렬 */
        font-size: 16px; /* 폰트 크기 설정 */
    }
    
    /* 서브 메뉴 들여쓰기를 위한 스타일 */
    .submenu-indent {
        margin-left: 20px; /* 20px 들여쓰기 */
    }
    
    /* 활성 페이지 버튼 강조 (선택 사항) */
    /* 현재 페이지 버튼의 색상을 변경하여 활성 상태를 표시할 수 있습니다. */
    </style>
    """, unsafe_allow_html=True)


# ==============================================================================
# 3. 사이드바에 메뉴 구성 및 버튼 배치 (st.sidebar 사용)
# ==============================================================================
with st.sidebar:
    # 3-1. 제목
    st.markdown('<div class="title-text">차량 정보 시스템</div>', unsafe_allow_html=True)
    # 헬퍼 함수: 현재 페이지일 경우 CSS 클래스를 추가
    def get_button_class(page_name):
        # 'active-page-button' 클래스가 현재 페이지일 때 적용됨
        return "active-page-button" if st.session_state['page'] == page_name else ""
    
    # 3-2. 메인 메뉴 버튼
    # on_click과 args를 사용하여 페이지 이동 함수를 호출합니다.
    st.button("Dashboard", on_click=move_page, args=('dashboard',), key='sb_dashboard')
    st.button("자동차 정보", on_click=move_page, args=('registration',), key='sb_registration')
    
    # 3-3. 서브 메뉴 (들여쓰기 적용)
    # st.markdown을 사용하여 HTML div 태그로 들여쓰기 클래스를 적용합니다.
    st.button("등록 현황", on_click=move_page, args=('status',), key='sb_status')
    st.button("리콜 목록", on_click=move_page, args=('recall',), key='sb_recall')
    
    # 3-4. 메인 메뉴 버튼
    st.button("FAQ", on_click=move_page, args=('faq',), key='sb_faq')


# ==============================================================================
# 4. 메인 화면 렌더링 로직 (선택된 페이지의 내용을 표시)
# ==============================================================================
page = st.session_state['page']

if page == 'dashboard':
    Dashboard.render()
elif page == 'registration':
    CarInfo.render()
elif page == 'status':
    CarRegistrationList.render()
elif page == 'recall':
    RecallList.render()
elif page == 'faq':
    FAQ.render()