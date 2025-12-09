# 실행 창 
""" 
backend/
 │
 ├── db_main/
 │     ├── database.py                # MySQL 연결
 │     ├── faq_repository.py          # FAQ DB 저장/조회
 │     ├── recall_repository.py       # 리콜 DB 저장/조회
 │     └── user_repository.py         # 사용자 정보 (옵션) 연령대별
 │
 ├── utils/
 │     ├── excel_utils.py
 |     |-- db_utils.py
 │     ├── text_utils.py
 │     └── log_utils.py    
 
 │
 ├── data/
 │     ├── temp/                      # 임시 파일만
 │
 ├── ui/
 │     └── streamlit_app.py           # Streamlit UI → DB에서 읽기
 │---test_db.py 서버 연결 및 닫기 함수 테스트
 |----test_car_repo.py 차량 함수 테스트 
 ├── config.py   #고정된 값&ui 조건 
 └── main.py    #실행 파일
 """

