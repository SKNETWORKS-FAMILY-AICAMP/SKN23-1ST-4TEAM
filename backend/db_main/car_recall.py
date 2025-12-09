import time
import re
import hashlib
import mysql.connector
from datetime import datetime, date

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC


# MySQL 연결정보
DB = {
    "host": "127.0.0.1",
    "port": 3307,
    "user": "admin",
    "password": "vmfhwprxm",
    "database": "SKN23",
}


#  DB INSERT 함수
def insert_recall_to_db(row_data):
    conn = mysql.connector.connect(**DB)
    cur = conn.cursor()

    sql = """
        INSERT INTO fact_recall (
            recall_date, maker_name, car_name,
            prod_start_date, prod_end_date,
            fix_start_date, fix_end_date,
            target_count, remedy_method, uniq_hash
        )
        VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)
        ON DUPLICATE KEY UPDATE
            remedy_method = VALUES(remedy_method)
    """
    cur.execute(sql, row_data)
    conn.commit()
    cur.close()
    conn.close()


# Selenium 시작
path = "chromedriver.exe"
service = webdriver.chrome.service.Service(path)
driver = webdriver.Chrome(service=service)
wait = WebDriverWait(driver, 10)
wait_detail = WebDriverWait(driver, 20)

driver.get("https://www.car.go.kr/ri/stat/list.do")
time.sleep(1)


# STEP 1: 조회까지 자동 클릭
driver.find_element(By.TAG_NAME, "body").send_keys(Keys.PAGE_DOWN)
time.sleep(1)

driver.find_element(By.CSS_SELECTOR, ".form-group.find").click()
time.sleep(2)

search_box = driver.find_element(By.ID, "srchwrd")
search_box.clear()
search_box.send_keys("볼보")
search_box.send_keys(Keys.RETURN)
time.sleep(2)

driver.find_element(By.XPATH, "//button[text()='조회']").click()
time.sleep(1)

driver.find_element(By.CSS_SELECTOR, ".uk-text-center").click()
time.sleep(1)


search_final_btn = wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, "#srchBtn")))
driver.execute_script("arguments[0].scrollIntoView(true);", search_final_btn)
time.sleep(0.2)
driver.execute_script("arguments[0].click();", search_final_btn)
time.sleep(2)


# 검색이 제대로 적용됐는지 1번만 체크
try:
    first_title = wait.until(
        EC.presence_of_element_located((By.CSS_SELECTOR, "ul.board-hrznt-list li a strong"))
    ).text.strip()
    if "[볼보]" not in first_title:
        print(" [경고] 볼보 검색이 적용되지 않은 것 같아요. 현재 첫 글:", first_title)
except:
    pass


# 유틸: 라벨(th)로 값 뽑기 (핵심 수정 포인트)
def get_td_by_th(label: str) -> str:
    """table-stat 안에서 th 텍스트(label)에 대응하는 첫 번째 td 텍스트를 가져옴"""
    try:
        el = driver.find_element(
            By.XPATH,
            f"//table[contains(@class,'table-stat')]//th[normalize-space()='{label}']/following-sibling::td[1]"
        )
        return el.text.strip()
    except:
        return ""


def parse_date_str(s: str):
    """YYYY-MM-DD -> date, 아니면 None"""
    s = (s or "").strip()
    if not s:
        return None
    try:
        return datetime.strptime(s, "%Y-%m-%d").date()
    except:
        return None


def split_period_to_dates(period_text: str):
    """
    'YYYY-MM-DD ~ YYYY-MM-DD' / 'YYYY-MM-DD ~' / '' 등 처리
    -> (start_date, end_date) as date or None
    """
    txt = (period_text or "").strip()
    if not txt:
        return None, None

    # 텍스트에서 날짜 패턴만 뽑기
    dates = re.findall(r"\d{4}-\d{2}-\d{2}", txt)
    if len(dates) == 0:
        return None, None
    if len(dates) == 1:
        return parse_date_str(dates[0]), None
    return parse_date_str(dates[0]), parse_date_str(dates[1])


def parse_target_count(txt: str):
    """'85,355 대' -> 85355, 없으면 None"""
    t = (txt or "").strip()
    if not t:
        return None
    digits = re.sub(r"[^\d]", "", t)  # 숫자만
    return int(digits) if digits else None


def clean_remedy_method(txt: str):
    """
    시정방법에서 '<단, ... 고객센터 ...>' 안내 문구 제거
    - 고객센터/문의 문장이 포함된 줄 제거
    - '<단' 또는 '단,'으로 시작하는 안내 문구 제거
    """
    t = (txt or "").strip()
    if not t:
        return ""

    lines = [ln.strip() for ln in t.splitlines()]
    cleaned = []
    for ln in lines:
        if not ln:
            continue

        # '<단' / '단,'로 시작하는 안내문 라인 제거
        if ln.startswith("<단") or ln.startswith("단,") or ln.startswith("※"):
            continue

        # 고객센터 안내 문구 제거
        if ("고객센터" in ln and ("문의" in ln or "문의하여" in ln or "문의해" in ln)):
            continue

        cleaned.append(ln)

    # 그래도 본문 중간에 '<단,' 문구가 붙어 들어오면 그 지점에서 잘라냄
    result = "\n".join(cleaned).strip()
    cut_keywords = ["<단", "\n<단", "단, 일부 차량", "제작사 고객센터"]
    cut_pos = None
    for kw in cut_keywords:
        p = result.find(kw)
        if p != -1:
            cut_pos = p if cut_pos is None else min(cut_pos, p)
    if cut_pos is not None:
        result = result[:cut_pos].strip()

    return result


#상세 정보 크롤링 함수
def crawl_detail_page():
    # 상세 페이지로 실제 이동했는지 기다림
    wait_detail.until(EC.presence_of_element_located((By.CSS_SELECTOR, "div.stat-tit div.subject")))

    # 상단 정보
    title = driver.find_element(By.CSS_SELECTOR, "div.stat-tit div.subject").text.strip()
    info_list = driver.find_elements(By.CSS_SELECTOR, "div.stat-tit div.info dd")

    source = info_list[0].text.strip() if len(info_list) > 0 else ""
    write_date_text = info_list[1].text.strip() if len(info_list) > 1 else ""

    # 테이블에서 라벨 기반으로 안정 추출 (핵심)
    maker_name = get_td_by_th("제작(수입)사")
    car_name = get_td_by_th("차명")
    prod_period = get_td_by_th("생산기간")
    fix_period = get_td_by_th("시정기간")
    target_cnt_text = get_td_by_th("대상수량")
    remedy_raw = get_td_by_th("시정방법")

    # 요구사항: 기간 분리 저장
    prod_start_date, prod_end_date = split_period_to_dates(prod_period)
    fix_start_date, fix_end_date = split_period_to_dates(fix_period)

    # 요구사항: 대상수량 숫자만
    target_count = parse_target_count(target_cnt_text)

    # 요구사항: 시정방법 안내문 제거
    remedy_method = clean_remedy_method(remedy_raw)

    # recall_date (작성일) DATE 변환
    recall_date = parse_date_str(write_date_text)

    # 필수값 체크 (NOT NULL 컬럼)
    if not recall_date or not maker_name or not car_name:
        print("[저장 스킵] 필수값 누락",
            f"(recall_date={write_date_text}, maker='{maker_name}', car='{car_name}')",
            " / 제목:", title)
        return

    # uniq_hash (중복방지) - 필수값 위주로 안정 생성
    hash_input = f"{recall_date.isoformat()}|{maker_name}|{car_name}|{prod_period}|{fix_period}|{target_cnt_text}"
    uniq_hash = hashlib.sha256(hash_input.encode("utf-8")).hexdigest()

    # DB insert row
    row_data = (
        recall_date,              # DATE
        maker_name,               # VARCHAR
        car_name,                 # VARCHAR
        prod_start_date,          # DATE or None
        prod_end_date,            # DATE or None
        fix_start_date,           # DATE or None
        fix_end_date,             # DATE or None
        target_count,             # INT or None
        remedy_method,            # TEXT
        uniq_hash                 # CHAR(64)
    )

    insert_recall_to_db(row_data)
    print("✔ DB 저장 완료:", title)


# 링크 클릭 안정화 (Timeout 최소화용, 흐름은 동일)
def open_detail_from_link(link):
    driver.execute_script("arguments[0].scrollIntoView({block:'center'});", link)
    time.sleep(0.1)
    try:
        link.click()
    except:
        driver.execute_script("arguments[0].click();", link)

    # 상세 진입 확인
    wait_detail.until(EC.presence_of_element_located((By.CSS_SELECTOR, "div.stat-tit div.subject")))


# 페이지 순차 이동 (1~10)
for page in range(1, 11):

    print(f"\n========== {page} 페이지 ==========")

    # 페이지네이션 영역까지 스크롤
    pagination = wait.until(
        EC.presence_of_element_located(
            (By.CSS_SELECTOR, "ul.uk-pagination")
        )
    )
    driver.execute_script("arguments[0].scrollIntoView(true);", pagination)
    time.sleep(0.5)

    # 페이지 버튼 클릭 시도
    try:
        page_btn = wait.until(
            EC.element_to_be_clickable(
                (By.XPATH, f"//ul[contains(@class,'pagination')]//a[text()='{page}']")
            )
        )
        driver.execute_script("arguments[0].click();", page_btn)
        time.sleep(1.5)
    except:
        # 1페이지는 span일 수 있음 -> "skip"은 하되, 실제 수집은 현재 페이지에서 진행 가능
        if page == 1:
            print("ℹ 1페이지는 span(현재페이지)이라 클릭 없이 진행")
        else:
            print(f"⚠ {page} 페이지는 클릭할 a 태그가 없어 span 상태일 수 있음. skip")
            continue

    # 글 5개 수집
    links = wait.until(
        EC.presence_of_all_elements_located(
            (By.CSS_SELECTOR, "ul.board-hrznt-list li a")
        )
    )

    for i in range(len(links)):
        links = driver.find_elements(By.CSS_SELECTOR, "ul.board-hrznt-list li a")
        link = links[i]

        print(f"▶ {page}페이지 - {i+1}번째글:", link.text.strip())

        open_detail_from_link(link)   # (기존 link.click() 대신 최소 안정화)
        crawl_detail_page()

        driver.back()
        wait.until(EC.presence_of_all_elements_located((By.CSS_SELECTOR, "ul.board-hrznt-list li a")))
        time.sleep(0.7)


print("\n🎉 모든 페이지 크롤링 및 DB 저장 완료!")
