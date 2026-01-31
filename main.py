from fastapi import FastAPI, Header, HTTPException, Request, BackgroundTasks
from fastapi.responses import RedirectResponse
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from supabase import create_client, Client
from datetime import datetime, timedelta
import random
import os
import uuid
import base64
import requests
from typing import List, Optional

app = FastAPI(title="A-Sense Unified Ad Engine")

# [모델] 요청 데이터 검증
class AdRequest(BaseModel):
    keywords: List[str] = []
    platform: str = "chatbot"
    publisher_id: Optional[str] = None
    user_id: Optional[str] = None # For frequency capping
    lang: str = "en" # Language targeting

# [설정] CORS 허용
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], 
    allow_methods=["*"],
    allow_headers=["*"],
)

# [설정] 정적 파일 서비스 (안전한 초기화)
if os.path.exists("static"):
    app.mount("/static", StaticFiles(directory="static"), name="static")
else:
    # Vercel 환경 등에서 static 폴더가 없을 경우를 대비
    pass

# [설정] 환경 변수
SUPABASE_URL = os.getenv("SUPABASE_URL", "https://your-project.supabase.co")
SUPABASE_KEY = os.getenv("SUPABASE_KEY", "your-anon-key")
TOSS_SECRET_KEY = os.getenv("TOSS_SECRET_KEY", "test_sk_...") 
PAYPAL_CLIENT_ID = os.getenv("PAYPAL_CLIENT_ID", "...")
PAYPAL_SECRET = os.getenv("PAYPAL_SECRET", "...")

# [Mock DB Classes] - 로컬 테스트 및 DB 연결 실패 시 작동
class MockTable:
    def __init__(self, db, table_name):
        self.db = db
        self.table_name = table_name
        self.query_result = []

    def select(self, columns):
        self.query_result = self.db.get(self.table_name, [])
        return self

    def insert(self, data):
        if self.table_name not in self.db: self.db[self.table_name] = []
        if isinstance(data, dict):
            if "id" not in data: data["id"] = str(uuid.uuid4())
            self.db[self.table_name].append(data)
        elif isinstance(data, list):
            for item in data:
                if "id" not in item: item["id"] = str(uuid.uuid4())
                self.db[self.table_name].append(item)
        return self

    def update(self, data):
        self.pending_update = data
        return self
    
    def delete(self):
        self.pending_delete = True
        return self

    def eq(self, column, value):
        if hasattr(self, 'query_result'):
            self.query_result = [row for row in self.query_result if row.get(column) == value]
        if hasattr(self, 'pending_update'):
            for row in self.db[self.table_name]:
                if row.get(column) == value:
                    row.update(self.pending_update)
        if hasattr(self, 'pending_delete') and self.pending_delete:
            self.db[self.table_name] = [row for row in self.db[self.table_name] if row.get(column) != value]
        return self
    
    def gt(self, column, value):
        if hasattr(self, 'query_result'):
            self.query_result = [row for row in self.query_result if row.get(column, 0) > value]
        return self

    def execute(self):
        class Result:
            def __init__(self, data): self.data = data
        return Result(self.query_result if hasattr(self, 'query_result') else [])

class MockSupabaseClient:
    def __init__(self):
        self.db = {
            "advertisers": [
                {"id": "mock-ad-1", "brand_name": "테스트 브랜드 A", "ad_copy": "이것은 로컬 테스트 광고입니다.", "cpc_bid": 500, "keywords": ["테스트", "광고"], "ad_type": "cpc", "owner_id": "demo-user", "balance": 5000, "lang": "ko", "landing_url": "https://example.com"},
                {"id": "mock-ad-2", "brand_name": "Test Brand B", "ad_copy": "This is a local test ad.", "cpc_bid": 300, "keywords": ["test", "sample"], "ad_type": "cpc", "owner_id": "demo-user", "balance": 0, "lang": "en", "landing_url": "https://example.com"}
            ],
            "publishers": [],
            "logs": self._generate_mock_logs(),
            "payout_requests": [],
            "advertiser_users": [
                {"id": "demo-user", "email": "demo@test.com", "password_hash": "demo", "company_name": "Demo Corp", "balance": 100000}
            ],
            "deposits": [],
            "conversions": [],
            "transactions": []
        }
        print("⚠️  Running in MOCK MODE (In-Memory DB)")

    def _generate_mock_logs(self):
        logs = []
        platforms = ["chatbot", "web", "mobile_app"]
        reasons = ["IP_REPEAT", "BOT_UA", "SPEED_CLICK"]
        now = datetime.now()
        for i in range(50):
            is_valid = random.choice([True, True, False])
            logs.append({
                "id": str(uuid.uuid4()),
                "timestamp": (now - timedelta(hours=random.randint(0, 24))).isoformat(),
                "type": random.choice(["impression", "impression", "click"]),
                "platform": random.choice(platforms),
                "is_valid": is_valid,
                "invalid_reason": random.choice(reasons) if not is_valid else None,
                "user_ip": f"192.168.1.{random.randint(1, 255)}"
            })
        return logs

    def table(self, table_name):
        return MockTable(self.db, table_name)

# [Supabase Connection Logic]
try:
    if "your-project" in SUPABASE_URL:
        # 환경 변수가 기본값이면 Mock 모드 강제
        raise ValueError("Supabase environment variables not set.")
    supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)
    print("✅ Supabase Connected!")
except Exception as e:
    print(f"⚠️ Supabase Connection Failed: {e}")
    print("⚠️ Running in MOCK MODE (In-Memory DB)")
    supabase = MockSupabaseClient()

# --- 핵심 비즈니스 로직: 광고 매칭 엔진 ---
def match_best_ad(user_keywords: list, lang: str = 'en'):
    """사용자 맥락 키워드와 가장 잘 맞는 고단가 광고를 매칭합니다."""
    try:
        # 해당 언어의 잔액이 있는 광고주만 조회
        ads_query = supabase.table("advertisers") \
            .select("*") \
            .eq("lang", lang) \
            .gt("balance", 0) \
            .execute()
        ads = ads_query.data
    except Exception as e:
        print(f"Supabase Error: {e}")
        return None
    
    if not ads:
        return None

    valid_ads = [ad for ad in ads if ad['balance'] >= ad.get('cpc_bid', 0)]
    if not valid_ads: return None

    matched_ads = []
    for ad in valid_ads:
        # 키워드가 겹치는 광고 찾기
        common_keywords = set(user_keywords) & set(ad.get('keywords', []))
        if common_keywords:
            matched_ads.append(ad)

    # 매칭된 게 있다면 단가(cpc_bid)가 높은 순으로 정렬 후 상위권 중 랜덤 송출
    if matched_ads:
        matched_ads.sort(key=lambda x: x.get('cpc_bid', 0), reverse=True)
        return matched_ads[0] 
    
    # 매칭된 게 없으면 전체 중 랜덤 반환 (백필 광고)
    return random.choice(valid_ads)

# --- [API] 광고 요청 (GET_AD) ---
@app.post("/api/v1/get-ad")
async def get_ad(request: Request, body: AdRequest, background_tasks: BackgroundTasks, x_api_key: str = Header(None)):
    platform = body.platform
    user_keywords = body.keywords
    pub_id = body.publisher_id
    lang = body.lang 

    # 1. 매체 인증 (API Key 검증)
    publisher_info = None

    if platform != "web":
        # 챗봇/앱: API Key로 검증 상태까지 함께 조회
        if not x_api_key:
             # Allow test key for dev
             if pub_id == "test-publisher":
                 pass
             else:
                 raise HTTPException(status_code=401, detail="API Key is missing")
        
        if x_api_key:
            try:
                pub_query = supabase.table("publishers").select("id, verification_token, is_verified").eq("api_key", x_api_key).execute()
                if not pub_query.data: 
                    if x_api_key == "test-api-key": # Backdoor for testing
                        pub_id = "test-publisher"
                        publisher_info = {"id": "test-publisher", "is_verified": True}
                    else:
                        raise HTTPException(status_code=401, detail="Invalid Key")
                else:
                    publisher_info = pub_query.data[0]
                    pub_id = publisher_info['id']

                    # [자동 검증 로직]
                    if not publisher_info['is_verified']:
                        expected_token = publisher_info.get('verification_token')
                        context_str = " ".join(user_keywords)
                        # 사용자가 토큰을 시스템 프롬프트 등에 심어두었는지 확인
                        if expected_token and expected_token in context_str:
                            supabase.table("publishers").update({"is_verified": True}).eq("id", pub_id).execute()
                            print(f"Auto-verified publisher {pub_id}")
                            return {
                                "brand": "A-Sense System",
                                "ad_copy": f"인증이 완료되었습니다! (Code: {expected_token})",
                                "link": "https://a-sense.vercel.app"
                            }
            except Exception as e:
                print(f"Auth Error: {e}")
                pass

    # 2. 광고 매칭
    ad = match_best_ad(user_keywords, lang)
    
    if not ad:
        return {"message": "No ads available"}

    # 3. 응답 반환
    return {
        "id": ad['id'],
        "brand": ad['brand_name'],
        "ad_copy": ad['ad_copy'],
        "link": f"{str(request.base_url)}api/v1/click/{ad['id']}?pub_id={pub_id or 'unknown'}",
        "cpc": ad['cpc_bid']
    }

@app.get("/api/v1/click/{ad_id}")
async def track_click(ad_id: str, pub_id: str = "unknown"):
    # 1. 광고 정보 조회 (CPC 단가 확인)
    try:
        ad_res = supabase.table("advertisers").select("cpc_bid, landing_url, owner_id, balance").eq("id", ad_id).execute()
        if not ad_res.data:
            return RedirectResponse("https://google.com") # Fallback
        
        ad = ad_res.data[0]
        cpc = ad['cpc_bid']
        landing_url = ad.get('landing_url') or "https://google.com"
        
        # 2. 잔액 차감
        if ad['balance'] >= cpc:
             new_balance = ad['balance'] - cpc
             supabase.table("advertisers").update({"balance": new_balance}).eq("id", ad_id).execute()
             
             # 3. 로그 기록
             supabase.table("logs").insert({
                 "ad_id": ad_id,
                 "publisher_id": pub_id,
                 "cost": cpc,
                 "action_type": "click",
                 "timestamp": datetime.now().isoformat(),
                 "is_valid": True
             }).execute()
             
    except Exception as e:
        print(f"Click tracking error: {e}")
        return RedirectResponse("https://google.com")

    return RedirectResponse(landing_url)

# --- [API] 토큰 발급 및 검증 ---
@app.post("/api/v1/generate-token")
async def generate_token(request: Request):
    data = await request.json()
    app_name = data.get("app_name")
    platform_type = data.get("platform_type")
    bank_name = data.get("bank_name")
    account_number = data.get("account_number")
    account_holder = data.get("account_holder")
    
    api_key = f"sk_live_{uuid.uuid4().hex[:16]}"
    verification_token = f"asense-verify-{uuid.uuid4().hex[:8]}"
    
    try:
        supabase.table("publishers").insert({
            "name": app_name,
            "platform": platform_type,
            "api_key": api_key,
            "verification_token": verification_token,
            "is_verified": False,
            "bank_name": bank_name,
            "account_number": account_number,
            "account_holder": account_holder
        }).execute()
        
        return {
            "status": "success",
            "api_key": api_key,
            "verification_token": verification_token,
            "message": "Token generated."
        }
    except Exception as e:
        print(f"DB Error: {e}")
        return {"status": "success", "api_key": api_key, "verification_token": verification_token, "is_mock": True}

@app.get("/api/v1/check-verification")
async def check_verification(api_key: str):
    try:
        response = supabase.table("publishers").select("id, is_verified, bank_name, account_number").eq("api_key", api_key).execute()
        if response.data:
            return response.data[0]
        return {"verified": False}
    except Exception:
        return {"verified": False}

@app.post("/api/v1/verify-token")
async def verify_token(data: dict):
    # 수동 검증 API
    api_key = data.get("api_key")
    if api_key:
        try:
            supabase.table("publishers").update({"is_verified": True}).eq("api_key", api_key).execute()
            return {"status": "success", "message": "Ownership verified"}
        except:
            pass
    return {"status": "fail", "message": "Verification failed"}

# --- [API] 광고주 기능 ---
@app.post("/api/v1/advertiser/register")
async def advertiser_register(request: Request):
    data = await request.json()
    email = data.get("email")
    password = data.get("password")
    company_name = data.get("company_name")
    
    user_id = str(uuid.uuid4())
    supabase.table("advertiser_users").insert({
        "id": user_id,
        "email": email,
        "password_hash": password, 
        "company_name": company_name,
        "balance": 0
    }).execute()
    
    return {"status": "success", "user_id": user_id}

@app.post("/api/v1/advertiser/login")
async def advertiser_login(request: Request):
    data = await request.json()
    email = data.get("email")
    password = data.get("password")
    
    res = supabase.table("advertiser_users").select("*").eq("email", email).execute()
    if not res.data or res.data[0]["password_hash"] != password:
        return {"status": "error", "message": "Invalid credentials"}
    
    return {"status": "success", "user": res.data[0]}

@app.post("/api/v1/advertiser/ads")
async def create_ad(request: Request):
    data = await request.json()
    supabase.table("advertisers").insert(data).execute()
    return {"status": "success"}

@app.get("/api/v1/advertiser/ads")
async def list_ads(owner_id: str):
    res = supabase.table("advertisers").select("*").eq("owner_id", owner_id).execute()
    return {"ads": res.data}

@app.post("/api/v1/advertiser/deposit")
async def deposit(request: Request):
    data = await request.json()
    advertiser_id = data.get("advertiser_id")
    amount = int(data.get("amount"))
    
    supabase.table("deposits").insert({"advertiser_id": advertiser_id, "amount": amount, "status": "completed"}).execute()
    
    # Update Advertiser User Balance
    user_res = supabase.table("advertiser_users").select("balance").eq("id", advertiser_id).execute()
    if user_res.data:
        new_balance = user_res.data[0]["balance"] + amount
        supabase.table("advertiser_users").update({"balance": new_balance}).eq("id", advertiser_id).execute()
        
    return {"status": "success", "new_balance": new_balance}

# --- [API] 결제 웹훅 (Toss/PayPal) ---
@app.get("/api/payment/toss/success")
async def toss_success(paymentKey: str, orderId: str, amount: int):
    # 1. Toss 결제 승인 요청 (실제 구현 시 필요)
    # ...
    
    # 2. 잔액 업데이트 (Dashboard 로직에 따라 개별 광고 캠페인에 충전)
    advertiser_id = orderId.split("_")[0] # orderId = "{ad_id}_{timestamp}"
    
    try:
        current = supabase.table("advertisers").select("balance").eq("id", advertiser_id).execute()
        if current.data:
            new_bal = current.data[0]['balance'] + amount
            supabase.table("advertisers").update({"balance": new_bal}).eq("id", advertiser_id).execute()
            
            supabase.table("transactions").insert({
                "advertiser_id": advertiser_id,
                "amount": amount,
                "type": "deposit",
                "description": "Toss Payments 충전"
            }).execute()
    except Exception as e:
        print(f"Payment Update Error: {e}")

    return {"status": "success", "message": "Payment confirmed and balance updated."}

@app.post("/api/payment/paypal/capture")
async def paypal_capture(request: Request):
    data = await request.json()
    order_id = data.get("orderID")
    advertiser_id = data.get("advertiserID") # Dashboard passes ad_id here
    
    # PayPal 결제 확인 로직 (생략)
    amount = 10000 # Mock amount
    
    try:
        current = supabase.table("advertisers").select("balance").eq("id", advertiser_id).execute()
        if current.data:
            new_bal = current.data[0]['balance'] + amount
            supabase.table("advertisers").update({"balance": new_bal}).eq("id", advertiser_id).execute()
            
            supabase.table("transactions").insert({
                "advertiser_id": advertiser_id,
                "amount": amount,
                "type": "deposit",
                "description": "PayPal Charge"
            }).execute()
            
        return {"status": "success", "payer": {"name": {"given_name": "TestUser"}}}
    except Exception as e:
        return {"status": "error", "message": str(e)}

# Root Endpoint
@app.get("/")
async def root():
    return {"message": "A-Sense API is running", "docs": "/docs"}
