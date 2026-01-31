import requests
import json

# 로컬 서버 주소
BASE_URL = "http://localhost:8000"

def test_chatbot_ad_request():
    # API 엔드포인트 변경됨: /api/v1/get-ad
    url = f"{BASE_URL}/api/v1/get-ad"
    
    # 헤더에 API Key 포함
    headers = {
        "x-api-key": "test-api-key"
    }
    
    # 요청 데이터
    payload = {
        "platform": "chatbot",
        "keywords": ["다이어트", "운동"] # 키워드 매칭 테스트용
    }

    try:
        print(f"Sending request to {url}...")
        response = requests.post(url, headers=headers, json=payload)
        
        if response.status_code == 200:
            data = response.json()
            print("\n[성공] 광고 데이터를 수신했습니다:")
            print(json.dumps(data, indent=2, ensure_ascii=False))
        else:
            print(f"\n[오류] 상태 코드: {response.status_code}")
            print(response.text)
            
    except requests.exceptions.ConnectionError:
        print(f"\n[연결 실패] 서버가 실행 중인지 확인하세요. ({BASE_URL})")

if __name__ == "__main__":
    test_chatbot_ad_request()
