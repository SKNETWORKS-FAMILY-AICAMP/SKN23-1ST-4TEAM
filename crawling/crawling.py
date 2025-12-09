from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.keys import Keys
import time

# 1. 사용할 정보
SEARCH_KEYWORD = "리콜"
BASE_URL = "https://faq.bmw.co.kr/s/?language=ko&searchKey&hashtags"
SEARCH_INPUT_CLASS = 'scpSearch' # ★ 클래스 변경 ★

# 2. WebDriver 설정
options = webdriver.ChromeOptions()
options.add_argument('--no-sandbox')
options.add_argument('--disable-dev-shm-usage')
driver = webdriver.Chrome(options=options)

print(f"--- BMW FAQ 검색 테스트 시작 (클래스: {SEARCH_INPUT_CLASS}, 검색어: {SEARCH_KEYWORD}) ---")

try:
    # 1. 초기 페이지 로드
    driver.get(BASE_URL)
    print("초기 페이지 로드 완료. 검색창 탐색 시작.")
    
    wait = WebDriverWait(driver, 15) # 15초 대기
    
    # 2. 검색창(scpSearch) 요소 탐색
    try:
        search_input = wait.until(
            EC.presence_of_element_located((By.CLASS_NAME, SEARCH_INPUT_CLASS))
        )
        print(f"✅ 검색창({SEARCH_INPUT_CLASS}) 찾기 성공.")
        
    except TimeoutException:
        print(f"❗ 검색창({SEARCH_INPUT_CLASS})을 찾는 데 실패했습니다. 클래스 이름을 다시 확인해 주세요.")
        driver.quit()
        exit()

    # 3. 검색어 입력 및 실행
    search_input.send_keys(SEARCH_KEYWORD)
    search_input.send_keys(Keys.ENTER) # Enter 키를 눌러 검색 실행
    print(f"'{SEARCH_KEYWORD}' 검색 실행 완료. 결과 페이지 로드 대기.")
    
    # 4. 결과 페이지 로드를 위해 충분히 대기
    time.sleep(5) 
    
    # 5. 현재 URL 확인 및 멈춤
    print(f"\n✅ 검색 결과 페이지로 이동 완료.")
    print("브라우저를 확인하시고, **질문 제목**의 **클래스/태그**를 찾아주세요.")
    
    input("확인 완료 (엔터를 누르면 브라우저가 종료됩니다)...")


finally:
    driver.quit()
    print("--- 브라우저 종료 ---")