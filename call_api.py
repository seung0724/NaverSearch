import requests

url = "http://127.0.0.1:8000/analyzeData"

payload = {
    "text": "이건 자동 호출 테스트입니다!"
}

try:
    response = requests.post(url, json=payload)
    print("✅ 응답 코드:", response.status_code)
    print("📦 응답 데이터:", response.json())
except requests.exceptions.RequestException as e:
    print("❌ API 호출 중 오류:", e)
