"""
project_1st_4team/
├── .venv/                         # 가상 환경 (git X )
│
├── backend/                       # 핵심 백엔드/데이터 처리 패키지
│   ├── db_main/                   # DB 저장/조회 레이어 (Repository)
│   ├── bmw_faq.py
│   ├── car_faq.py                 # FAQ DB 저장/조회
│   ├── car_recall.py
│   ├── car_repository.py          # 등록/차량 기본정보 DB 레이어
│   ├── common_repository.py
│   ├── database.py                # DB 연결 설정
│   ├── dim_tables.py
│   ├── flow_repository.py         # 유입/흐름 데이터 저장/조회
│   ├── kia_faq.py
│   ├── load_fact_flow_count.py
│   ├── load_fact_fuel_stock.py
│   ├── load_fact_owner_demo_stock.py
│   ├── load_fact_vehicle_stock.py
│   ├── owner_repository.py
│   └── recall_repository.py       # 리콜 DB 저장/조회  
│
├── project_crawling/              # 크롤링 스크립트 폴더
│   ├── benz.py
│   ├── hyundai.py
│   └── kia_faq.py
│
├── assets/                        # 정적 파일 모음
│   ├── car_excel_files/           # 자동차 등록 통계 엑셀 파일
│   ├── charts/                    # GIS/지도/차트용 shp, prj 파일
│   ├── fonts/                     # 폰트 파일들
│   └── images/                    # 화면/ERD/시스템 구성도 이미지
│
├── views/                         # Streamlit 멀티 페이지 정의 폴더
│   ├── Dashboard.py               # 대시보드
│   ├── CarInfo.py                 # 자동차 정보
│   ├── CarRegistrationList.py     # 2-1 자동차 등록 현황
│   ├── RecallList.py              # 2-2 리콜 목록
│   ├── Map.py                     # 지도 기반 통계
│   └── FAQ.py                     # FAQ 페이지
│
├── .streamlit/
│   └── config.toml                # Streamlit UI/Theme 설정
│
├── streamlit_app.py               # Streamlit 메인 앱 시작 파일
├── requirements.txt               # 프로젝트 의존성 목록
└── README.md                      # 프로젝트 문서
"""