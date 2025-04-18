import requests
import time

# API 주소
url = "http://127.0.0.1/analyzeData"

# 반복적으로 보낼 데이터 (예시)
payload = {
    "text": "자동화된 테스트 데이터입니다"
}

# 자동 반복 횟수
repeat_count = 5
delay_seconds = 2  # 호출 간 딜레이 (초)

for i in range(repeat_count):
    try:
        print(f"[{i+1}] analyzeData 호출 중...")
        response = requests.post(url, json=payload)
        print("응답 코드:", response.status_code)
        print("응답 내용:", response.json())
    except requests.exceptions.RequestException as e:
        print("오류 발생:", e)

    time.sleep(delay_seconds)
