import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from supabase import create_client, Client
from datetime import datetime, timedelta
import os
import random
import uuid
import streamlit.components.v1 as components

# [설정] 페이지 기본 세팅
st.set_page_config(
    page_title="A-Sense Admin", 
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded"
)

# [CSS] UI 개선
st.markdown("""
    <style>
    .main {
        background-color: #f8f9fa;
    }
    .stMetric {
        background-color: #ffffff;
        padding: 15px;
        border-radius: 10px;
        box-shadow: 0 2px 4px rgba(0,0,0,0.05);
    }
    div[data-testid="stSidebarNav"] {
        padding-top: 20px;
    }
    </style>
    """, unsafe_allow_html=True)

# [i18n] 다국어 지원 설정
if "lang" not in st.session_state:
    st.session_state.lang = "ko"

with st.sidebar:
    st.title("🤖 A-Sense")
    lang_mode = st.radio("Language / 언어", ["한국어", "English"], horizontal=True)
    st.session_state.lang = "en" if lang_mode == "English" else "ko"
    LANG = st.session_state.lang

T = {
    "en": {
        "menu_home": "Dashboard",
        "menu_partner": "Partners",
        "menu_ads": "Advertisers",
        "menu_fraud": "Fraud Guard",
        "title_home": "Dashboard Overview",
        "kpi_revenue": "Total Revenue",
        "kpi_valid": "Valid Clicks",
        "kpi_ctr": "CTR (Avg)",
        "kpi_imp": "Impressions",
        "chart_trend": "Traffic Trend (Hourly)",
        "chart_platform": "Platform Distribution",
        "tab_overview": "Overview",
        "tab_verify": "Verification",
        "tab_payout": "Payouts",
        "tab_list": "Ad List",
        "tab_create": "Create Ad",
        "tab_budget": "Budget & Billing",
        "verify_req": "Verification Requests",
        "verify_btn": "Approve Partner",
        "no_data": "No data available yet.",
        "ad_brand": "Brand Name",
        "ad_bid": "CPC Bid",
        "ad_copy": "Ad Copy",
        "ad_url": "Landing URL",
        "ad_kw": "Keywords",
        "ad_submit": "Register Ad",
        "charge_amount": "Amount (KRW)",
        "charge_btn": "Charge",
        "fraud_reason": "Block Reasons",
        "fraud_log": "Blocked Logs"
    },
    "ko": {
        "menu_home": "대시보드",
        "menu_partner": "파트너 관리",
        "menu_ads": "광고주 센터",
        "menu_fraud": "부정 클릭 방지",
        "title_home": "운영 현황 대시보드",
        "kpi_revenue": "총 예상 수익",
        "kpi_valid": "유효 클릭 수",
        "kpi_ctr": "평균 클릭률 (CTR)",
        "kpi_imp": "총 노출 수",
        "chart_trend": "시간대별 트래픽 추이",
        "chart_platform": "플랫폼별 점유율",
        "tab_overview": "전체 현황",
        "tab_verify": "승인 대기",
        "tab_payout": "정산 관리",
        "tab_list": "광고 목록",
        "tab_create": "새 광고 등록",
        "tab_budget": "예산/결제 관리",
        "verify_req": "파트너 승인 요청",
        "verify_btn": "승인 처리",
        "no_data": "데이터가 없습니다.",
        "ad_brand": "브랜드명",
        "ad_bid": "입찰가 (CPC)",
        "ad_copy": "광고 문구 (AI 추천)",
        "ad_url": "랜딩 페이지 URL",
        "ad_kw": "타겟 키워드 (쉼표 구분)",
        "ad_submit": "광고 등록하기",
        "charge_amount": "충전 금액 (원)",
        "charge_btn": "충전하기",
        "fraud_reason": "차단 사유 분석",
        "fraud_log": "차단 상세 로그"
    }
}

# [보안] 관리자 로그인
ADMIN_PASSWORD = os.environ.get("ADMIN_PASSWORD", "admin1234")

def check_password():
    if "password_correct" not in st.session_state:
        st.session_state["password_correct"] = False

    if not st.session_state["password_correct"]:
        st.info("🔒 관리자 모드 접근을 위해 비밀번호를 입력해주세요.")
        pwd = st.text_input("Password", type="password")
        if st.button("Login"):
            if pwd == ADMIN_PASSWORD:
                st.session_state["password_correct"] = True
                st.rerun()
            else:
                st.error("비밀번호가 올바르지 않습니다.")
        return False
    return True

if not check_password():
    st.stop()

# --- [Mock Data Provider] ---
class MockClient:
    def __init__(self):
        self.data = {
            "advertisers": [
                {"id": "1", "brand_name": "Nike", "cpc_bid": 500, "balance": 50000, "ad_copy": "Just Do It", "keywords": ["shoes", "sports"], "landing_url": "https://nike.com"},
                {"id": "2", "brand_name": "Samsung", "cpc_bid": 700, "balance": 120000, "ad_copy": "Galaxy S24 AI", "keywords": ["phone", "ai"], "landing_url": "https://samsung.com"},
                {"id": "3", "brand_name": "Coupang", "cpc_bid": 300, "balance": 5000, "ad_copy": "Rocket Delivery", "keywords": ["shopping"], "landing_url": "https://coupang.com"},
            ],
            "publishers": [
                {"id": "pub1", "name": "My AI Chatbot", "email": "dev@test.com", "is_verified": True},
                {"id": "pub2", "name": "Travel Helper", "email": "travel@test.com", "is_verified": False},
            ],
            "logs": self._generate_mock_logs()
        }
    
    def _generate_mock_logs(self):
        logs = []
        platforms = ["chatbot", "web", "mobile_app"]
        reasons = ["IP_REPEAT", "BOT_UA", "SPEED_CLICK"]
        now = datetime.now()
        for i in range(100):
            is_valid = random.choice([True, True, True, False])
            logs.append({
                "timestamp": (now - timedelta(hours=random.randint(0, 24))).isoformat(),
                "type": random.choice(["impression", "impression", "click"]),
                "platform": random.choice(platforms),
                "is_valid": is_valid,
                "invalid_reason": random.choice(reasons) if not is_valid else None,
                "user_ip": f"192.168.1.{random.randint(1, 255)}"
            })
        return logs

    def table(self, table_name):
        return MockTableQuery(self.data.get(table_name, []))

class MockTableQuery:
    def __init__(self, data):
        self.data = data
        
    def select(self, *args):
        return self
        
    def insert(self, record):
        self.data.append(record)
        return self
        
    def update(self, record):
        # Mock update (simple)
        return self
        
    def eq(self, col, val):
        # Mock filter for update logic (simplified)
        return self
        
    def execute(self):
        class Res:
            def __init__(self, d): self.data = d
        return Res(self.data)

# [연결] Supabase
SUPABASE_URL = os.environ.get("SUPABASE_URL")
SUPABASE_KEY = os.environ.get("SUPABASE_KEY")

@st.cache_resource
def init_supabase():
    # 1. Try Real Connection
    if SUPABASE_URL and "your-project" not in SUPABASE_URL:
        try:
            client = create_client(SUPABASE_URL, SUPABASE_KEY)
            # Simple check
            client.table("advertisers").select("id").limit(1).execute()
            return client
        except:
            pass
            
    # 2. Fallback to Mock
    return MockClient()

supabase = init_supabase()
is_mock = isinstance(supabase, MockClient)

if is_mock:
    st.sidebar.warning("⚠️ Running in Mock Mode (No Real DB)")

# [공통] 데이터 로딩
def load_data(table):
    if not supabase: return pd.DataFrame()
    try:
        response = supabase.table(table).select("*").execute()
        return pd.DataFrame(response.data)
    except Exception:
        return pd.DataFrame()

# --- [사이드바] 메뉴 ---
menu = st.sidebar.radio("Navigation", [
    T[LANG]["menu_home"], 
    T[LANG]["menu_partner"], 
    T[LANG]["menu_ads"], 
    T[LANG]["menu_fraud"]
])

st.sidebar.markdown("---")
st.sidebar.caption(f"v1.0.2 | Server: {os.environ.get('API_BASE_URL', 'Localhost')}")

# ==========================================
# 1. 대시보드 (Home)
# ==========================================
if menu == T[LANG]["menu_home"]:
    st.header(T[LANG]["title_home"])
    
    logs = load_data("logs")
    
    # KPI Cards
    col1, col2, col3, col4 = st.columns(4)
    
    valid_clicks = 0
    impressions = 0
    revenue = 0
    ctr = 0.0

    if not logs.empty and 'type' in logs.columns:
        if 'is_valid' in logs.columns:
            valid_clicks = len(logs[(logs['type'] == 'click') & (logs['is_valid'] == True)])
        else:
            valid_clicks = len(logs[logs['type'] == 'click'])
            
        impressions = len(logs[logs['type'] == 'impression'])
        revenue = valid_clicks * 500  # Mock CPC
        if impressions > 0:
            ctr = (valid_clicks / impressions) * 100

    col1.metric(T[LANG]["kpi_revenue"], f"₩{revenue:,}", delta="Real-time")
    col2.metric(T[LANG]["kpi_valid"], f"{valid_clicks} Click", delta="Valid")
    col3.metric(T[LANG]["kpi_imp"], f"{impressions} Imp")
    col4.metric(T[LANG]["kpi_ctr"], f"{ctr:.2f}%")

    st.markdown("---")

    # Charts
    if not logs.empty:
        c1, c2 = st.columns([2, 1])
        
        with c1:
            st.subheader(T[LANG]["chart_trend"])
            if 'timestamp' in logs.columns:
                logs['timestamp'] = pd.to_datetime(logs['timestamp'])
                logs['hour'] = logs['timestamp'].dt.hour
                hourly_data = logs.groupby(['hour', 'type']).size().reset_index(name='count')
                fig_trend = px.line(hourly_data, x='hour', y='count', color='type', markers=True)
                st.plotly_chart(fig_trend, use_container_width=True)
        
        with c2:
            st.subheader(T[LANG]["chart_platform"])
            if 'platform' in logs.columns:
                platform_counts = logs['platform'].value_counts().reset_index()
                platform_counts.columns = ['platform', 'count']
                fig_pie = px.pie(platform_counts, values='count', names='platform', hole=0.4)
                st.plotly_chart(fig_pie, use_container_width=True)
    else:
        st.info(T[LANG]["no_data"])

# ==========================================
# 2. 파트너 관리
# ==========================================
elif menu == T[LANG]["menu_partner"]:
    st.header(T[LANG]["menu_partner"])
    
    tab1, tab2, tab3 = st.tabs([T[LANG]["tab_overview"], T[LANG]["tab_verify"], T[LANG]["tab_payout"]])
    
    pubs = load_data("publishers")
    
    with tab1:
        st.subheader(T[LANG]["tab_overview"])
        if not pubs.empty:
            st.dataframe(pubs, use_container_width=True)
        else:
            st.info(T[LANG]["no_data"])

    with tab2:
        st.subheader(T[LANG]["verify_req"])
        if not pubs.empty and 'is_verified' in pubs.columns:
            unverified = pubs[pubs['is_verified'] == False]
            if not unverified.empty:
                st.warning(f"Wait List: {len(unverified)}")
                for idx, row in unverified.iterrows():
                    c1, c2 = st.columns([3, 1])
                    with c1:
                        st.write(f"**{row['name']}** ({row.get('email', 'No Email')})")
                        st.caption(f"ID: {row['id']}")
                    with c2:
                        if st.button(T[LANG]["verify_btn"], key=f"v_{row['id']}"):
                            # Mock logic handled by UI feedback
                            st.success("Approved!")
                            st.rerun()
            else:
                st.success("All partners are verified! 🎉")
        else:
            st.info("No partners found.")

    with tab3:
        st.subheader(T[LANG]["tab_payout"])
        st.info("Coming Soon: Payout Request Management")

# ==========================================
# 3. 광고주 센터
# ==========================================
elif menu == T[LANG]["menu_ads"]:
    st.header(T[LANG]["menu_ads"])
    
    tab1, tab2, tab3 = st.tabs([T[LANG]["tab_list"], T[LANG]["tab_create"], T[LANG]["tab_budget"]])
    
    ads_df = load_data("advertisers")
    
    with tab1:
        if not ads_df.empty:
            st.dataframe(ads_df, use_container_width=True)
        else:
            st.info(T[LANG]["no_data"])
            
    with tab2:
        st.subheader(T[LANG]["tab_create"])
        with st.form("create_ad_form"):
            col1, col2 = st.columns(2)
            brand = col1.text_input(T[LANG]["ad_brand"])
            bid = col2.number_input(T[LANG]["ad_bid"], min_value=100, value=500, step=50)
            
            copy = st.text_area(T[LANG]["ad_copy"], height=100)
            url = st.text_input(T[LANG]["ad_url"], placeholder="https://...")
            keywords = st.text_input(T[LANG]["ad_kw"], placeholder="e.g. AI, Chatbot, Tech")
            
            submitted = st.form_submit_button(T[LANG]["ad_submit"], type="primary")
            
            if submitted:
                st.success(f"Ad for '{brand}' created successfully! (Mock)")
                st.rerun()

    with tab3:
        st.subheader(T[LANG]["tab_budget"])
        
        # Admin Manual Charge
        with st.expander("Admin Manual Charge", expanded=True):
            if not ads_df.empty:
                c1, c2, c3 = st.columns([2, 1, 1])
                target_brand = c1.selectbox("Select Advertiser", ads_df['brand_name'].unique())
                amount = c2.number_input(T[LANG]["charge_amount"], step=10000)
                if c3.button(T[LANG]["charge_btn"]):
                    st.success(f"Charged {amount:,} KRW to {target_brand}")
                    st.rerun()
            else:
                st.info("No advertisers to charge.")

        st.divider()
        
        # Payment Gateway Integration (UI Mockup)
        st.subheader("Online Payment Gateway")
        st.info("Toss Payments & PayPal integration is ready. Connect API Keys in production.")
        
        if not ads_df.empty:
            target_ad_idx = st.selectbox("Select Advertiser for Online Payment", range(len(ads_df)), format_func=lambda x: ads_df.iloc[x]['brand_name'])
            target_ad = ads_df.iloc[target_ad_idx]
            
            pay_amt = st.number_input("Amount", min_value=1000, step=1000, key="online_pay")
            
            API_BASE_URL = os.environ.get("API_BASE_URL", "https://a-sense-project.vercel.app")
            
            html_code = f"""
            <div style="display: flex; gap: 10px;">
                <button onclick="alert('Toss Payment Window will open for {target_ad['brand_name']}')" 
                        style="background:#0064FF; color:white; border:none; padding:10px 20px; border-radius:5px; cursor:pointer;">
                    Pay with Toss
                </button>
                <button onclick="alert('PayPal Window will open')" 
                        style="background:#FFC439; color:black; border:none; padding:10px 20px; border-radius:5px; cursor:pointer;">
                    Pay with PayPal
                </button>
            </div>
            """
            components.html(html_code, height=60)

# ==========================================
# 4. 부정 클릭 (Fraud)
# ==========================================
elif menu == T[LANG]["menu_fraud"]:
    st.header(T[LANG]["menu_fraud"])
    
    logs = load_data("logs")
    if not logs.empty and 'is_valid' in logs.columns:
        fraud_logs = logs[logs['is_valid'] == False]
        
        c1, c2 = st.columns(2)
        c1.metric("Blocked Clicks", len(fraud_logs), delta_color="inverse")
        
        if not fraud_logs.empty:
            if 'invalid_reason' in fraud_logs.columns:
                reason_counts = fraud_logs['invalid_reason'].value_counts().reset_index()
                reason_counts.columns = ['reason', 'count']
                fig_reason = px.bar(reason_counts, x='count', y='reason', orientation='h', title=T[LANG]["fraud_reason"])
                st.plotly_chart(fig_reason, use_container_width=True)
            
            st.subheader(T[LANG]["fraud_log"])
            st.dataframe(fraud_logs[['timestamp', 'platform', 'user_ip', 'invalid_reason']], use_container_width=True)
    else:
        st.info(T[LANG]["no_data"])
