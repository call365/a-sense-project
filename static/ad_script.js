(function() {
    // 1. 광고 영역 및 설정값 확인
    const adArea = document.getElementById("asense-ad-area");
    if (!adArea) return;

    const pubId = adArea.getAttribute("data-pub-id");
    
    // 기본적으로 배포된 서버 주소 사용 (Vercel)
    let serverUrl = "https://a-sense-project.vercel.app";
    
    // 로컬 테스트 환경인 경우 (예: test_site.html을 파일로 열거나 다른 포트에서 열 때) 
    // 명시적으로 로컬 API 서버 주소 지정
    if (window.location.hostname === "localhost" || window.location.hostname === "127.0.0.1") {
        // 만약 현재 페이지가 8000번 포트(백엔드 서버)가 아니라면 (예: 5500번 Live Server)
        // 백엔드 주소인 http://localhost:8000 을 가리키도록 설정
        if (window.location.port !== "8000") {
             serverUrl = "http://localhost:8000";
             console.log("ASense SDK: Local mode, connecting to " + serverUrl);
        }
    }

    // 키워드 추출: 문서 제목 + 메타 태그 키워드
    const keywords = [document.title];
    const metaKeywords = document.querySelectorAll('meta[name="keywords"]');
    if (metaKeywords) {
        metaKeywords.forEach(m => {
            if (m.content) keywords.push(m.content);
        });
    }

    // [New] 언어 감지
    const userLang = (navigator.language || navigator.userLanguage || "en").slice(0, 2);

    // 2. 광고 요청
    fetch(`${serverUrl}/api/v1/get-ad`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
            "platform": "web",
            "publisher_id": pubId,
            "keywords": keywords,
            "lang": userLang // 감지된 언어 전송
        })
    })
    .then(res => res.json())
    .then(data => {
        if (!data.link) return;

        // 3. 네이티브 UI 렌더링 (스타일 개선)
        adArea.innerHTML = `
            <div style="border:1px solid #eee; padding:20px; border-radius:12px; font-family:-apple-system,BlinkMacSystemFont,sans-serif; background:#fff; box-shadow:0 4px 6px rgba(0,0,0,0.05);">
                <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:10px;">
                    <span style="font-size:12px; font-weight:bold; color:#007aff; background:#e5f1ff; padding:2px 8px; border-radius:4px;">AI 추천</span>
                    <span style="font-size:12px; color:#999;">${data.brand}</span>
                </div>
                <p style="font-size:16px; line-height:1.5; color:#333; margin:0 0 15px 0;">${data.ad_copy}</p>
                <a href="${data.link}" target="_blank" style="display:block; text-align:center; background:#007aff; color:#fff; text-decoration:none; padding:12px; border-radius:8px; font-weight:bold; transition:0.2s;">자세히 보기</a>
            </div>
        `;
    })
    .catch(e => console.error("A-Sense Load Failed", e));
})();
