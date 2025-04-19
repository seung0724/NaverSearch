
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from dotenv import load_dotenv
import os
import requests
import openai
from urllib.parse import urlparse

load_dotenv()

app = FastAPI(
    title="NaverSearch Hybrid API",
    description="KRX + 키움증권 API 하이브리드 기반의 종합 주식 분석 서비스",
    version="1.0.0",
    servers=[{"url": "https://naversearch.onrender.com"}]
)

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
NAVER_CLIENT_ID = os.getenv("NAVER_CLIENT_ID")
NAVER_CLIENT_SECRET = os.getenv("NAVER_CLIENT_SECRET")
KRX_API_KEY = os.getenv("KRX_API_KEY")
KIWOOM_APPKEY = os.getenv("KIWOOM_APPKEY")
KIWOOM_SECRETKEY = os.getenv("KIWOOM_SECRETKEY")

openai.api_key = OPENAI_API_KEY

class StockQuery(BaseModel):
    symbol: str
    date: str

class BlogRequest(BaseModel):
    topic: str

class SEORequest(BaseModel):
    url: str

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
    headers = {
        "Content-Type": "application/json",
        "authorization": f"Bearer {KRX_API_KEY}"
    }
    body = {"basDd": query.date, "isuCd": query.symbol}
    try:
        response = requests.post(url, headers=headers, json=body)
        response.raise_for_status()
        return response.json()
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"KRX API 오류: {e}")

@app.get("/gold_price")
async def get_gold_price():
    gold_price_1g = 87500
    gold_price_1don = round(gold_price_1g * 3.75)
    return {
        "gold_1g": f"{gold_price_1g}원",
        "gold_1don": f"{gold_price_1don}원"
    }

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
            "소제목도 적절히 넣고, 문단은 자연스럽게 나눠줘."
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

@app.post("/seo_score")
async def seo_score(data: SEORequest):
    def is_valid_url(url):
        parsed = urlparse(url)
        return parsed.scheme in ("http", "https") and parsed.netloc

    if not is_valid_url(data.url):
        raise HTTPException(status_code=400, detail="유효하지 않은 URL입니다.")

    try:
        html = requests.get(data.url, timeout=5).text
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"URL 요청 실패: {str(e)}")

    seo_prompt = (
        "아래 HTML은 사용자가 입력한 웹페이지입니다.\n"
        "네이버 웹마스터 가이드에 따라 SEO 요소들을 점검하고, 다음 항목들을 포함해 평가해줘:\n"
        "1. 전체 SEO 점수 (100점 만점 기준)\n"
        "2. 개선이 필요한 요소 리스트 (meta 태그, 제목, OpenGraph, robots.txt 등)\n"
        "3. 전반적인 요약\n"
        f"아래는 HTML입니다:\n```html\n{html[:3000]}\n```"
    )

    try:
        response = openai.chat.completions.create(
            model="gpt-4",
            messages=[{"role": "user", "content": seo_prompt}],
            max_tokens=800
        )
        result = response.choices[0].message.content.strip()
        return {"seo_analysis": result}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"GPT 분석 실패: {e}")

@app.get("/kiwoom_token")
def get_kiwoom_token():
    url = "https://openapi.koreainvestment.com:9443/oauth2/tokenP"
    headers = {"Content-Type": "application/json"}
    data = {
        "grant_type": "client_credentials",
        "appkey": KIWOOM_APPKEY,
        "appsecret": KIWOOM_SECRETKEY
    }
    try:
        response = requests.post(url, json=data, headers=headers)
        return response.json()
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"키움 토큰 발급 실패: {e}")
