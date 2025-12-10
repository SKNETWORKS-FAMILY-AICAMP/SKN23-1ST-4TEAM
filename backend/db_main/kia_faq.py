import time
import hashlib
import mysql.connector

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, StaleElementReferenceException



# MySQL 연결정보
DB = {
    "host": "127.0.0.1",
    "port": 3307,
    "user": "admin",
    "password": "vmfhwprxm",
    "database": "SKN23",
}

BRAND = "KIA"
CATEGORY = "전체"


def sha256_hex(s: str) -> str:
    return hashlib.sha256(s.encode("utf-8")).hexdigest()


def normalize(s: str) -> str:
    if not s:
        return ""
    s = s.replace("\r", "\n").strip()
    # 줄 중복 공백 정리(선택)
    lines = [ln.strip() for ln in s.split("\n")]
    lines = [ln for ln in lines if ln]
    return "\n".join(lines).strip()


def safe_click(driver, el):
    driver.execute_script("arguments[0].scrollIntoView({block:'center'});", el)
    time.sleep(0.15)
    try:
        el.click()
    except Exception:
        driver.execute_script("arguments[0].click();", el)


def save_faq(cur, brand: str, category: str, question: str, answer: str) -> bool:
    question = (question or "").strip()
    answer = (answer or "").strip()

    if not question or not answer:
        return False

    # 테이블이 question VARCHAR(100) 이라서 초과 방지
    if len(question) > 100:
        question = question[:100]

    uniq_hash = sha256_hex(f"{brand}|{category}|{question}")

    sql = """
    INSERT INTO faq (brand, category, question, answer, uniq_hash)
    VALUES (%s, %s, %s, %s, %s)
    ON DUPLICATE KEY UPDATE
      answer = VALUES(answer),
      updated_at = CURRENT_TIMESTAMP
    """
    cur.execute(sql, (brand, category, question, answer, uniq_hash))
    return True



# 1) 전체 탭 클릭
def click_tab_all(driver, wait: WebDriverWait):
    # button.tabs__btn 안에 span 텍스트가 "전체"
    all_btn = wait.until(
        EC.element_to_be_clickable(
            (By.XPATH, "//button[contains(@class,'tabs__btn')][.//span[normalize-space()='전체']]")
        )
    )
    safe_click(driver, all_btn)
    time.sleep(0.6)


# 2) 페이지네이션 이동(1~5)
def goto_page(driver, wait: WebDriverWait, page_num: int):
    # 페이지 이동 전 첫 질문 텍스트(변화 감지용)
    def get_first_question_text():
        try:
            btn = driver.find_element(By.CSS_SELECTOR, "button[id^='accordion-item-'][id$='-button']")
            return btn.text.strip()
        except Exception:
            return ""

    before = get_first_question_text()

    # 화면 아래로 내려서 pagination이 보이게
    driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
    time.sleep(0.4)

    # 페이지 숫자 버튼/링크를 최대한 넓게 찾기
    xpaths = [
        f"//button[normalize-space()='{page_num}']",
        f"//a[normalize-space()='{page_num}']",
        f"//div[contains(@class,'pagination') or contains(@class,'paging') or contains(@class,'page')]"
        f"//*[self::a or self::button][normalize-space()='{page_num}']",
    ]

    target = None
    for xp in xpaths:
        try:
            target = wait.until(EC.element_to_be_clickable((By.XPATH, xp)))
            break
        except TimeoutException:
            continue

    if not target:
        raise RuntimeError(f"페이지 {page_num} 버튼을 찾지 못했어. (pagination selector 확인 필요)")

    safe_click(driver, target)

    # 페이지가 바뀔 때까지 대기(첫 질문이 바뀌거나, active 표시가 바뀌는 순간)
    end = time.time() + 10
    while time.time() < end:
        time.sleep(0.3)
        now = get_first_question_text()
        if now and now != before:
            return
    # 텍스트가 동일해도 페이지가 바뀌는 경우가 있어 약간의 여유
    time.sleep(0.6)



# 3) 한 페이지에서 Q/A 수집(제목 클릭 → 답변 p만)
def scrape_current_page(driver, wait: WebDriverWait):
    # 제목 버튼들
    wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, "button[id^='accordion-item-'][id$='-button']")))

    results = []

    # 개수가 DOM 변경으로 바뀔 수 있으니 "인덱스 기반 재탐색"으로 안전하게
    buttons = driver.find_elements(By.CSS_SELECTOR, "button[id^='accordion-item-'][id$='-button']")
    total = len(buttons)

    for i in range(total):
        # 매번 다시 찾기(열고 닫히면서 stale 방지)
        try:
            btns = driver.find_elements(By.CSS_SELECTOR, "button[id^='accordion-item-'][id$='-button']")
            if i >= len(btns):
                break
            btn = btns[i]

            # 제목(버튼 안 span.cmp-accordion__title 우선, 없으면 버튼 텍스트)
            try:
                title_el = btn.find_element(By.CSS_SELECTOR, "span.cmp-accordion__title")
                question = title_el.text.strip()
            except Exception:
                question = btn.text.strip()

            # 확장(aria-expanded=true)
            safe_click(driver, btn)
            try:
                wait.until(lambda d: (btn.get_attribute("aria-expanded") or "").lower() == "true")
            except Exception:
                pass

            # panel id 가져오기(aria-controls)
            panel_id = btn.get_attribute("aria-controls")  # ex) accordion-item-0-panel
            if not panel_id:
                # 혹시 구조가 다를 때 대비: id 규칙으로 추정
                bid = btn.get_attribute("id") or ""
                panel_id = bid.replace("-button", "-panel")

            # 패널이 DOM에 보이도록 기다렸다가 p 텍스트 수집
            panel = wait.until(EC.presence_of_element_located((By.ID, panel_id)))
            # "숨김" 클래스가 풀릴 시간을 조금 줌
            time.sleep(0.2)

            p_list = panel.find_elements(By.CSS_SELECTOR, "p")
            lines = []
            for p in p_list:
                t = (p.text or "").strip()
                if t:
                    lines.append(t)

            answer = normalize("\n".join(lines))
            question = normalize(question)

            results.append((question, answer))

        except StaleElementReferenceException:
            # DOM이 갱신되면 한 번 정도는 재시도하는 느낌으로 스킵하지 않게 처리
            time.sleep(0.4)
            continue

    return results



# MAIN
def main():
    path = "chromedriver.exe"
    service = Service(path)
    driver = webdriver.Chrome(service=service)
    wait = WebDriverWait(driver, 15)

    # DB
    conn = mysql.connector.connect(**DB)
    conn.autocommit = False
    cur = conn.cursor()

    saved, skipped = 0, 0

    try:
        driver.get("https://www.kia.com/kr/customer-service/center/faq")

        # 전체 탭 클릭
        click_tab_all(driver, wait)

        # 1~5 페이지 수집
        for page in range(1, 6):
            if page != 1:
                goto_page(driver, wait, page)

            qa_list = scrape_current_page(driver, wait)
            print(f"\n=== Page {page} / 수집 {len(qa_list)}개 ===")

            for idx, (q, a) in enumerate(qa_list, 1):
                print(f"[{page}-{idx}] Q: {q}")
                print(f"A: {a}\n" + "-" * 80)

                try:
                    ok = save_faq(cur, BRAND, CATEGORY, q, a)
                    if ok:
                        conn.commit()
                        saved += 1
                    else:
                        skipped += 1
                except Exception as e:
                    conn.rollback()
                    skipped += 1
                    print(f"DB 저장 실패(롤백): {e}")

        print(f"\n✅ 완료! 저장 성공: {saved} / 스킵(빈값·실패): {skipped}")

    finally:
        try:
            cur.close()
            conn.close()
        except Exception:
            pass
        # driver.quit()


if __name__ == "__main__":
    main()
