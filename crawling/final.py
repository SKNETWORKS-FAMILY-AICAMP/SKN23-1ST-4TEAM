from selenium import webdriver
from selenium.webdriver.common.by import By
import time
import mysql.connector

# 1️⃣ MySQL 연결
conn = mysql.connector.connect(
    host="127.0.0.1",
    user="admin",
    password="vmfhwprxm",  # MySQL 비밀번호
    database="SKN23"
)
cursor = conn.cursor()

# 2️⃣ 크롬 드라이버 실행
driver = webdriver.Chrome()
driver.get("https://www.mercedes-benz.co.kr/passengercars/buy/mbmk/help/help-faq.html")

# 3️⃣ 페이지 로딩 대기
time.sleep(5)

# 4️⃣ 쿠키 '전체 동의' 클릭 (JS 클릭)
driver.execute_script("""
let btns = document.querySelectorAll('button');
for(let btn of btns){
    if(btn.innerText.trim() === '전체 동의'){
        btn.click();
        break;
    }
}
""")
print("쿠키 '전체 동의' 클릭 완료")
time.sleep(2)

# 5️⃣ 모든 FAQ 항목 가져오기
faqs = driver.find_elements(By.CSS_SELECTOR, ".wb-accordion-item.hydrated")
print(f"총 FAQ 항목 수: {len(faqs)}")

# 6️⃣ FAQ 반복
for faq in faqs:
    # 질문(header 태그)
    try:
        question = faq.find_element(By.TAG_NAME, "header").text
    except:
        question = ""
    
    # '더보기' 버튼 클릭(div.toggle)
    try:
        more_btn = faq.find_element(By.CSS_SELECTOR, "div.toggle")
        driver.execute_script("arguments[0].click();", more_btn)
        time.sleep(0.2)
    except:
        pass
    
    # 답변 내용 (FAQ 블록 내부 전체 텍스트)
    try:
        answer = faq.text.replace(question, "").strip()  # 질문 제외하고 답변만
    except:
        answer = ""
    
    print(f"질문: {question}")
    print(f"답변: {answer}\n---")

    # 7️⃣ MySQL에 저장
    cursor.execute(
        "INSERT INTO mercedes_faq (question, answer) VALUES (%s, %s)",
        (question, answer)
    )

# 8️⃣ 커밋 후 종료
conn.commit()
cursor.close()
conn.close()
driver.quit()
print("FAQ 크롤링 완료! MySQL에 저장됨.")
