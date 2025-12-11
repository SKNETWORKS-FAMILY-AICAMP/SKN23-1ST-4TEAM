"""
PROJECT_1ST_4TEAM/
│
├── backend/                         # 백엔드 로직(Repository, DB, Utils) 전체
│   │
│   ├── db_main/                     # 모든 DB 테이블 / Repository 함수 모음
│   │   ├── car_recall.py            # (미사용 가능) 차량 리콜 관련 특수 로직
│   │   ├── car_repository.py        # 차량 관련 조회 함수 (보유대, 등록 추세 등)
│   │   ├── common_repository.py     # 공통 코드 (SIDO, 연료, 연령대 등 공통 테이블 조회)
│   │   ├── dim_tables.py           
│   │   ├── flow_repository.py       # ‘등록/이전/말소/중고’ 등 차량 흐름 통계 조회
│   │   ├── owner_repository.py      # 소유자 기준 통계 (성별/연령 등)
│   │   ├── recall_repository.py     # 리콜 관련 통계 (제조사별, 차종별, 월별 등)
│   │   │
│   │   ├── load_fact_*.py           # 각 FACT 테이블 ETL 스크립트 (DB 적재용)
│   │   └── (엑셀 데이터 모음)        # FACT 테이블 생성에 사용된 원본 엑셀
│   │
│   ├── utils/                       # 프로젝트 공통 유틸
│   │   ├── db_utils.py              # DB 연결, fetch_all_dict(), fetch_dataframe()
│   │   └── config.py                # DB 접속정보, 공통 설정값
│   │
│   ├── main.py                      
│
├── crawling/                      
│   ├── bmw_crawler.py               
│   └── crawling.py                 
│
├── pages/                          
│   ├── Dashboard.py                
│   └── ...                         
│
├── test_car_repo.py                 # 차량 관련 repository 테스트 코드
├── test_common.py                   # 공통 테이블 조회 테스트
├── test_db.py                       # DB 연결 테스트
├── test_flow.py                     # 차량 등록/중고 흐름 테스트
├── test_owner.py                    # 소유자 통계 테스트
├── test_recall.py                   # 리콜 관련 테스트
│
├── user_flow.drawio                 # 기능 흐름 다이어그램
│
├── streamlit_app.py                 # Streamlit 메인 실행 파일
├── requirements.txt                 # 프로젝트 패키지 설치 목록-
└── README.md                        # 프로젝트 문서 (설명/사용방법) 
"""





