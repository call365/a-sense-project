TOSS_CLIENT_KEY=live_ck_GKNbdOvk5rkdPyao0eA8n07xlzmj
TOSS_SECRET_KEY=live_sk_... (내 토스 시크릿 키)
PAYPAL_CLIENT_ID=...
PAYPAL_SECRET=...# A-Sense 결제 및 환경 변수 설정 가이드

A-Sense 프로젝트의 결제(Toss, PayPal) 및 DB 연결을 위한 API Key 설정 방법입니다.

## 1. 키 발급 방법

### 💳 토스페이먼츠 (Toss Payments) - 국내 결제
1. **[토스페이먼츠 개발자센터](https://developers.tosspayments.com/)** 접속 및 로그인
2. **내 개발 정보 > API 키** 메뉴 이동
3. **Client Key (클라이언트 키)** 와 **Secret Key (시크릿 키)** 확인
   - 개발 중에는 `test_ck_...`, `test_sk_...` (테스트용) 사용
   - 실서비스 오픈 시 `live_ck_...`, `live_sk_...` (라이브용) 사용

### 🌏 페이팔 (PayPal) - 해외 결제
1. **[PayPal Developer Dashboard](https://developer.paypal.com/dashboard/)** 접속 및 로그인
2. **Apps & Credentials** 메뉴 이동
3. **Create App** 클릭하여 새 앱 생성
4. **Client ID** 와 **Secret** 확인
   - Sandbox (테스트) 모드와 Live (실서비스) 모드 구분하여 사용

---

## 2. 키 입력 위치 (환경 변수 설정)

보안을 위해 API Key는 코드에 직접 적지 않고 **환경 변수**로 관리합니다.

### 🖥️ 로컬 개발 환경 (Localhost)
프로젝트 루트 폴더(`a-sense-project/`)의 `.env` 파일에 아래 내용을 작성합니다.
(`.env.example` 파일을 복사하여 `.env`로 이름을 변경하세요)

```ini
# Supabase (DB 설정)
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_KEY=your-anon-key-here

# 관리자 비밀번호
ADMIN_PASSWORD=your_secure_password

# Toss Payments (토스)
# 클라이언트 키: 대시보드(프론트엔드)에서 사용
TOSS_CLIENT_KEY=test_ck_D5GePWvyJnrK0W0k6q8gLzN97Eoq
# 시크릿 키: API 서버(백엔드)에서 결제 승인 시 사용
TOSS_SECRET_KEY=test_sk_zXLkKEypNArWmo50nX3lmeaxYG5R

# PayPal (페이팔)
PAYPAL_CLIENT_ID=your_paypal_client_id
PAYPAL_SECRET=your_paypal_secret_key
```

### ☁️ 배포 환경 (Vercel)
Vercel에 배포한 경우, 대시보드에서 환경 변수를 등록해야 합니다.

1. Vercel 프로젝트 페이지 이동
2. **Settings** > **Environment Variables** 메뉴 클릭
3. 아래 키-값 쌍을 하나씩 추가 (`Key`, `Value` 입력 후 Add 클릭)

| Key (키 이름) | Value (값 예시) | 설명 |
|---|---|---|
| `SUPABASE_URL` | `https://xyz.supabase.co` | Supabase 프로젝트 URL |
| `SUPABASE_KEY` | `eyJhbGciOi...` | Supabase Anon Key |
| `ADMIN_PASSWORD` | `admin1234` | 관리자 페이지 접속 비밀번호 |
| `TOSS_CLIENT_KEY` | `live_ck_GKNbdOvk5rkdPyao0eA8n07xlzmj` | 토스 클라이언트 키 |
| `TOSS_SECRET_KEY` | `live_sk_...` | 토스 시크릿 키 |
| `PAYPAL_CLIENT_ID` | `Af...` | 페이팔 Client ID |
| `PAYPAL_SECRET` | `ED...` | 페이팔 Secret |
| `API_BASE_URL` | `https://your-app.vercel.app` | 배포된 웹사이트 주소 |

---

## 3. 주의사항
- **절대 Secret Key를 코드에 직접 노출하지 마세요.** (GitHub 등에 올라가면 해킹 위험)
- 테스트가 끝나면 **Live(라이브) 키**로 교체해야 실제 결제가 이루어집니다.
- 배포 후 환경 변수를 변경하면 **Redeploy(재배포)** 해야 적용됩니다.
