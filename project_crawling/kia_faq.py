import time
import re

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import (
    TimeoutException,
    StaleElementReferenceException,
    ElementClickInterceptedException,
)

URL = "https://www.kia.com/kr/customer-service/center/faq"



def norm(s: str) -> str:
    s = (s or "").replace("\r", "\n")
    s = re.sub(r"[ \t]{2,}", " ", s)
    s = re.sub(r"\n{3,}", "\n\n", s)
    return s.strip()

def js_click(driver, el):
    driver.execute_script("arguments[0].scrollIntoView({block:'center'});", el)
    time.sleep(0.1)
    try:
        el.click()
    except (ElementClickInterceptedException, Exception):
        driver.execute_script("arguments[0].click();", el)

def wait_questions(driver, prev_first_title=None, timeout=15):
    def _get_first_title():
        btns = driver.find_elements(By.CSS_SELECTOR, "button.cmp-accordion__button[id^='accordion-item-']")
        if not btns:
            return None
        try:
            t = btns[0].text
            return norm(t)
        except Exception:
            return None

    WebDriverWait(driver, timeout).until(
        lambda d: len(d.find_elements(By.CSS_SELECTOR, "button.cmp-accordion__button[id^='accordion-item-']")) > 0
    )

    if prev_first_title is not None:
        end = time.time() + timeout
        while time.time() < end:
            cur = _get_first_title()
            if cur and cur != prev_first_title:
                return
            time.sleep(0.2)

def click_tab_all(driver, timeout=15):
    # button.tabs__btn 내부 span에 "전체"
    xpath = (
        "//button[contains(@class,'tabs__btn') and .//span[normalize-space()='전체']]"
        "|//button[contains(@class,'tabs__btn') and contains(normalize-space(.),'전체')]"
    )
    btn = WebDriverWait(driver, timeout).until(EC.presence_of_element_located((By.XPATH, xpath)))
    js_click(driver, btn)

def find_pagination_button(driver, page_num: int):
    # 페이지네이션 영역 안에서 숫자 버튼/링크 찾기 (여러 케이스 대비)
    x = str(page_num)
    xpath = (
        "//*[self::nav or self::div][contains(@class,'pagination') or contains(@class,'paging') or contains(@class,'page') "
        "or contains(@class,'Pagination') or contains(@class,'Paging')]"
        f"//*[self::button or self::a][normalize-space()='{x}']"
        f"|//button[normalize-space()='{x}' and (contains(@class,'page') or contains(@class,'paging') or contains(@class,'pagination'))]"
        f"|//a[normalize-space()='{x}' and (contains(@class,'page') or contains(@class,'paging') or contains(@class,'pagination'))]"
    )
    elems = driver.find_elements(By.XPATH, xpath)
    for e in elems:
        try:
            if e.is_displayed() and e.is_enabled():
                return e
        except Exception:
            pass
    return None

def click_next_pagination(driver):
    # 숫자 페이지가 안 보일 때 "다음" 버튼을 눌러 페이지 리스트 넘기는 fallback
    xpath = (
        "//button[contains(.,'다음') or contains(@aria-label,'다음') or contains(@class,'next')]"
        "|//a[contains(.,'다음') or contains(@aria-label,'다음') or contains(@class,'next')]"
    )
    elems = driver.find_elements(By.XPATH, xpath)
    for e in elems:
        try:
            if e.is_displayed() and e.is_enabled():
                js_click(driver, e)
                return True
        except Exception:
            pass
    return False

def go_to_page(driver, page_num: int, timeout=15):
    # 현재 첫 질문 타이틀을 잡고, 페이지 이동 후 바뀔 때까지 기다림
    prev_first = None
    try:
        btns = driver.find_elements(By.CSS_SELECTOR, "button.cmp-accordion__button[id^='accordion-item-']")
        if btns:
            prev_first = norm(btns[0].text)
    except Exception:
        prev_first = None

    # 페이지 버튼 찾기 (없으면 다음 버튼 눌러보며 재시도)
    for _ in range(3):
        btn = find_pagination_button(driver, page_num)
        if btn:
            js_click(driver, btn)
            wait_questions(driver, prev_first_title=prev_first, timeout=timeout)
            return True
        # 숫자 버튼이 안 보이면 "다음"으로 넘겨서 다시 찾기
        if not click_next_pagination(driver):
            break
        time.sleep(0.4)

    return False

def extract_one(driver, btn):
    # 제목
    question = norm(btn.text)

    # 확장 (aria-expanded=true)
    try:
        expanded = (btn.get_attribute("aria-expanded") or "").lower() == "true"
    except Exception:
        expanded = False

    if not expanded:
        js_click(driver, btn)
        try:
            WebDriverWait(driver, 10).until(
                lambda d: (btn.get_attribute("aria-expanded") or "").lower() == "true"
            )
        except Exception:
            pass

    # panel id는 aria-controls 로 연결됨
    panel_id = btn.get_attribute("aria-controls")
    answer = ""

    if panel_id:
        panel = driver.find_element(By.ID, panel_id)

        # hidden 클래스/표시 상태가 풀릴 때까지
        try:
            WebDriverWait(driver, 10).until(lambda d: panel.is_displayed())
        except Exception:
            pass

        ps = panel.find_elements(By.CSS_SELECTOR, "p")
        lines = []
        for p in ps:
            t = norm(p.text)
            if t:
                lines.append(t)
        answer = norm("\n".join(lines))

    return question, answer


path = "chromedriver.exe"
service = Service(path)
driver = webdriver.Chrome(service=service)
wait = WebDriverWait(driver, 20)

driver.get(URL)

# 1) "전체" 탭 클릭
wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, "button.tabs__btn")))
click_tab_all(driver)
time.sleep(0.6)

# 2) 1~5페이지 순회
for page in range(1, 6):
    if page != 1:
        ok = go_to_page(driver, page)
        if not ok:
            print(f"\n⚠️ {page}페이지로 이동 실패 (페이지네이션 셀렉터 확인 필요)\n")
            break

    wait_questions(driver)

    print(f"\n========== PAGE {page} ==========\n")

    # 현재 페이지의 질문 버튼 목록
    btn_selector = "button.cmp-accordion__button[id^='accordion-item-']"
    count = len(driver.find_elements(By.CSS_SELECTOR, btn_selector))

    for i in range(count):
        # stale 방지: 매번 다시 가져오기
        btns = driver.find_elements(By.CSS_SELECTOR, btn_selector)
        if i >= len(btns):
            break
        btn = btns[i]

        try:
            q, a = extract_one(driver, btn)
        except StaleElementReferenceException:
            time.sleep(0.3)
            btns = driver.find_elements(By.CSS_SELECTOR, btn_selector)
            if i >= len(btns):
                break
            q, a = extract_one(driver, btns[i])

        print(f"[{page}-{i+1}] Q: {q}")
        print(f"A:\n{a}\n{'-'*80}")

# driver.quit()