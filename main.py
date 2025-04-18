from fastapi import FastAPI
from pydantic import BaseModel
import openai

app = FastAPI()

# OpenAI API 키 설정
openai.api_key = "sk-your-api-key-here"  # 여기에 OpenAI API 키를 입력하세요.

# 데이터 모델 정의 (사용자가 보내는 쿼리)
class AnalyzeRequest(BaseModel):
    query: str

# POST 엔드포인트: 사용자의 쿼리 분석
@app.post("/analyze_data")
async def analyze_data(data: AnalyzeRequest):
    # OpenAI GPT 모델을 사용하여 쿼리 분석
    response = openai.Completion.create(
        engine="text-davinci-003",
        prompt=data.query,
        max_tokens=200,
        temperature=0.7
    )

    # 분석된 결과 반환
    return {"analysis_result": response.choices[0].text.strip()}

# 서버 실행
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
