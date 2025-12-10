import time
import re
import hashlib
import html

import mysql.connector
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.action_chains import ActionChains

from selenium.common.exceptions import (
    TimeoutException,
    StaleElementReferenceException,
    JavascriptException,
)


# MySQL 연결정보
DB = {
    "host": "127.0.0.1",
    "port": 3307,
    "user": "admin",
    "password": "vmfhwprxm",
    "database": "SKN23",
}

def wait_for_url_stable(driver, timeout=10, stable_for=2.0, poll=0.2):
    end = time.time() + timeout
    last = driver.current_url
    last_change = time.time()

    while time.time() < end:
        cur = driver.current_url
        if cur != last:
            last = cur
            last_change = time.time()
        else:
            if time.time() - last_change >= stable_for:
                return True
        time.sleep(poll)
    return False


def accept_cookies_bmw(driver, timeout=10, delay_after_stable=3.5):
    wait = WebDriverWait(driver, timeout)

    wait_for_url_stable(driver, timeout=min(10, timeout), stable_for=1.5)
    time.sleep(delay_after_stable)

    span_css = "div.buttons.buttonsMobile button.accept-button span.button-text"
    btn_css  = "div.buttons.buttonsMobile button.accept-button"

    def popup_gone(d):
        try:
            elems = d.find_elements(By.CSS_SELECTOR, btn_css)
            visible = [e for e in elems if e.is_displayed()]
            return len(visible) == 0
        except StaleElementReferenceException:
            return True

    end = time.time() + timeout
    while time.time() < end:
        try:
            span = WebDriverWait(driver, 3).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, span_css))
            )

            driver.execute_script("arguments[0].scrollIntoView({block:'center'});", span)
            time.sleep(0.1)

            clicked = False

            try:
                ActionChains(driver).move_to_element(span).pause(0.05).click(span).perform()
                clicked = True
            except Exception:
                pass

            if not clicked:
                try:
                    driver.execute_script("arguments[0].click();", span)
                    clicked = True
                except Exception:
                    pass

            if not clicked:
                btn = driver.find_element(By.CSS_SELECTOR, btn_css)
                driver.execute_script("arguments[0].scrollIntoView({block:'center'});", btn)
                try:
                    btn.click()
                    clicked = True
                except Exception:
                    driver.execute_script("arguments[0].click();", btn)
                    clicked = True

            try:
                WebDriverWait(driver, 6).until(popup_gone)
                return True
            except TimeoutException:
                pass

        except TimeoutException:
            time.sleep(0.3)
        except StaleElementReferenceException:
            time.sleep(0.3)
        except Exception:
            time.sleep(0.3)

        try:
            js = """
            const targetText = '모두 수락';
            const selBtn = 'button.accept-button';
            const selSpan = 'span.button-text';
            function deepQuery(root) {
            const out = [];
            const walk = (node) => {
                if (!node) return;
                if (node.querySelectorAll) {
                out.push(...node.querySelectorAll(selSpan));
                out.push(...node.querySelectorAll(selBtn));
                }
                const all = node.querySelectorAll ? node.querySelectorAll('*') : [];
                for (const el of all) {
                if (el.shadowRoot) walk(el.shadowRoot);
                }
            };
            walk(root);
            return out;
            }
            const items = deepQuery(document);
            const span = items.find(x => x.matches && x.matches(selSpan) && x.textContent.trim() === targetText);
            if (span) { span.click(); return true; }
            const btn = items.find(x => x.matches && x.matches(selBtn) && x.textContent.includes(targetText));
            if (btn) { btn.click(); return true; }
            return false;
            """
            clicked = driver.execute_script(js)
            if clicked:
                try:
                    WebDriverWait(driver, 6).until(popup_gone)
                    return True
                except TimeoutException:
                    pass
        except Exception:
            pass

        time.sleep(0.3)

    return False


path = "chromedriver.exe"
service = Service(path)
driver = webdriver.Chrome(service=service)

driver.get("https://faq.bmw.co.kr/s/?language=ko")

accepted = accept_cookies_bmw(driver, timeout=25, delay_after_stable=3.5)
print("쿠키 수락 처리:", accepted)

time.sleep(3)

Ai_assistant_btn = driver.find_element(By.CSS_SELECTOR, ".outline-bmwBlue")
Ai_assistant_btn.click()
time.sleep(2)

# 여기부터 프로세스 시작: load more 끝까지 → Q/A 전체 수집(터미널 출력 + DB 저장)

DEEP_QUERY_JS = r"""
const selector = arguments[0];
const results = [];
function walk(root) {
  if (!root) return;
  if (root.querySelectorAll) results.push(...root.querySelectorAll(selector));
  const all = root.querySelectorAll ? root.querySelectorAll('*') : [];
  for (const el of all) {
    if (el.shadowRoot) walk(el.shadowRoot);
  }
}
walk(document);
return results;
"""

def deep_find_css(selector):
    try:
        return driver.execute_script(DEEP_QUERY_JS, selector) or []
    except JavascriptException:
        return []

def safe_click(el):
    driver.execute_script("arguments[0].scrollIntoView({block:'center'});", el)
    time.sleep(0.15)
    try:
        el.click()
    except Exception:
        driver.execute_script("arguments[0].click();", el)

def normalize_text(s: str) -> str:
    s = html.unescape((s or ""))          # &quot; 같은 엔티티 복원
    s = s.replace("\r", "\n")
    s = re.sub(r"\n{3,}", "\n\n", s)
    s = re.sub(r"[ \t]{2,}", " ", s)
    return s.strip()

def strip_disclaimer(answer: str) -> str:
    """
    답변 끝에 붙는 면책/주의 문구 제거:
    '*차량의 옵션...' '*위 전비...' '*충전 시간...' '도움이 되었습니까?' 등 시작 지점에서 잘라냄
    """
    if not answer:
        return answer

    markers = [
        "\n*차량의 옵션",
        "\n*위 전비",
        "\n*충전 시간",
        "\n도움이 되었습니까",
        "\n프로필 및 개인",
        "\n서비스",
        "\n모델 & 옵션",
        "\n기술 & 혁신",
        "\nBMW ConnectedDrive",
    ]

    cut = None
    for m in markers:
        pos = answer.find(m)
        if pos != -1:
            cut = pos if cut is None else min(cut, pos)

    if cut is not None:
        answer = answer[:cut]

    # 라인 단위로도 한번 더 정리(가끔 맨앞부터 별표로 시작하는 케이스 방지)
    lines = [ln.rstrip() for ln in answer.splitlines()]
    cleaned = []
    for ln in lines:
        if ln.strip().startswith("*차량의 옵션") or ln.strip().startswith("*위 전비") or ln.strip().startswith("*충전 시간"):
            break
        if ln.strip().startswith("도움이 되었습니까"):
            break
        cleaned.append(ln)
    return "\n".join(cleaned).strip()

QUESTION_SEL = "h2.article-headline button"
LOADMORE_SEL = 'button[data-name="loadMoreButton"].button.buttonOutline.slds-align_absolute-center'

def click_loadmore_until_end(max_clicks=500):
    clicks = 0
    stagnant = 0

    WebDriverWait(driver, 25).until(lambda d: len(deep_find_css(QUESTION_SEL)) > 0)

    while clicks < max_clicks:
        before = len(deep_find_css(QUESTION_SEL))

        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        time.sleep(0.6)

        btns = driver.find_elements(By.CSS_SELECTOR, LOADMORE_SEL)
        load_btn = None
        for b in btns:
            try:
                if b.is_displayed() and b.is_enabled():
                    load_btn = b
                    break
            except Exception:
                pass

        if not load_btn:
            btns = deep_find_css('button[data-name="loadMoreButton"]')
            for b in btns:
                try:
                    if b.is_displayed() and b.is_enabled():
                        load_btn = b
                        break
                except Exception:
                    pass

        if not load_btn:
            break

        safe_click(load_btn)
        clicks += 1

        end_wait = time.time() + 12
        grew = False
        while time.time() < end_wait:
            time.sleep(0.4)
            after = len(deep_find_css(QUESTION_SEL))
            if after > before:
                grew = True
                break

        if not grew:
            stagnant += 1
        else:
            stagnant = 0

        if stagnant >= 3:
            break

    return clicks

# 답변 후보를 여러 개 수집 → (면책 제거 후) 가장 긴 본문을 선택
def extract_qa(btn):
    js = r"""
    const btn = arguments[0];
    const question = (btn.innerText || '').trim();

    const container =
    (btn.getRootNode && btn.getRootNode().host) ||
    btn.closest('c-scp-article-list-item-expandable') ||
    btn.closest('div.article-list-item') ||
    document;

    function isVisible(el) {
    try {
        const s = window.getComputedStyle(el);
        if (!s) return false;
        if (s.display === 'none' || s.visibility === 'hidden' || Number(s.opacity) === 0) return false;
        const r = el.getClientRects();
        return r && r.length > 0;
    } catch (e) { return false; }
    }

    const candidates = [];

    function collect(root) {
    if (!root) return;

      // 1) span[part="formatted-rich-text"] (p가 있든 span 텍스트든 innerText로 다 가져옴)
    const spans = root.querySelectorAll ? root.querySelectorAll("span[part='formatted-rich-text']") : [];
    spans.forEach(sp => {
        const t = (sp.innerText || '').replace(/\u00a0/g, ' ').trim();
        if (t) candidates.push({ text: t, visible: isVisible(sp), len: t.length });
    });

      // 2) 혹시 위 selector가 안 잡히는 케이스 대비(보조)
    const rich = root.querySelectorAll ? root.querySelectorAll("lightning-formatted-rich-text") : [];
    rich.forEach(rt => {
        const t = (rt.innerText || '').replace(/\u00a0/g, ' ').trim();
        if (t) candidates.push({ text: t, visible: isVisible(rt), len: t.length });
    });

    const all = root.querySelectorAll ? root.querySelectorAll('*') : [];
    for (const el of all) {
        if (el.shadowRoot) collect(el.shadowRoot);
    }
    }

    if (container.shadowRoot) collect(container.shadowRoot);
    collect(container);

    return [question, candidates];
    """
    q, cand = driver.execute_script(js, btn)
    return (q or "").strip(), (cand or [])

# DB 저장
def make_hash(brand: str, category: str | None, question: str) -> str:
    base = f"{brand}|{category or ''}|{question}".strip()
    return hashlib.sha256(base.encode("utf-8")).hexdigest()

def save_faq(cur, brand: str, category: str | None, question: str, answer: str) -> bool:
    # 테이블이 question VARCHAR(100)라서 초과하면 저장 실패 가능 → 안전하게 자름
    q_db = (question or "").strip()
    if len(q_db) > 100:
        q_db = q_db[:100]

    a_db = (answer or "").strip()
    if not q_db or not a_db:
        return False

    uniq_hash = make_hash(brand, category, q_db)

    sql = """
    INSERT INTO faq (brand, category, question, answer, uniq_hash)
    VALUES (%s, %s, %s, %s, %s)
    ON DUPLICATE KEY UPDATE
    answer = VALUES(answer),
    updated_at = CURRENT_TIMESTAMP
    """
    cur.execute(sql, (brand, category, q_db, a_db, uniq_hash))
    return True

# 1) 도움말 더 보기 끝까지 클릭
load_clicks = click_loadmore_until_end(max_clicks=10)
total = len(deep_find_css(QUESTION_SEL))
print(f"\n 로드 완료: 질문 개수 = {total} (load more 클릭 {load_clicks}회)\n")

# DB 연결(한 번만)
conn = mysql.connector.connect(**DB)
conn.autocommit = False
cur = conn.cursor()

saved_count = 0
skipped_count = 0

try:
    # 2) 첫 질문부터 끝까지: "제목 클릭(확장) → 본문 후보 수집 → 면책 제거 → 가장 긴 본문 선택 → 출력/저장"
    for idx in range(total):
        btns = deep_find_css(QUESTION_SEL)
        if idx >= len(btns):
            break

        btn = btns[idx]

        # 무조건 클릭해서 확장
        safe_click(btn)
        try:
            WebDriverWait(driver, 10).until(
                lambda d: (btn.get_attribute("aria-expanded") or "").lower() == "true"
            )
        except Exception:
            pass

        # 후보 텍스트가 확장된 값으로 바뀔 시간을 주고 몇 번 재시도
        question = ""
        best_answer = ""

        for _ in range(8):
            question, candidates = extract_qa(btn)

            # candidates에서 (면책 제거한 뒤) 가장 긴 답변 선택
            best = ""
            for c in candidates:
                txt = c.get("text", "")
                txt = normalize_text(txt)
                txt = strip_disclaimer(txt)
                txt = normalize_text(txt)
                if len(txt) > len(best):
                    best = txt

            # '...' 요약본이면 더 기다렸다가 다시
            if best and not (best.endswith("...") or best.endswith("…")):
                best_answer = best
                break

            best_answer = best
            time.sleep(0.5)

        question = normalize_text(question)
        answer = normalize_text(best_answer)
        answer = strip_disclaimer(answer)
        answer = normalize_text(answer)

        print(f"[{idx+1}/{total}] Q: {question}")
        print(f"A: {answer}\n{'-'*80}\n")

        # DB 저장
        try:
            ok = save_faq(cur, brand="BMW", category=None, question=question, answer=answer)
            if ok:
                conn.commit()
                saved_count += 1
            else:
                skipped_count += 1
        except Exception as e:
            conn.rollback()
            skipped_count += 1
            print(f" DB 저장 실패(롤백): {e}\n")

finally:
    cur.close()
    conn.close()
    # driver.quit()

print(f" 전체 FAQ 완료! 저장 성공: {saved_count} / 스킵(빈답변·실패): {skipped_count}")
