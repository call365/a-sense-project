-- 1. 광고 소재 테이블 (매칭 엔진이 참조할 키워드 포함)
create table advertisers ( 
  id uuid default gen_random_uuid() primary key, 
  brand_name text not null, 
  ad_copy text not null,          -- AI 추천 문구 
  landing_url text not null,       -- 이동할 링크 
  keywords text[] default '{}',   -- 매칭용 키워드 (예: ["다이어트", "운동"]) 
  cpc_bid int default 500,        -- 클릭당 단가 
  lang text default 'en',         -- [New] 광고 언어 타겟팅 (en, ko, ja 등)
  created_at timestamp with time zone default now(),
  -- [New] 광고주 기능 추가
  owner_id uuid references advertiser_users(id),
  ad_type text default 'cpc',     -- 'cpc' or 'cpa'
  cpa_bid int default 0,          -- CPA 단가 (전환당 비용)
  target_action text,             -- 'signup', 'purchase' 등 전환 기준
  balance int default 0           -- [New] 광고주 잔액 추가
); 

-- 8. [New] 입출금 내역 기록용 테이블 (회계 증빙용)
create table transactions ( 
  id uuid default gen_random_uuid() primary key, 
  advertiser_id uuid references advertisers(id), 
  amount int not null,           -- 충전이면 +, 차감이면 - 
  currency text default 'USD',   -- [New] 통화 단위 (USD, KRW)
  type text not null,            -- 'deposit'(충전), 'spend'(광고비) 
  description text,              -- 메모 (예: 1월 광고비 입금) 
  created_at timestamp with time zone default now() 
); 

-- 2. 매체사 테이블 (GPTs 제작자, 웹 운영자 등) 
create table publishers ( 
  id uuid default gen_random_uuid() primary key, 
  name text not null, 
  api_key text not null unique,   -- 매체 고유 식별 키 
  platform_type text not null,    -- 'chatbot', 'web', 'app' 
  pref_lang text default 'en',    -- [New] 선호 언어
  verification_token text,
  is_verified boolean default false,
  web_domain text,  -- 웹사이트 보안을 위한 도메인 화이트리스트
  bank_name text,   -- 정산용 은행명
  account_number text, -- 정산용 계좌번호
  account_holder text, -- 예금주명
  created_at timestamp with time zone default now() 
); 

-- 4. 인출 요청 테이블
create table payout_requests (
  id uuid default gen_random_uuid() primary key,
  publisher_id uuid references publishers(id),
  amount int not null,
  status text default 'pending', -- pending, paid, rejected
  requested_at timestamp with time zone default now(),
  processed_at timestamp with time zone
); 

-- 3. 성과 통합 로그 테이블 
create table logs ( 
  id uuid default gen_random_uuid() primary key, 
  type text not null,             -- 'impression', 'click' 
  platform text not null, 
  publisher_id uuid references publishers(id), 
  advertiser_id uuid references advertisers(id), 
  user_ip text,                   -- 어뷰징 방지용 
  is_valid boolean default true,
  invalid_reason text,
  timestamp timestamp with time zone default now() 
);

-- 5. 광고주 계정 (Advertiser Users)
create table advertiser_users (
  id uuid default gen_random_uuid() primary key,
  email text unique not null,
  password_hash text not null,
  company_name text,
  balance int default 0,
  created_at timestamp with time zone default now()
);

-- 6. 충전/결제 내역 (Deposits)
create table deposits (
  id uuid default gen_random_uuid() primary key,
  advertiser_id uuid references advertiser_users(id),
  amount int not null,
  method text default 'bank_transfer',
  status text default 'completed',
  created_at timestamp with time zone default now()
);

-- 7. 전환(CPA) 로그 (Conversions)
create table conversions (
  id uuid default gen_random_uuid() primary key,
  log_id uuid references logs(id), -- 클릭 로그와 연결
  amount int not null, -- CPA 단가
  created_at timestamp with time zone default now()
);
