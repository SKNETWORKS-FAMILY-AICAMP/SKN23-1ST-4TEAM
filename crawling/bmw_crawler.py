import csv
import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
# Edge 드라이버 관련 임포트
from selenium.webdriver.edge.service import Service 
from webdriver_manager.microsoft import EdgeChromiumDriverManager 
# 🚨 수정된 부분: EdgeOptions 대신 Options 객체를 사용합니다.
from selenium.webdriver.edge.options import Options 

# --- 1. 설정 및 초기화 ---
URL = "https://faq.bmw.co.kr/s/article-search?language=ko&searchKey=%EB%A6%AC%EC%BD%9C"
CSV_FILE = 'bmw_faq_edge_final.csv'
faq_data = []
total_items_count = 0

print("🔍 BMW FAQ 페이지에 접속합니다...")

try:
    # 📌 Edge 옵션 설정
    # 🚨 EdgeOptions 대신 Options() 객체를 사용합니다.
    edge_options = Options() 
    edge_options.add_argument("--headless") 
    edge_options.add_argument("--disable-gpu") 
    edge_options.add_argument("window-size=1920x1080")

    # EdgeChromiumDriverManager를 사용하여 Edge 드라이버를 자동 설치 및 설정
    service = Service(EdgeChromiumDriverManager().install())
    driver = webdriver.Edge(service=service, options=edge_options) 
    
    wait = WebDriverWait(driver, 15)

    # --- 2. 페이지 접속 및 로딩 대기 ---
    driver.get(URL)

    result_container_selector = ".scpCarouselSearchContainer" 
    wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, result_container_selector)))
    print("✅ 검색 결과 컨테이너 탐색 성공. 데이터 로딩을 시작합니다.")
    time.sleep(2)

    # --- 3. "더보기" 버튼 반복 클릭 (모든 데이터 로드) ---
    load_more_button_selector = ".slds-button_brand[title='더보기']"
    
    while True:
        try:
            load_more_button = wait.until(
                EC.element_to_be_clickable((By.CSS_SELECTOR, load_more_button_selector))
            )
            
            driver.execute_script("arguments[0].click();", load_more_button)
            time.sleep(1.5)
            print("👉 '더보기' 버튼 클릭...")

        except Exception:
            print("🛑 더 이상 표시할 항목이 없습니다. 모든 데이터 로드 완료.")
            break

    # --- 4. 데이터 추출 (Extraction) ---
    link_selector = "c-scp-article-list-item a.slds-truncate"
    
    items = driver.find_elements(By.CSS_SELECTOR, link_selector)
    total_items_count = len(items)
    print(f"📌 총 {total_items_count}개의 검색 결과 항목 발견.")

    for item in items:
        try:
            title = item.text
            url = item.get_attribute('href')
            
            faq_data.append({'Title': title, 'URL': url})
            
        except Exception:
            continue

    # --- 5. CSV 파일로 저장 ---
    with open(CSV_FILE, 'w', newline='', encoding='utf-8-sig') as f:
        fieldnames = ['Title', 'URL']
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(faq_data)

    print(f"🎉 완료! 총 {len(faq_data)}개의 FAQ가 '{CSV_FILE}'에 CSV 형식으로 저장되었습니다.")


except Exception as e:
    print(f"\n❌ 크롤링 중 치명적인 오류 발생:")
    print(e)

finally:
    if 'driver' in locals():
        driver.quit()
        print("브라우저 종료.")