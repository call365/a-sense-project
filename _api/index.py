from fastapi import FastAPI, Header, HTTPException, Request, BackgroundTasks, Response, Depends
from fastapi.responses import RedirectResponse, FileResponse, HTMLResponse, JSONResponse, PlainTextResponse
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from fastapi.openapi.utils import get_openapi
from pydantic import BaseModel
from supabase import create_client, Client
from datetime import datetime, timedelta
import random
import os
import uuid
import base64
import requests
import httpx
from typing import List, Optional, Dict, Any
from urllib.parse import urlparse

app = FastAPI(title="A-Sense Unified Ad Engine")
_coze_openapi_cache = None

# [Health Check]
@app.get("/api/health")
async def health_check():
    try:
        # Supabase를 실제로 깨우기 위한 초경량 쿼리
        supabase.table("publishers").select("id").limit(1).execute()
        return JSONResponse(content={
            "status": "alive",
            "message": "Supabase DB가 무사히 깨어있습니다! ☀️",
            "timestamp": datetime.now().isoformat(),
        })
    except Exception as e:
        return JSONResponse(content={
            "status": "error",
            "message": str(e),
            "timestamp": datetime.now().isoformat(),
        })


@app.get("/api/v1/health-check")
async def health_check_v1():
    return await health_check()


@app.get("/robots.txt", response_class=PlainTextResponse)
async def robots_txt():
    domain = "https://asense.nextfintechai.com"
    content = f"""User-agent: *
Allow: /
Disallow: /api/
Disallow: /static/

Sitemap: {domain}/sitemap.xml
"""
    return content


@app.get("/sitemap.xml")
async def sitemap_xml():
    domain = "https://asense.nextfintechai.com"
    today = datetime.now().strftime("%Y-%m-%d")
    paths = [
        "/",
        "/home",
        "/home_ko",
        "/about",
        "/docs",
        "/partners",
        "/success_stories",
        "/support",
        "/terms",
        "/privacy",
        "/payment",
        "/dashboard",
        "/advertiser_center",
        "/advertiser_auth",
        "/advertiser_dashboard",
        "/register",
        "/register_publisher",
        "/register_advertiser",
        "/sales_landing",
    ]
    urls = "\n".join(
        f"""  <url>
    <loc>{domain}{path}</loc>
    <lastmod>{today}</lastmod>
    <changefreq>weekly</changefreq>
    <priority>0.7</priority>
  </url>"""
        for path in paths
    )
    sitemap_content = f"""<?xml version="1.0" encoding="UTF-8"?>
<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">
{urls}
</urlset>"""
    return Response(content=sitemap_content, media_type="application/xml")

# [Config] 공개 키 제공 (Toss, PayPal)
@app.get("/api/config/public-keys")
async def get_public_keys():
    return JSONResponse(content={
        "toss_client_key": os.environ.get("TOSS_CLIENT_KEY", "live_ck_GKNbdOvk5rkdPyao0eA8n07xlzmj"),
        "paypal_client_id": os.environ.get("PAYPAL_CLIENT_ID", "sb")
    })

def _resolve_static_path(filename: str) -> str:
    base_dir = os.path.dirname(os.path.abspath(__file__))
    absolute_path = os.path.join(base_dir, "..", "static", filename)
    if os.path.exists(absolute_path):
        return absolute_path
    fallback_path = os.path.join("static", filename)
    return fallback_path


def _is_korean_preferred(accept_language: Optional[str]) -> bool:
    if not accept_language:
        return False
    lowered = accept_language.lower()
    tokens = [part.split(";")[0].strip() for part in lowered.split(",") if part.strip()]
    return any(token.startswith("ko") for token in tokens)


# [Root] 언어 기반 301 리다이렉트 (SEO 중복 페이지 방지)
@app.get("/")
async def read_root(request: Request):
    target = "/home_ko" if _is_korean_preferred(request.headers.get("accept-language")) else "/home"
    return RedirectResponse(url=target, status_code=301, headers={"Cache-Control": "no-store"})


@app.get("/home")
async def home():
    file_path = _resolve_static_path("home.html")
    if not os.path.exists(file_path):
        return JSONResponse(status_code=404, content={"error": "home.html not found"})
    return FileResponse(file_path, media_type="text/html", headers={"Cache-Control": "no-cache, no-store, must-revalidate"})


@app.get("/home_ko")
async def home_ko():
    file_path = _resolve_static_path("home_ko.html")
    if not os.path.exists(file_path):
        return JSONResponse(status_code=404, content={"error": "home_ko.html not found"})
    return FileResponse(file_path, media_type="text/html", headers={"Cache-Control": "no-cache, no-store, must-revalidate"})


@app.get("/home_en")
async def home_en():
    return RedirectResponse(url="/home", status_code=301, headers={"Cache-Control": "no-store"})


@app.get("/home.html")
async def legacy_home_html():
    return RedirectResponse(url="/home", status_code=301, headers={"Cache-Control": "no-store"})


@app.get("/home_ko.html")
async def legacy_home_ko_html():
    return RedirectResponse(url="/home_ko", status_code=301, headers={"Cache-Control": "no-store"})


@app.get("/home_en.html")
async def legacy_home_en_html():
    return RedirectResponse(url="/home", status_code=301, headers={"Cache-Control": "no-store"})


# [Google Verification] 동적 파일 인증 (모든 google*.html 처리)
@app.get("/google02e167ec2d7812c3.html")
async def explicit_verification():
    return PlainTextResponse("google-site-verification: google02e167ec2d7812c3.html")

@app.get("/{filename}")
async def dynamic_verification(filename: str):
    if filename.startswith("google") and filename.endswith(".html"):
        return PlainTextResponse(f"google-site-verification: {filename}")
    
    # [Fallback] 정적 파일 폴백 처리
    # Vercel Rewrites로 인해 API로 넘어온 정적 파일 요청 처리
    file_path = os.path.join(STATIC_DIR, filename)
    if os.path.exists(file_path) and os.path.isfile(file_path):
        return FileResponse(file_path)

    if not filename.endswith(".html"):
        file_path_html = os.path.join(STATIC_DIR, f"{filename}.html")
        if os.path.exists(file_path_html) and os.path.isfile(file_path_html):
            return FileResponse(file_path_html, media_type="text/html")
    
    # 다른 파일 요청은 404 처리
    return JSONResponse(status_code=404, content={"error": "File not found", "filename": filename})


# [모델] 요청 데이터 검증
class AdRequest(BaseModel):
    keywords: List[str] = []
    platform: str = "chatbot"
    publisher_id: Optional[str] = None
    user_id: Optional[str] = None # For frequency capping
    lang: str = "en" # Language targeting


class CozeAdRequest(BaseModel):
    keyword: str


class QuickSignupRequest(BaseModel):
    email: str


class DomainUpdateRequest(BaseModel):
    domain: str


class WithdrawalRequest(BaseModel):
    amount: int
    paypal_email: str

# [설정] CORS 허용
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], 
    allow_methods=["*"],
    allow_headers=["*"],
)

# [설정] 정적 파일 서비스 (안전한 초기화)
# Vercel 환경에서 경로 문제를 방지하기 위해 절대 경로 사용
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
STATIC_DIR = os.path.join(BASE_DIR, "..", "static")

if os.path.exists(STATIC_DIR):
    app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")
else:
    # 로컬이나 다른 환경을 위한 폴백
    if os.path.exists("static"):
         app.mount("/static", StaticFiles(directory="static"), name="static")

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


def _normalize_domain(url_or_domain: Optional[str]) -> str:
    if not url_or_domain:
        return ""

    raw = str(url_or_domain).strip().lower()
    if not raw:
        return ""

    parsed = urlparse(raw if "://" in raw else f"https://{raw}")
    host = (parsed.netloc or parsed.path or "").strip().lower()
    if host.startswith("www."):
        host = host[4:]
    return host


def _enforce_domain_whitelist(request: Request, registered_domain_raw: Optional[str], api_key: str):
    client_origin = request.headers.get("origin") or request.headers.get("referer")
    client_domain = _normalize_domain(client_origin)
    registered_domain = _normalize_domain(registered_domain_raw)

    # Coze 같은 S2S는 Origin/Referer가 없는 경우가 있어 허용
    if not client_domain:
        return

    # 브라우저 호출인데 등록 도메인이 없으면 차단
    if not registered_domain:
        raise HTTPException(
            status_code=403,
            detail="등록된 도메인이 없습니다. 대시보드에서 챗봇 URL을 먼저 등록해주세요."
        )

    # 엄격 일치 정책
    if client_domain != registered_domain:
        print(f"[SECURITY] Unregistered domain access: {client_origin} (key={api_key})")
        raise HTTPException(
            status_code=403,
            detail="등록되지 않은 도메인입니다. A-Sense 대시보드에서 URL 화이트리스트를 등록해주세요."
        )


async def verify_coze_api_key(request: Request, authorization: str = Header(None)) -> Dict[str, Any]:
    """Coze Plugin Bearer 인증 + 도메인 화이트리스트를 검증합니다."""
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="API 키가 누락되었거나 형식이 잘못되었습니다.")

    api_key = authorization.split("Bearer ", 1)[1].strip()
    if not api_key:
        raise HTTPException(status_code=401, detail="유효하지 않은 API 키입니다.")

    # 1) 신규 구조 우선: publisher_apps
    # 2) 레거시 호환: publishers
    try:
        app_res = supabase.table("publisher_apps").select("id, publisher_id, is_verified, app_url, web_domain, domain").eq("api_key", api_key).execute()
        if app_res.data:
            app_info = app_res.data[0]
            if app_info.get("is_verified") is False:
                raise HTTPException(status_code=403, detail="검증되지 않은 앱입니다.")

            registered_domain = app_info.get("app_url") or app_info.get("web_domain") or app_info.get("domain")
            _enforce_domain_whitelist(request, registered_domain, api_key)

            return {
                "api_key": api_key,
                "source": "publisher_apps",
                "app_id": app_info.get("id"),
                "publisher_id": app_info.get("publisher_id"),
                "registered_domain": registered_domain,
            }
    except HTTPException:
        raise
    except Exception:
        # publisher_apps 미구성 환경은 publishers로 폴백
        pass

    try:
        pub_res = supabase.table("publishers").select("id, is_verified, web_domain").eq("api_key", api_key).execute()
        if not pub_res.data:
            raise HTTPException(status_code=401, detail="유효하지 않은 API 키입니다.")

        pub_info = pub_res.data[0]
        if pub_info.get("is_verified") is False:
            raise HTTPException(status_code=403, detail="검증되지 않은 퍼블리셔입니다.")

        registered_domain = pub_info.get("web_domain")
        _enforce_domain_whitelist(request, registered_domain, api_key)

        return {
            "api_key": api_key,
            "source": "publishers",
            "publisher_id": pub_info.get("id"),
            "registered_domain": registered_domain,
        }
    except HTTPException:
        raise
    except Exception:
        raise HTTPException(status_code=401, detail="API 키 검증 중 오류가 발생했습니다.")


@app.post("/api/v1/coze/get-ad", summary="Coze Plugin Ad Generator")
async def get_coze_ad(
    payload: CozeAdRequest,
    auth_ctx: Dict[str, Any] = Depends(verify_coze_api_key)
):
    """Coze 플러그인 전용 광고 매칭 API"""
    _ = auth_ctx

    keyword = (payload.keyword or "").strip()
    if not keyword:
        return {
            "ad_found": False,
            "ad_text": "현재 일치하는 스폰서 정보가 없습니다.",
            "ad_link": ""
        }

    # Coze 요청은 단일 키워드 기반으로 단순 매칭
    lang = "ko" if any('\uac00' <= ch <= '\ud7a3' for ch in keyword) else "en"
    matched_ad = match_best_ad([keyword], lang=lang)

    if not matched_ad:
        return {
            "ad_found": False,
            "ad_text": "현재 일치하는 스폰서 정보가 없습니다.",
            "ad_link": ""
        }

    brand_name = matched_ad.get('brand_name', 'A-Sense')
    ad_copy = matched_ad.get('ad_copy', '')
    ad_link = matched_ad.get('landing_url') or ""
    ad_text = f"""
💡 [맞춤 추천] {brand_name}
{ad_copy}
👉 자세히 보기: {ad_link}
""".strip()

    return {
        "ad_found": True,
        "ad_text": ad_text,
        "ad_link": ad_link
    }


@app.post("/api/v1/publisher/domain", summary="퍼블리셔 도메인 화이트리스트 등록")
async def update_publisher_domain(
    payload: DomainUpdateRequest,
    auth_ctx: Dict[str, Any] = Depends(verify_coze_api_key)
):
    domain = (payload.domain or "").strip()
    normalized_domain = _normalize_domain(domain)
    if not normalized_domain:
        raise HTTPException(status_code=400, detail="유효한 도메인 URL을 입력해주세요.")

    canonical_url = f"https://{normalized_domain}"
    source = auth_ctx.get("source")
    api_key = auth_ctx.get("api_key")

    updated = False
    if source == "publisher_apps" and auth_ctx.get("app_id"):
        try:
            supabase.table("publisher_apps").update({"app_url": canonical_url}).eq("id", auth_ctx.get("app_id")).execute()
            updated = True
        except Exception:
            pass

    if not updated:
        try:
            supabase.table("publishers").update({"web_domain": canonical_url}).eq("api_key", api_key).execute()
            updated = True
        except Exception:
            pass

    if not updated:
        raise HTTPException(status_code=500, detail="도메인 저장에 실패했습니다.")

    return {
        "status": "success",
        "domain": canonical_url,
        "message": "도메인 화이트리스트가 저장되었습니다."
    }


@app.get("/api/v1/coze/openapi.json", include_in_schema=False)
async def get_coze_openapi_schema(request: Request):
    """Coze 플러그인 등록용 최소 OpenAPI 스키마"""
    global _coze_openapi_cache
    if _coze_openapi_cache is None:
        schema = get_openapi(
            title="A-Sense Coze Plugin API",
            version="1.0.0",
            description="Coze Plugin용 A-Sense 광고 매칭 API",
            routes=app.routes,
        )

        coze_path = "/api/v1/coze/get-ad"
        schema["paths"] = {coze_path: schema.get("paths", {}).get(coze_path, {})}

        post_op = schema["paths"].get(coze_path, {}).get("post")
        if post_op is not None:
            post_op["operationId"] = "getCozeAd"
            post_op["tags"] = ["coze"]

        schema["servers"] = [{"url": str(request.base_url).rstrip("/")}]
        _coze_openapi_cache = schema

    return JSONResponse(content=_coze_openapi_cache)


@app.post("/api/v1/quick-signup", summary="Coze 유저용 1초 API 키 발급")
async def quick_signup(payload: QuickSignupRequest):
    email = (payload.email or "").strip().lower()
    if not email or "@" not in email or email.startswith("@") or email.endswith("@"):
        raise HTTPException(status_code=400, detail="유효한 이메일을 입력해주세요.")

    # 1) 기존 가입자면 기존 키 재사용 (중복 발급 방지)
    try:
        existing = supabase.table("publishers").select("id, api_key").eq("email", email).execute()
        if existing.data:
            existing_key = existing.data[0].get("api_key")
            if existing_key:
                return {
                    "status": "success",
                    "message": "이미 발급된 키입니다. Coze 플러그인 설정에 아래 키를 입력하세요.",
                    "api_key": existing_key,
                    "is_existing": True
                }
    except Exception:
        # email 컬럼이 없는 스키마일 수 있어 신규 발급으로 진행
        pass

    # 2) 신규 키 발급
    new_api_key = f"sk_live_{uuid.uuid4().hex}"

    # 3) 즉시 활성 상태로 저장 (심사 없음)
    inserted = False
    try:
        supabase.table("publishers").insert({
            "email": email,
            "name": "Coze Bot User",
            "platform": "coze",
            "api_key": new_api_key,
            "is_verified": True,
        }).execute()
        inserted = True
    except Exception:
        # 스키마 호환 폴백 (email 컬럼 미보유 등)
        try:
            supabase.table("publishers").insert({
                "name": f"Coze Bot User ({email})",
                "platform": "coze",
                "api_key": new_api_key,
                "is_verified": True,
            }).execute()
            inserted = True
        except Exception as e:
            print(f"Quick signup insert error: {e}")

    if not inserted:
        raise HTTPException(status_code=500, detail="API 키 발급 중 오류가 발생했습니다.")

    return {
        "status": "success",
        "message": "발급이 완료되었습니다. Coze 플러그인 설정에 아래 키를 입력하세요.",
        "api_key": new_api_key,
        "is_existing": False
    }


async def get_current_publisher(authorization: str = Header(None)) -> Dict[str, Any]:
    """Bearer 토큰(API Key 또는 세션 토큰)에서 퍼블리셔를 식별합니다."""
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="로그인이 필요합니다.")

    token = authorization.split("Bearer ", 1)[1].strip()
    if not token:
        raise HTTPException(status_code=401, detail="유효하지 않은 인증 토큰입니다.")

    # 1) MVP 호환: API Key 직접 인증
    try:
        pub_by_key = supabase.table("publishers").select("id, balance, is_verified").eq("api_key", token).execute()
        if pub_by_key.data:
            row = pub_by_key.data[0]
            return {
                "id": row.get("id"),
                "balance": row.get("balance", 0),
                "is_verified": row.get("is_verified", True),
            }
    except Exception:
        pass

    # 2) 프로덕션: 세션 토큰 인증 (Supabase Auth)
    try:
        auth_user = supabase.auth.get_user(token)
        user_id = getattr(getattr(auth_user, "user", None), "id", None)
        if user_id:
            pub_by_id = supabase.table("publishers").select("id, balance, is_verified").eq("id", user_id).execute()
            if pub_by_id.data:
                row = pub_by_id.data[0]
                return {
                    "id": row.get("id"),
                    "balance": row.get("balance", 0),
                    "is_verified": row.get("is_verified", True),
                }
    except Exception:
        pass

    raise HTTPException(status_code=401, detail="인증에 실패했습니다.")


async def send_slack_notification(amount: int, paypal_email: str, publisher_id: str) -> bool:
    """정산 신청 접수 시 슬랙 채널로 실시간 알림을 전송합니다."""
    slack_webhook_url = os.environ.get("SLACK_WEBHOOK_URL")
    if not slack_webhook_url:
        print("SLACK_WEBHOOK_URL is not configured.")
        return False

    message = {
        "text": "🚨 새로운 정산 신청이 접수되었습니다!",
        "attachments": [
            {
                "color": "#36a64f",
                "fields": [
                    {"title": "요청 금액", "value": f"₩ {amount:,}", "short": True},
                    {"title": "지급 수단", "value": "PayPal", "short": True},
                    {"title": "페이팔 계정", "value": paypal_email, "short": False},
                    {"title": "매체사 ID", "value": publisher_id, "short": False},
                ],
                "footer": "A-Sense 관리자 시스템",
                "ts": int(datetime.utcnow().timestamp()),
            }
        ],
    }

    try:
        async with httpx.AsyncClient(timeout=5.0) as client:
            resp = await client.post(slack_webhook_url, json=message)
            return 200 <= resp.status_code < 300
    except Exception as e:
        print(f"Slack notification failed: {e}")
        return False


async def send_telegram_notification(amount: int, paypal_email: str, publisher_id: str) -> bool:
    """정산 신청 접수 시 텔레그램 봇으로 실시간 알림을 전송합니다."""
    bot_token = os.environ.get("TELEGRAM_BOT_TOKEN")
    chat_id = os.environ.get("TELEGRAM_CHAT_ID")
    if not bot_token or not chat_id:
        return False

    now_utc = datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S')
    text = (
        "🚨 *A-Sense 정산 신청 접수!*\n\n"
        f"💰 *요청 금액:* ₩ {amount:,}\n"
        f"📧 *PayPal:* `{paypal_email}`\n"
        f"🆔 *매체사 ID:* `{publisher_id}`\n"
        f"⏰ *시간:* {now_utc} (UTC)\n\n"
        "관리자 대시보드에서 검수 후 송금/승인 처리해 주세요."
    )
    url = f"https://api.telegram.org/bot{bot_token}/sendMessage"
    payload = {
        "chat_id": chat_id,
        "text": text,
        "parse_mode": "Markdown",
        "disable_web_page_preview": True,
    }

    try:
        async with httpx.AsyncClient(timeout=5.0) as client:
            resp = await client.post(url, json=payload)
            return 200 <= resp.status_code < 300
    except Exception as e:
        print(f"Telegram notification failed: {e}")
        return False


async def send_discord_notification(amount: int, paypal_email: str, publisher_id: str) -> bool:
    """정산 신청 접수 시 디스코드 웹훅으로 실시간 알림을 전송합니다."""
    webhook_url = os.environ.get("DISCORD_WEBHOOK_URL")
    if not webhook_url:
        return False

    payload = {
        "content": (
            "🚨 **새로운 정산 신청 접수!**\n"
            f"💰 금액: ₩ {amount:,}\n"
            f"📧 페이팔: {paypal_email}\n"
            f"🆔 매체사: `{publisher_id}`"
        )
    }

    try:
        async with httpx.AsyncClient(timeout=5.0) as client:
            resp = await client.post(webhook_url, json=payload)
            return 200 <= resp.status_code < 300
    except Exception as e:
        print(f"Discord notification failed: {e}")
        return False


async def send_admin_notification(amount: int, paypal_email: str, publisher_id: str):
    """환경설정에 따라 관리자 실시간 알림 채널(Telegram/Discord/Slack)을 전송합니다."""
    preferred = (os.environ.get("ADMIN_NOTIFICATION_CHANNEL") or "telegram").strip().lower()

    channels = {
        "telegram": send_telegram_notification,
        "discord": send_discord_notification,
        "slack": send_slack_notification,
    }

    # 1) 선호 채널 우선
    sender = channels.get(preferred)
    if sender:
        sent = await sender(amount, paypal_email, publisher_id)
        if sent:
            return

    # 2) 폴백 (Telegram -> Discord -> Slack)
    for fallback in (send_telegram_notification, send_discord_notification, send_slack_notification):
        sent = await fallback(amount, paypal_email, publisher_id)
        if sent:
            return

    print("No admin notification channel configured or all notification sends failed.")


@app.post("/api/v1/withdrawals", summary="수익금 정산 신청")
async def request_withdrawal(
    payload: WithdrawalRequest,
    publisher: Dict[str, Any] = Depends(get_current_publisher)
):
    MINIMUM_PAYOUT = 50000
    publisher_id = publisher.get("id")
    if not publisher_id:
        raise HTTPException(status_code=401, detail="퍼블리셔 인증에 실패했습니다.")

    # 1) DB에서 현재 유저의 진짜 잔액 재조회
    try:
        pub_res = supabase.table("publishers").select("id, balance").eq("id", publisher_id).execute()
        if not pub_res.data:
            raise HTTPException(status_code=404, detail="퍼블리셔 정보를 찾을 수 없습니다.")
        current_balance = int(pub_res.data[0].get("balance", 0) or 0)
    except HTTPException:
        raise
    except Exception as e:
        print(f"Withdrawal balance fetch error: {e}")
        raise HTTPException(status_code=500, detail="잔액 조회 중 오류가 발생했습니다.")

    # 2) 서버 사이드 검증
    if current_balance < MINIMUM_PAYOUT:
        raise HTTPException(status_code=400, detail=f"잔액이 {MINIMUM_PAYOUT}원 미만이라 출금할 수 없습니다.")

    if payload.amount <= 0:
        raise HTTPException(status_code=400, detail="출금 요청 금액은 0보다 커야 합니다.")

    paypal_email = (payload.paypal_email or "").strip().lower()
    if not paypal_email or "@" not in paypal_email:
        raise HTTPException(status_code=400, detail="유효한 PayPal 이메일을 입력해주세요.")

    if payload.amount > current_balance:
        raise HTTPException(status_code=400, detail="보유 잔액보다 많은 금액을 요청할 수 없습니다.")

    # 3) 출금 대기 기록 + 4) 잔액 차감
    try:
        try:
            supabase.table("payout_requests").insert({
                "publisher_id": publisher_id,
                "amount": current_balance,
                "status": "pending",
                "requested_at": datetime.utcnow().isoformat(),
                "paypal_email": paypal_email,
            }).execute()
        except Exception:
            # 스키마 폴백: paypal_email 컬럼이 없으면 기본 컬럼만 기록
            supabase.table("payout_requests").insert({
                "publisher_id": publisher_id,
                "amount": current_balance,
                "status": "pending",
                "requested_at": datetime.utcnow().isoformat(),
            }).execute()

        supabase.table("publishers").update({"balance": 0}).eq("id", publisher_id).execute()

        # DB 반영 성공 후 관리자 실시간 알림 전송 (Telegram/Discord/Slack)
        await send_admin_notification(
            amount=current_balance,
            paypal_email=paypal_email,
            publisher_id=publisher_id,
        )

        return {
            "status": "success",
            "message": "정산 신청이 완료되었습니다.",
            "requested_amount": current_balance,
            "paypal_email": paypal_email,
        }
    except Exception as e:
        print(f"출금 처리 에러: {e}")
        raise HTTPException(status_code=500, detail="서버 오류로 인해 출금 요청에 실패했습니다.")

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
                pub_query = supabase.table("publishers").select("id, verification_token, is_verified, web_domain").eq("api_key", x_api_key).execute()
                if not pub_query.data: 
                    if x_api_key == "test-api-key": # Backdoor for testing
                        pub_id = "test-publisher"
                        publisher_info = {"id": "test-publisher", "is_verified": True}
                    else:
                        raise HTTPException(status_code=401, detail="Invalid Key")
                else:
                    publisher_info = pub_query.data[0]
                    pub_id = publisher_info['id']

                    # [도메인 화이트리스트 검증]
                    _enforce_domain_whitelist(request, publisher_info.get("web_domain"), x_api_key)

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
    try:
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
    except Exception as e:
        print(f"Register Error: {e}")
        return JSONResponse(status_code=500, content={"status": "error", "message": str(e)})

@app.post("/api/v1/advertiser/login")
async def advertiser_login(request: Request):
    try:
        data = await request.json()
        email = data.get("email")
        password = data.get("password")
        
        res = supabase.table("advertiser_users").select("*").eq("email", email).execute()
        if not res.data or res.data[0]["password_hash"] != password:
            return JSONResponse(status_code=401, content={"status": "error", "message": "Invalid credentials"})
        
        return {"status": "success", "user": res.data[0]}
    except Exception as e:
        print(f"Login Error: {e}")
        return JSONResponse(status_code=500, content={"status": "error", "message": str(e)})

@app.post("/api/v1/advertiser/ads")
async def create_ad(request: Request):
    data = await request.json()
    supabase.table("advertisers").insert(data).execute()
    return {"status": "success"}

@app.get("/api/v1/advertiser/ads")
async def list_ads(owner_id: str):
    res = supabase.table("advertisers").select("*").eq("owner_id", owner_id).execute()
    return {"ads": res.data}

@app.get("/api/v1/advertiser/balance")
async def get_balance(advertiser_id: str):
    res = supabase.table("advertiser_users").select("balance").eq("id", advertiser_id).execute()
    if res.data:
        return {"balance": res.data[0]["balance"]}
    return {"balance": 0}

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
@app.get("/api/payment/success", response_class=HTMLResponse)
@app.get("/api/payment/toss/success", response_class=HTMLResponse) # Keep for backward compatibility
async def payment_success(paymentKey: str, orderId: str, amount: int, provider: str = "toss"):
    # 1. Toss 결제 승인 요청 (필수)
    if provider == "toss":
        toss_secret = os.environ.get("TOSS_SECRET_KEY")
        if not toss_secret:
            return HTMLResponse(content="<h1>Error: TOSS_SECRET_KEY not set</h1>", status_code=500)
            
        # Secret Key를 Base64로 인코딩 (뒤에 콜론 필수)
        secret_key_bytes = f"{toss_secret}:".encode("utf-8")
        auth_header = f"Basic {base64.b64encode(secret_key_bytes).decode('utf-8')}"
        
        url = "https://api.tosspayments.com/v1/payments/confirm"
        headers = {
            "Authorization": auth_header,
            "Content-Type": "application/json"
        }
        data = {
            "paymentKey": paymentKey,
            "orderId": orderId,
            "amount": amount
        }
        
        try:
            response = requests.post(url, json=data, headers=headers)
            res_json = response.json()
            
            if response.status_code != 200:
                # 결제 승인 실패
                error_msg = res_json.get('message', 'Unknown error')
                code = res_json.get('code', 'ERROR')
                return HTMLResponse(content=f"<h1>결제 승인 실패</h1><p>{code}: {error_msg}</p><a href='/static/advertiser_dashboard.html'>돌아가기</a>", status_code=400)
                
        except Exception as e:
            print(f"Toss Confirm Error: {e}")
            return HTMLResponse(content=f"<h1>결제 시스템 오류</h1><p>{str(e)}</p>", status_code=500)
    
    # 2. 잔액 업데이트 (Dashboard 로직에 따라 개별 광고 캠페인에 충전)
    advertiser_id = orderId.split("_")[0] # orderId = "{ad_id}_{timestamp}"
    
    try:
        current = supabase.table("advertiser_users").select("balance").eq("id", advertiser_id).execute()
        if current.data:
            new_bal = current.data[0]['balance'] + amount
            supabase.table("advertiser_users").update({"balance": new_bal}).eq("id", advertiser_id).execute()
            
            supabase.table("transactions").insert({
                "advertiser_id": advertiser_id,
                "amount": amount,
                "type": "deposit",
                "provider": provider,
                "payment_key": paymentKey,
                "description": f"{provider.upper()} 충전"
            }).execute()
            
            # (Optional) Log to deposits table for redundancy
            supabase.table("deposits").insert({
                "advertiser_id": advertiser_id,
                "amount": amount,
                "status": "completed",
                "method": provider
            }).execute()

    except Exception as e:
        print(f"Payment Update Error: {e}")

    return f"""
    <html>
        <head>
            <title>Payment Successful</title>
            <style>
                body {{ font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif; text-align: center; padding: 50px; background-color: #f9fafb; }}
                .container {{ max-width: 500px; margin: 0 auto; background: white; padding: 40px; border-radius: 16px; box-shadow: 0 4px 6px rgba(0,0,0,0.1); }}
                .icon {{ font-size: 48px; margin-bottom: 20px; }}
                .title {{ color: #111827; font-size: 24px; font-weight: bold; margin-bottom: 10px; }}
                .message {{ color: #6b7280; margin-bottom: 30px; }}
                .details {{ background: #f3f4f6; padding: 20px; border-radius: 8px; margin-bottom: 30px; text-align: left; }}
                .btn {{ display: inline-block; width: 100%; padding: 12px; background: #3b82f6; color: white; text-decoration: none; border-radius: 8px; font-weight: bold; box-sizing: border-box; }}
                .btn:hover {{ background: #2563eb; }}
            </style>
        </head>
        <body>
            <div class="container">
                <div class="icon">✅</div>
                <div class="title">결제가 완료되었습니다</div>
                <div class="message">요청하신 예치금 충전이 정상적으로 처리되었습니다.</div>
                
                <div class="details">
                    <p><strong>주문 번호:</strong> {orderId}</p>
                    <p><strong>충전 금액:</strong> ₩{amount:,}</p>
                    <p><strong>결제 수단:</strong> {provider.upper()}</p>
                    <p><strong>처리 결과:</strong> 성공</p>
                </div>
                
                <a href="javascript:window.close()" class="btn">창 닫기</a>
                <p style="margin-top: 10px; font-size: 12px; color: #9ca3af;">2초 후 자동으로 닫힙니다.</p>
            </div>
            <script>
                // 팝업으로 열렸을 경우 부모창 새로고침 후 닫기
                if(window.opener) {{
                    window.opener.location.reload();
                    setTimeout(function() {{ window.close(); }}, 2000);
                }} else {{
                    setTimeout(function() {{ window.location.href = '/static/dashboard.html'; }}, 3000);
                }}
            </script>
        </body>
    </html>
    """

@app.get("/api/payment/fail", response_class=HTMLResponse)
@app.get("/api/payment/toss/fail", response_class=HTMLResponse)
async def toss_fail(code: str, message: str, orderId: str):
    return f"""
    <html>
        <head>
            <title>Payment Failed</title>
            <style>
                body {{ font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif; text-align: center; padding: 50px; background-color: #f9fafb; }}
                .container {{ max-width: 500px; margin: 0 auto; background: white; padding: 40px; border-radius: 16px; box-shadow: 0 4px 6px rgba(0,0,0,0.1); }}
                .icon {{ font-size: 48px; margin-bottom: 20px; }}
                .title {{ color: #ef4444; font-size: 24px; font-weight: bold; margin-bottom: 10px; }}
                .message {{ color: #6b7280; margin-bottom: 30px; }}
                .btn {{ display: inline-block; width: 100%; padding: 12px; background: #4b5563; color: white; text-decoration: none; border-radius: 8px; font-weight: bold; box-sizing: border-box; }}
            </style>
        </head>
        <body>
            <div class="container">
                <div class="icon">⚠️</div>
                <div class="title">결제에 실패했습니다</div>
                <div class="message">{message}</div>
                <p style="color:#9ca3af; font-size:0.9em;">Code: {code}</p>
                <br>
                <a href="javascript:history.back()" class="btn">뒤로 가기</a>
            </div>
        </body>
    </html>
    """

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

@app.get("/debug-paths")
async def debug_paths():
    """Vercel 디버깅용: 현재 경로 및 파일 목록 확인"""
    import glob
    cwd = os.getcwd()
    ls = os.listdir(cwd)
    static_ls = []
    if os.path.exists(STATIC_DIR):
        static_ls = os.listdir(STATIC_DIR)
    
    return {
        "cwd": cwd,
        "ls": ls,
        "STATIC_DIR": STATIC_DIR,
        "static_exists": os.path.exists(STATIC_DIR),
        "static_ls": static_ls,
        "base_dir": BASE_DIR
    }
