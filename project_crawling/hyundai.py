from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
import csv

driver = webdriver.Chrome()
driver.get("https://www.hyundai.com/kr/ko/faq.html")

wait = WebDriverWait(driver, 10)

with open("hyundai_faq.csv", mode="w", newline="", encoding="utf-8-sig") as file:
    writer = csv.writer(file)
    writer.writerow(["질문", "답변"])

    # 1~5페이지
    for page in range(1, 6):

        # 페이지 이동
        if page > 1:
            try:
                btn = wait.until(
                    EC.element_to_be_clickable((By.CSS_SELECTOR, f'[title="{page} 페이지 이동"]'))
                )
                driver.execute_script("arguments[0].click();", btn)
                time.sleep(2)
            except:
                print(f"{page}페이지 이동 실패")

        # dl 리스트 가져오기
        dls = driver.find_elements(By.TAG_NAME, "dl")
        print(f"{page}페이지 dl 개수: {len(dls)}")

        for dl in dls:

            # 질문이 있는 dl만 처리
            try:
                question_tag = dl.find_element(By.CLASS_NAME, "brief")
                question = question_tag.text.strip()
            except:
                continue  # brief 없으면 FAQ 아님 → 스킵

            # 더보기 버튼 클릭
            try:
                more_btn = dl.find_element(By.CLASS_NAME, "more")
                driver.execute_script("arguments[0].click();", more_btn)

                # exp가 열릴 때까지 대기(핵심)
                exp_tag = wait.until(
                    EC.visibility_of_element_located(
                        (By.CSS_SELECTOR, "dd.exp")
                    )
                )
                time.sleep(0.2)

                answer = exp_tag.text.strip()
            except:
                answer = ""

            # 출력
            print(f"질문: {question}")
            print(f"답변: {answer}\n---")

            # CSV 저장
            writer.writerow([question, answer])

print("크롤링 완료!")
driver.quit()
