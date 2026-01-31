-- 테스트용 데이터 시드 (SQL Editor에서 실행)

-- 1. 광고주 추가
insert into advertisers (brand_name, ad_copy, landing_url, keywords, cpc_bid)
values 
('ASense Coffee', '지친 오후, 프리미엄 커피 한 잔 어때요?', 'https://example.com/coffee', '{"커피", "휴식"}', 600),
('Fast Diet', '3주 완성 다이어트 프로그램', 'https://example.com/diet', '{"다이어트", "운동"}', 800);

-- 2. 매체사 추가
-- (주의: 이 ID를 static/test_site.html의 data-pub-id와 test_chatbot.py의 x-api-key 로직에 맞춰 사용해야 함)
insert into publishers (name, api_key, platform_type)
values 
('My Chatbot', 'test-api-key', 'chatbot'),
('My Blog', 'web-api-key-123', 'web');

-- 확인용 쿼리
-- select * from advertisers;
-- select * from publishers;
