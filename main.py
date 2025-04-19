from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from dotenv import load_dotenv
import os
import requests
import openai

# ✅ 환경 변수 로딩
load_dotenv()
app = FastAPI()

# ✅ API 키 설정
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
NAVER_CLIENT_ID = os.getenv("NAVER_CLIENT_ID")
NAVER_CLIENT_SECRET = os.getenv("NAVER_CLIENT_SECRET")
KRX_API_KEY = os.getenv("KRX_API_KEY")

openai.api_key = OPENAI_API_KEY

# ✅ 공통 요청 모델 정의
class StockQuery(BaseModel):
    symbol: str
    date: str

class BlogRequest(BaseModel):
    topic: str

# ✅ 주식 정보 조회 (유가/코스닥 자동 감지)
def get_market_type(isuCd: str) -> str:
    url = "http://data-dbg.krx.co.kr/svc/apis/sto/stk_isu_base_info"
    headers = {"Content-Type": "application/json"}
    body = {"mktsel": "ALL", "isuCd": isuCd}
    try:
        response = requests.post(url, headers=headers, json=body)
        data = response.json()
        for item in data.get("OutBlock_1", []):
            if item["isuCd"] == isuCd:
                return "kosdaq" if item["mktNm"] == "KOSDAQ" else "kospi"
    except:
        pass
    return "kospi"

@app.post("/stock_info")
async def get_stock_info(query: StockQuery):
    market = get_market_type(query.symbol)
    url = (
        "https://data-dbg.krx.co.kr/svc/apis/sto/ksq_bydd_trd"
        if market == "kosdaq"
        else "https://data-dbg.krx.co.kr/svc/apis/sto/stk_bydd_trd"
    )
    headers = {"Content-Type": "application/json"}
    body = {"basDd": query.date, "isuCd": query.symbol}
    try:
        response = requests.post(url, headers=headers, json=body)
        return response.json()
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"KRX API 오류: {e}")

# ✅ 금 시세 조회 (샘플)
@app.get("/gold_price")
async def get_gold_price():
    gold_price_1g = 87500
    gold_price_1don = round(gold_price_1g * 3.75)
    return {
        "gold_1g": f"{gold_price_1g}원",
        "gold_1don": f"{gold_price_1don}원"
    }

# ✅ GPT-4 주식 분석
@app.post("/stock_analysis")
async def analyze_stock(query: StockQuery):
    try:
        gpt_prompt = (
            f"{query.date} 기준으로 종목 코드 {query.symbol}에 대한 "
            "주식 시장 분석과 투자 유의사항을 알려줘."
        )
        response = openai.chat.completions.create(
            model="gpt-4",
            messages=[{"role": "user", "content": gpt_prompt}],
            max_tokens=500
        )
        result = response.choices[0].message.content.strip()
        return {"analysis": result}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"GPT 오류: {e}")

@app.post("/generate_post")
async def generate_post(data: BlogRequest):
    try:
        prompt = (
            f"'{data.topic}'이라는 주제로 블로그 글을 작성해줘. "
            "서론, 본론, 결론 구조로 나누고, 친근하면서도 정보성 있게 써줘. "
            "소제목도 적절히 넣고, 문단은 자연스럽게 나눠줘. 마치 블로거가 쓴 글처럼."
        )
        response = openai.chat.completions.create(
            model="gpt-4",
            messages=[{"role": "user", "content": prompt}],
            max_tokens=1200
        )
        content = response.choices[0].message.content.strip()
        return {"topic": data.topic, "blog_content": content}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"GPT 오류: {e}")
