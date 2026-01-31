-- [A-Sense] DB Schema Update for Payment & Verification

-- 1. Advertisers Table Update
ALTER TABLE advertisers ADD COLUMN IF NOT EXISTS balance BIGINT DEFAULT 0;
ALTER TABLE advertisers ADD COLUMN IF NOT EXISTS lang TEXT DEFAULT 'en';
ALTER TABLE advertisers ADD COLUMN IF NOT EXISTS landing_url TEXT;

-- 2. Publishers Table Update
ALTER TABLE publishers ADD COLUMN IF NOT EXISTS verification_token TEXT;
ALTER TABLE publishers ADD COLUMN IF NOT EXISTS is_verified BOOLEAN DEFAULT FALSE;
ALTER TABLE publishers ADD COLUMN IF NOT EXISTS bank_name TEXT;
ALTER TABLE publishers ADD COLUMN IF NOT EXISTS account_number TEXT;
ALTER TABLE publishers ADD COLUMN IF NOT EXISTS account_holder TEXT;

-- 3. Transactions Table (New)
CREATE TABLE IF NOT EXISTS transactions (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    advertiser_id TEXT REFERENCES advertisers(id),
    amount BIGINT NOT NULL,
    type TEXT NOT NULL, -- 'deposit', 'click_cost', 'withdrawal'
    description TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- 4. Payout Requests Table (New)
CREATE TABLE IF NOT EXISTS payout_requests (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    publisher_id TEXT REFERENCES publishers(id),
    amount BIGINT NOT NULL,
    status TEXT DEFAULT 'pending', -- 'pending', 'paid', 'rejected'
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- 5. Deposits Table (New - for record keeping)
CREATE TABLE IF NOT EXISTS deposits (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    advertiser_id TEXT, -- Can be linked to advertiser_users or advertisers
    amount BIGINT NOT NULL,
    status TEXT DEFAULT 'completed',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- 6. Advertiser Users Table (New - for login)
CREATE TABLE IF NOT EXISTS advertiser_users (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    email TEXT UNIQUE NOT NULL,
    password_hash TEXT NOT NULL,
    company_name TEXT,
    balance BIGINT DEFAULT 0,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);
