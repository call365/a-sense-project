import streamlit as st
import pandas as pd
import plotly.express as px
from supabase import create_client, Client
from datetime import datetime, timedelta
import os
import streamlit.components.v1 as components

# [설정] 페이지 기본 세팅
st.set_page_config(page_title="A-Sense Admin", layout="wide")

# [i18n] 다국어 지원 설정
lang_mode = st.sidebar.selectbox("Language / 언어", ["한국어", "English"])
LANG = "en" if lang_mode == "English" else "ko"

T = {
    "en": {
        "menu_title": "A-Sense Manager",
        "menu_home": "Dashboard (Home)",
        "menu_partner": "Partner Management",
        "menu_ads": "Ad & Budget Management",
        "menu_fraud": "Fraud Analysis",
        "title_home": "🚀 Real-time Operation Status",
        "kpi_revenue": "💰 Total Revenue",
        "kpi_valid": "👆 Valid Clicks",
        "kpi_fraud": "🛡️ Blocked Fraud",
        "kpi_imp": "👀 Impressions",
        "chart_title": "📊 Traffic Analysis (Valid vs Fraud)",
        "no_data": "No data yet. Connect a chatbot!",
        "title_partner": "🤝 Partner Management",
        "wait_verify": "⚠️ Partners waiting for verification:",
        "verify_input": "Partner ID to verify",
        "verify_btn": "Approve",
        "verify_success": "Partner approved!",
        "all_partners": "All Partners",
        "no_partners": "No partners registered.",
        "title_ads": "📢 Ad Budget & Creative Management",
        "curr_balance": "Current Advertiser Balances",
        "no_advertisers": "No advertisers registered.",
        "charge_sec": "💳 Recharge Budget (Admin Manual)",
        "charge_online": "💳 Online Recharge (Test/User Mode)",
        "charge_select": "Select Advertiser",
        "charge_amount": "Amount",
        "charge_memo": "Memo",
        "charge_btn": "Recharge Now",
        "charge_success": "Recharged successfully!",
        "charge_fail": "Recharge failed",
        "new_ad_sec": "Register New Ad",
        "ad_brand": "Brand Name",
        "ad_bid": "CPC Bid",
        "ad_copy": "AI Ad Copy",
        "ad_url": "Landing URL",
        "ad_kw": "Target Keywords (comma separated)",
        "ad_submit": "Register Ad",
        "ad_success": "Ad registered!",
        "title_fraud": "🕵️ Fraud Log Analysis",
        "fraud_count": "Total fraud clicks blocked:",
        "fraud_detail": "Detailed Block Logs"
    },
    "ko": {
        "menu_title": "A-Sense Manager",
        "menu_home": "대시보드 (Home)",
        "menu_partner": "파트너 관리",
        "menu_ads": "광고주/소재 관리",
        "menu_fraud": "부정 클릭 분석",
        "title_home": "🚀 실시간 운영 현황",
        "kpi_revenue": "💰 누적 수익",
        "kpi_valid": "👆 유효 클릭",
        "kpi_fraud": "🛡️ 차단된 부정 클릭",
        "kpi_imp": "👀 총 노출수",
        "chart_title": "📊 시간대별 트래픽 추이 (유효 vs 무효)",
        "no_data": "아직 데이터가 없습니다. 챗봇을 연결해보세요!",
        "title_partner": "🤝 파트너(매체) 관리",
        "wait_verify": "⚠️ 승인 대기 중인 파트너가 있습니다:",
        "verify_input": "승인할 파트너 ID 입력",
        "verify_btn": "승인 처리",
        "verify_success": "승인 완료! 이제 광고가 송출됩니다.",
        "all_partners": "전체 파트너 목록",
        "no_partners": "등록된 파트너가 없습니다.",
        "title_ads": "📢 광고 예산 및 소재 관리",
        "curr_balance": "현재 광고주별 잔액 현황",
        "no_advertisers": "등록된 광고주가 없습니다.",
        "charge_sec": "💳 예산 충전 (관리자 수동)",
        "charge_online": "💳 온라인 충전 (테스트/사용자 모드)",
        "charge_select": "충전할 광고주",
        "charge_amount": "충전 금액 (원)",
        "charge_memo": "메모",
        "charge_btn": "즉시 충전",
        "charge_success": "충전이 완료되었습니다.",
        "charge_fail": "충전 실패",
        "new_ad_sec": "새 광고 등록",
        "ad_brand": "브랜드명",
        "ad_bid": "입찰가(CPC)",
        "ad_copy": "AI 추천 멘트",
        "ad_url": "랜딩 URL",
        "ad_kw": "타겟 키워드 (쉼표로 구분)",
        "ad_submit": "광고 등록",
        "ad_success": "광고가 등록되었습니다!",
        "title_fraud": "🕵️ 부정 클릭(Fraud) 상세 로그",
        "fraud_count": "총 차단된 부정 클릭 수:",
        "fraud_detail": "상세 차단 내역"
    }
}

# [보안] 관리자 로그인
# 비밀번호 설정 (배포 시 secrets에 넣는 게 좋음)
ADMIN_PASSWORD = os.environ.get("ADMIN_PASSWORD", "admin1234")

def check_password():
    if "password_correct" not in st.session_state:
        st.session_state["password_correct"] = False

    if not st.session_state["password_correct"]:
        pwd = st.text_input("관리자 비밀번호를 입력하세요", type="password")
        if st.button("로그인"):
            if pwd == ADMIN_PASSWORD:
                st.session_state["password_correct"] = True
                st.rerun()
            else:
                st.error("비밀번호가 틀렸습니다.")
        return False
    return True

if not check_password():
    st.stop() # 비밀번호 틀리면 아래 코드 실행 안 함

# [연결] Supabase (환경 변수 우선, 로컬 폴백)
SUPABASE_URL = os.environ.get("SUPABASE_URL")
SUPABASE_KEY = os.environ.get("SUPABASE_KEY")

# 로컬 테스트용 폴백 (개발 편의성)
if not SUPABASE_URL:
    # st.warning("SUPABASE_URL not found in env. Using default for local test.")
    SUPABASE_URL = "https://your-project.supabase.co" 
if not SUPABASE_KEY:
    SUPABASE_KEY = "your-anon-key"

@st.cache_resource
def init_supabase():
    try:
        return create_client(SUPABASE_URL, SUPABASE_KEY)
    except Exception as e:
        st.error(f"Supabase 연결 실패: {e}")
        return None

supabase = init_supabase()

# --- [사이드바] 메뉴 ---
st.sidebar.title(T[LANG]["menu_title"])
menu_options = [T[LANG]["menu_home"], T[LANG]["menu_partner"], T[LANG]["menu_ads"], T[LANG]["menu_fraud"]]
menu = st.sidebar.radio("Menu", menu_options)

# --- [공통] 데이터 로딩 함수 ---
def load_data(table):
    if not supabase: return pd.DataFrame()
    try:
        response = supabase.table(table).select("*").execute()
        return pd.DataFrame(response.data)
    except Exception as e:
        st.error(f"데이터 로딩 실패 ({table}): {e}")
        return pd.DataFrame()

# ==========================================
# 1. 대시보드 (Home) - 전체 현황판
# ==========================================
if menu == T[LANG]["menu_home"]:
    st.title(T[LANG]["title_home"])
    
    # 데이터 가져오기
    logs = load_data("logs")
    
    if not logs.empty:
        if 'timestamp' in logs.columns:
            logs['timestamp'] = pd.to_datetime(logs['timestamp'])
        
        # 핵심 지표 (KPI) 계산
        valid_clicks = len(logs[(logs['type'] == 'click') & (logs['is_valid'] == True)])
        invalid_clicks = len(logs[(logs['type'] == 'click') & (logs['is_valid'] == False)])
        impressions = len(logs[logs['type'] == 'impression'])
        
        # 수익 계산 (클릭당 500원 가정 - 추후 광고주별 단가 연동 가능)
        revenue = valid_clicks * 500

        # 상단 지표 카드
        col1, col2, col3, col4 = st.columns(4)
        col1.metric(T[LANG]["kpi_revenue"], f"{revenue:,} KRW", delta="Real-time")
        col2.metric(T[LANG]["kpi_valid"], f"{valid_clicks}")
        col3.metric(T[LANG]["kpi_fraud"], f"{invalid_clicks}", delta_color="inverse")
        col4.metric(T[LANG]["kpi_imp"], f"{impressions}")

        # 차트 1: 시간대별 트래픽 (유효 vs 무효)
        if 'timestamp' in logs.columns:
            st.subheader(T[LANG]["chart_title"])
            logs['hour'] = logs['timestamp'].dt.hour
            chart_data = logs.groupby(['hour', 'type', 'is_valid']).size().reset_index(name='count')
            fig = px.bar(chart_data, x='hour', y='count', color='is_valid', 
                         title=T[LANG]["chart_title"], barmode='group')
            st.plotly_chart(fig, use_container_width=True)

    else:
        st.info(T[LANG]["no_data"])

# ==========================================
# 2. 파트너 관리 - 승인 및 검증
# ==========================================
elif menu == T[LANG]["menu_partner"]:
    st.title(T[LANG]["title_partner"])
    
    pubs = load_data("publishers")
    if not pubs.empty:
        # 미인증 파트너 강조
        if 'is_verified' in pubs.columns:
            unverified = pubs[pubs['is_verified'] == False]
            if not unverified.empty:
                st.error(f"{T[LANG]['wait_verify']} {len(unverified)}")
                st.dataframe(unverified)
                
                # 수동 승인 기능
                with st.form("verify_partner"):
                    verify_id = st.text_input(T[LANG]["verify_input"])
                    submitted = st.form_submit_button(T[LANG]["verify_btn"])
                    if submitted and verify_id:
                        supabase.table("publishers").update({"is_verified": True}).eq("id", verify_id).execute()
                        st.success(T[LANG]["verify_success"])
                        st.rerun()
        
        st.divider()
        st.subheader(T[LANG]["all_partners"])
        st.dataframe(pubs)
    else:
        st.info(T[LANG]["no_partners"])

# ==========================================
# 3. 광고주/소재 관리 - 광고 등록 및 예산 충전
# ==========================================
elif menu == T[LANG]["menu_ads"]:
    st.title(T[LANG]["title_ads"])
    
    # 데이터 로딩
    ads_df = load_data("advertisers")
    
    # 1. 현황판 출력
    st.subheader(T[LANG]["curr_balance"])
    if not ads_df.empty:
        # 필요한 컬럼만 선택해서 표시
        display_cols = ['brand_name', 'balance', 'cpc_bid', 'keywords']
        # 컬럼 존재 여부 확인 후 선택
        valid_cols = [c for c in display_cols if c in ads_df.columns]
        st.dataframe(ads_df[valid_cols])
    else:
        st.info(T[LANG]["no_advertisers"])

    st.divider()

    # 2. 예산 충전 기능 (무통장 입금 확인 후 사장님이 실행)
    st.subheader(T[LANG]["charge_sec"])
    if not ads_df.empty:
        with st.form("charge_form"):
            target_brand = st.selectbox(T[LANG]["charge_select"], ads_df['brand_name'].tolist())
            amount = st.number_input(T[LANG]["charge_amount"], min_value=1000, step=1000)
            memo = st.text_input(T[LANG]["charge_memo"], "0월 광고비 입금 확인")
            
            if st.form_submit_button(T[LANG]["charge_btn"]):
                try:
                    target_row = ads_df[ads_df['brand_name'] == target_brand].iloc[0]
                    ad_id = target_row['id']
                    old_bal = int(target_row['balance']) if pd.notna(target_row['balance']) else 0
                    
                    # 1. 잔액 업데이트
                    supabase.table("advertisers").update({"balance": old_bal + amount}).eq("id", ad_id).execute()
                    
                    # 2. 거래 기록
                    supabase.table("transactions").insert({
                        "advertiser_id": ad_id,
                        "amount": amount,
                        "type": "deposit",
                        "description": memo
                    }).execute()
                    
                    st.success(f"✅ '{target_brand}' + {amount:,} KRW")
                    st.rerun()
                except Exception as e:
                    st.error(f"{T[LANG]['charge_fail']}: {e}")
    else:
        st.warning(T[LANG]["no_advertisers"])

    st.divider()
    
    # 3. 온라인 결제 연동 테스트 (Toss / PayPal)
    st.subheader(T[LANG]["charge_online"])
    
    # [설정] API 기본 주소 (배포된 Vercel 서버 주소)
    # 로컬에서 테스트할 때는 "http://localhost:8000"으로 설정하세요.
    API_BASE_URL = os.environ.get("API_BASE_URL", "https://a-sense-project.vercel.app")

    if not ads_df.empty:
        target_ad_idx = st.selectbox("Select Advertiser (Online)", range(len(ads_df)), format_func=lambda x: ads_df.iloc[x]['brand_name'])
        target_ad = ads_df.iloc[target_ad_idx]
        
        pay_amount = st.number_input("Amount (KRW)", min_value=1000, step=1000, key="pay_amt")
        
        # Toss Payment JS
        # [보안] 환경 변수에서 키를 가져오며, 없을 경우 테스트 키 사용
        toss_client_key = os.environ.get("TOSS_CLIENT_KEY", "test_ck_D5GePWvyJnrK0W0k6q8gLzN97Eqa")
        
        # PayPal Client ID (Sandbox)
        paypal_client_id = os.environ.get("PAYPAL_CLIENT_ID", "test")

        # Generate unique orderId
        order_id = f"{target_ad['id']}_{int(datetime.now().timestamp())}"
        
        payment_html = f"""
        <head>
          <script src="https://js.tosspayments.com/v1/payment"></script>
          <script src="https://www.paypal.com/sdk/js?client-id={paypal_client_id}&currency=USD"></script>
        </head>
        <body>
          <h3>Select Payment Method</h3>
          
          <!-- Toss Payment -->
          <button id="toss-btn" style="padding:10px; background-color:#0064FF; color:white; border:none; border-radius:4px; cursor:pointer;">
            Toss Payment (KRW {pay_amount})
          </button>
          
          <br><br>
          
          <!-- PayPal -->
          <div id="paypal-button-container"></div>

          <script>
            // 1. Toss Payments
            const tossPayments = TossPayments("{toss_client_key}");
            const button = document.getElementById("toss-btn");
            
            button.addEventListener("click", function () {{
              tossPayments.requestPayment("카드", {{
                amount: {pay_amount},
                orderId: "{order_id}",
                orderName: "Ad Budget Charge ({target_ad['brand_name']})",
                customerName: "{target_ad['brand_name']}",
                successUrl: "{API_BASE_URL}/api/payment/toss/success", 
                failUrl: "{API_BASE_URL}/api/payment/toss/fail",
              }});
            }});

            // 2. PayPal
            paypal.Buttons({{
                createOrder: function(data, actions) {{
                    return actions.order.create({{
                        purchase_units: [{{
                            amount: {{
                                value: '{pay_amount / 1300:.2f}' // Approx USD conversion
                            }}
                        }}]
                    }});
                }},
                onApprove: function(data, actions) {{
                    // Call backend to capture
                    return fetch('{API_BASE_URL}/api/payment/paypal/capture', {{
                        method: 'post',
                        headers: {{
                            'content-type': 'application/json'
                        }},
                        body: JSON.stringify({{
                            orderID: data.orderID,
                            advertiserID: "{target_ad['id']}"
                        }})
                    }}).then(function(res) {{
                        return res.json();
                    }}).then(function(details) {{
                        alert('Transaction completed by ' + details.payer.name.given_name);
                    }});
                }}
            }}).render('#paypal-button-container');
          </script>
        </body>
        """
        components.html(payment_html, height=300)

    st.divider()

    st.subheader(T[LANG]["new_ad_sec"])
    with st.form("new_ad"):
        c1, c2 = st.columns(2)
        brand = c1.text_input(T[LANG]["ad_brand"])
        bid = c2.number_input(T[LANG]["ad_bid"], value=500)
        copy = st.text_area(T[LANG]["ad_copy"])
        link = st.text_input(T[LANG]["ad_url"], "https://...")
        keywords = st.text_input(T[LANG]["ad_kw"])
        
        submitted = st.form_submit_button(T[LANG]["ad_submit"])
        if submitted:
            kw_list = [k.strip() for k in keywords.split(",")]
            try:
                supabase.table("advertisers").insert({
                    "brand_name": brand,
                    "cpc_bid": bid,
                    "ad_copy": copy,
                    "landing_url": link,
                    "keywords": kw_list,
                    "ad_type": "cpc",
                    "balance": 0 # 초기 잔액 0
                }).execute()
                st.success(T[LANG]["ad_success"])
                st.rerun()
            except Exception as e:
                st.error(f"등록 실패: {e}")

# ==========================================
# 4. 부정 클릭 분석 - 보안 로그
# ==========================================
elif menu == T[LANG]["menu_fraud"]:
    st.title(T[LANG]["title_fraud"])
    
    logs = load_data("logs")
    if not logs.empty:
        if 'is_valid' in logs.columns:
            fraud_logs = logs[logs['is_valid'] == False]
            st.warning(f"{T[LANG]['fraud_count']} {len(fraud_logs)}")
            
            # 부정 사유별 통계
            if not fraud_logs.empty:
                if 'invalid_reason' in logs.columns:
                    reason_counts = fraud_logs['invalid_reason'].value_counts()
                    st.bar_chart(reason_counts)
                
                st.subheader(T[LANG]["fraud_detail"])
                display_cols = ['timestamp', 'platform', 'user_ip', 'invalid_reason']
                # 존재하는 컬럼만 선택
                valid_cols = [c for c in display_cols if c in fraud_logs.columns]
                st.dataframe(fraud_logs[valid_cols])
    else:
        st.info("로그 데이터가 없습니다.")
