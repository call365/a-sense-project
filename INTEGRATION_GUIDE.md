# A-Sense 통합 연동 가이드 (Integration Guide)

A-Sense는 **HTTP 표준 프로토콜**을 기반으로 설계되어, 인터넷 연결이 가능한 모든 플랫폼과 호환됩니다.  
이 문서는 다양한 AI 플랫폼 및 애플리케이션 개발자를 위한 연동 방법을 설명합니다.

---

## 1. 호환 가능한 플랫폼 리스트

| AI 플랫폼 | 연동 방식 | 난이도 | 비고 |
| :--- | :--- | :--- | :--- |
| **OpenAI (ChatGPT)** | Actions (JSON 스키마) | ★☆☆ (쉬움) | GPT Store 챗봇 수익화 |
| **Anthropic (Claude)** | Tool Use (API 호출) | ★★☆ (보통) | API 사용자 대상 |
| **뤼튼 (Wrtn)** | 플러그인 / 스튜디오 | ★☆☆ (쉬움) | 국내 플랫폼 |
| **LangChain** | Python `requests` | ★☆☆ (쉬움) | 자체 개발 LLM 애플리케이션 |
| **카카오톡 챗봇** | 스킬 서버 (API 연동) | ★★☆ (보통) | 옐로우아이디 / 비즈니스 |
| **No-Code 툴** | Zapier, Make (HTTP) | ★☆☆ (쉬움) | 자동화 워크플로우 |

---

## 2. 범용 API 호출 가이드

어떤 언어, 어떤 환경에서도 아래 엔드포인트로 **HTTP POST** 요청을 보내면 됩니다.

### 기본 정보
- **Endpoint**: `https://your-api.vercel.app/api/v1/get-ad`
- **Method**: `POST`
- **Content-Type**: `application/json`
- **Header**: `x-api-key: YOUR_API_KEY` (발급받은 키 입력)

### cURL 예시 (터미널/범용)
전 세계 개발자 공통어인 cURL 명령어입니다.

```bash
curl -X POST "https://your-api.vercel.app/api/v1/get-ad" \
     -H "Content-Type: application/json" \
     -H "x-api-key: YOUR_API_KEY" \
     -d '{
           "keywords": ["여행", "휴가"],
           "platform": "generic_app"
         }'
```

---

## 3. Python 개발자를 위한 연동 (자체 앱/웹)

Python으로 챗봇이나 앱을 직접 개발하는 경우(대학생, 스타트업 등), `requests` 라이브러리를 사용하여 단 한 줄로 연동 가능합니다.

```python
import requests

# 1. 사용자 대화에서 키워드 추출 (예: ["맛집", "강남역"])
user_keywords = ["맛집", "강남역"]

# 2. A-Sense API 호출
try:
    response = requests.post(
        "https://your-api.vercel.app/api/v1/get-ad",
        headers={"x-api-key": "SK_LIVE_YOUR_KEY"},
        json={
            "keywords": user_keywords,
            "platform": "python_app"
        }
    ).json()

    # 3. 응답 처리 및 광고 표시
    if "ad_copy" in response:
        print(f"[광고] {response['brand']}: {response['ad_copy']}")
        print(f"👉 링크: {response['link']}")
    else:
        print("광고가 없습니다.")

except Exception as e:
    print(f"광고 로드 실패: {e}")
```

---

## 4. 광고주를 위한 보안 시스템 (Triple-Shield)

A-Sense는 광고주의 예산을 보호하기 위해 **3단계 부정 클릭 방지 시스템(Triple-Shield)**을 운영합니다.

1.  **🤖 봇 필터링 (Bot Filtering)**
    *   검색 엔진 크롤러, 스크립트 봇 등 비정상적인 User-Agent를 감지하여 차단합니다.
2.  **🔄 중복 클릭 방지 (Anti-Duplicate)**
    *   동일 IP에서 일정 시간(1시간) 내에 발생한 반복 클릭은 과금하지 않습니다.
3.  **⚡ 광속 클릭 차단 (Speed Click Guard)**
    *   광고 노출 후 **0.5초 미만**에 발생하는 기계적 클릭을 무효화합니다. (사람은 내용을 읽고 클릭하는 데 최소한의 시간이 필요합니다.)

> **투명한 리포트 제공**: 모든 클릭 로그는 기록되며, 대시보드에서 '유효 클릭(Valid)'과 '무효 클릭(Invalid)'을 투명하게 구분하여 제공합니다.

---

## 5. OpenAI GPTs 연동 (Actions)

GPT Store에 챗봇을 출시할 때는 `gpt_action_schema.json` 파일의 내용을 복사하여 **Actions** 설정에 붙여넣으세요.

1.  GPT Builder > Configure > Actions > Create new action 선택
2.  Schema 입력란에 `gpt_action_schema.json` 내용 붙여넣기
3.  Authentication Type: API Key (Header: `x-api-key`) 선택
