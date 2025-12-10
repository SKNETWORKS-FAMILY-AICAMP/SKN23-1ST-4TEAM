


"""

==========================================
1. ⚙ Global Config (기본 설정값)
==========================================

## 📌 Database Settings
- HOST: skn23-1st-4team.cr6u26mg6lbq.eu-north-1.rds.amazonaws.com
- USER: admin
- PASSWORD: (프로젝트)
- PORT: 3306

# SSH SQL 터미널 설정
Connection Type: MySQL
Host: skn23-1st-4team.cr6u26mg6lbq.eu-north-1.rds.amazonaws.com
Port: 3306

Use SSH Tunnel: ✔  
- SSH Host: ec2-13-61-174-247.eu-north-1.compute.amazonaws.com
- SSH User: ec2-user
- Private Key: <.pem 파일 경로>  개인마다 설정 
- SSH Port: 22


******* 함수 정리 **********
	
Function Name	Description
get_regions	- 시도 목록 조회
get_fuel_types	- 연료 기준정보 조회
get_sido_list	- 시도 목록 조회
	
get_total_new_registrations	- 해당 기간 신규 등록 차량 합계
get_total_used_registrations	- 해당 기간 중고(이전) 등록 합계
get_monthly_registration_trend	- 연간 월별 등록 추이(신규/중고)
get_region_ranking	- 지역별 등록 상위 N개(신규/중고)
	
get_new_vehicle_count	- 전국)해당 연월의 신규 등록 합계
get_vehicle_count_by_type	- 지역->전국:차종별 보유수(승용/승합/화물 등)
get_vehicle_count_by_fuel	- 연료별 보유수(전기/휘발유 등)
get_vehicle_count_by_region	- 지역별 보유수(지역 검색 가능)
get_vehicle_count_by_category	- 용도(관용/ 자가용/ 영업용)별 집계
get_vehicle_stock_search	- 차량 보유대수 상세 검색
	
get_flow_count_by_subtype	- 변동 세부유형별 건수(상속/증여/말소 등)
get_inheritance_gift_count	- 지역별 상속/증여 등록 건수 
get_owner_count_by_age	- 연령대별 차량 소유자 수
get_owner_count_by_gender	- 성별 소유자 수 집계
get_owner_count_by_region	- 지역별 소유자 분포
	
get_recall_list	최신 리콜 목록 조회
get_recall_count_by_maker	- 제조사별 리콜 건수 집계
get_recall_by_car_name	- 차량명별 리콜 건수
get_recall_monthly	- 월별 리콜 수 조회
get_recall_reason_count	- 리콜 사유별 건수
	

"""