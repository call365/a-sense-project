-- [A-Sense] 전체 데이터베이스 초기화 및 테이블 생성 스크립트
-- 이 스크립트는 모든 테이블을 처음부터 생성합니다.
-- Supabase SQL Editor에서 이 코드를 실행하세요.

-- 0. 필수 확장 설치
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS "pgcrypto";

-- 1. 광고주 계정 (로그인용)
CREATE TABLE IF NOT EXISTS advertiser_users (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  email TEXT UNIQUE NOT NULL,
  password_hash TEXT NOT NULL,
  company_name TEXT,
  balance BIGINT DEFAULT 0,
  created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- 2. 광고 소재 및 캠페인 (Advertisers)
CREATE TABLE IF NOT EXISTS advertisers ( 
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(), 
  brand_name TEXT NOT NULL, 
  ad_copy TEXT NOT NULL, 
  landing_url TEXT NOT NULL, 
  keywords TEXT[] DEFAULT '{}', 
  cpc_bid INT DEFAULT 500, 
  lang TEXT DEFAULT 'en',
  created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
  owner_id UUID REFERENCES advertiser_users(id),
  ad_type TEXT DEFAULT 'cpc',
  cpa_bid INT DEFAULT 0,
  target_action TEXT,
  balance BIGINT DEFAULT 0
); 

-- 3. 매체사 (Publishers)
CREATE TABLE IF NOT EXISTS publishers ( 
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(), 
  name TEXT NOT NULL, 
  api_key TEXT NOT NULL UNIQUE, 
  platform_type TEXT NOT NULL, 
  pref_lang TEXT DEFAULT 'en',
  verification_token TEXT,
  is_verified BOOLEAN DEFAULT FALSE,
  web_domain TEXT,
  bank_name TEXT,
  account_number TEXT,
  account_holder TEXT,
  created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW() 
); 

-- 4. 성과 로그 (Logs)
CREATE TABLE IF NOT EXISTS logs ( 
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(), 
  type TEXT NOT NULL, -- 'impression', 'click' 
  platform TEXT NOT NULL, 
  publisher_id UUID REFERENCES publishers(id), 
  advertiser_id UUID REFERENCES advertisers(id), 
  user_ip TEXT, 
  is_valid BOOLEAN DEFAULT TRUE,
  invalid_reason TEXT,
  timestamp TIMESTAMP WITH TIME ZONE DEFAULT NOW() 
);

-- 5. 거래 내역 (Transactions)
CREATE TABLE IF NOT EXISTS transactions ( 
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(), 
  advertiser_id UUID REFERENCES advertisers(id), 
  amount BIGINT NOT NULL, 
  currency TEXT DEFAULT 'KRW',
  type TEXT NOT NULL, -- 'deposit', 'spend'
  provider TEXT, -- 'toss', 'paypal'
  payment_key TEXT,
  description TEXT, 
  created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW() 
); 

-- 6. 인출 요청 (Payout Requests)
CREATE TABLE IF NOT EXISTS payout_requests (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  publisher_id UUID REFERENCES publishers(id),
  amount BIGINT NOT NULL,
  status TEXT DEFAULT 'pending',
  requested_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
  processed_at TIMESTAMP WITH TIME ZONE
); 

-- 7. 입금 기록 (Deposits - 보조 테이블)
CREATE TABLE IF NOT EXISTS deposits (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  advertiser_id UUID REFERENCES advertiser_users(id),
  amount BIGINT NOT NULL,
  method TEXT DEFAULT 'bank_transfer',
  status TEXT DEFAULT 'completed',
  created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- 8. 전환 로그 (Conversions)
CREATE TABLE IF NOT EXISTS conversions (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  log_id UUID REFERENCES logs(id),
  amount INT NOT NULL,
  created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- 9. 권한 부여 (API 접근용)
GRANT ALL ON TABLE advertiser_users TO anon, authenticated, service_role;
GRANT ALL ON TABLE advertisers TO anon, authenticated, service_role;
GRANT ALL ON TABLE publishers TO anon, authenticated, service_role;
GRANT ALL ON TABLE logs TO anon, authenticated, service_role;
GRANT ALL ON TABLE transactions TO anon, authenticated, service_role;
GRANT ALL ON TABLE payout_requests TO anon, authenticated, service_role;
GRANT ALL ON TABLE deposits TO anon, authenticated, service_role;
GRANT ALL ON TABLE conversions TO anon, authenticated, service_role;
