document.addEventListener('DOMContentLoaded', () => {
    checkAuthUI();
});

function checkAuthUI() {
    const user = localStorage.getItem('ad_user');
    const dashboardBtn = document.getElementById('nav-dashboard');
    const loginBtn = document.getElementById('nav-login');

    if (user) {
        // [로그인 상태]
        // 1. 대시보드 버튼 보이기
        if (dashboardBtn) dashboardBtn.style.display = 'inline-flex';
        
        // 2. 로그인 버튼을 '로그아웃' 버튼으로 변경
        if (loginBtn) {
            loginBtn.style.display = 'inline-flex';
            loginBtn.setAttribute('data-i18n', 'nav.logout'); // 다국어 키 변경
            loginBtn.innerText = '로그아웃'; // 기본 텍스트 변경 (i18n 로드 전 대비)
            loginBtn.href = "#";
            loginBtn.onclick = (e) => {
                e.preventDefault();
                logout();
            };
        }
    } else {
        // [비로그인 상태]
        // 1. 대시보드 버튼 숨기기
        if (dashboardBtn) dashboardBtn.style.display = 'none';
        
        // 2. 로그인 버튼은 HTML 기본 상태 유지 (로그인 링크)
        if (loginBtn) {
            loginBtn.style.display = 'inline-flex';
            // 만약 JS로 텍스트가 변경된 상태라면 복구할 필요가 없지만(새로고침 하므로),
            // SPA 동작을 대비해 명시적으로 복구 가능. 하지만 현재 구조상 불필요.
        }
    }

    // 언어 설정이 있다면 텍스트 갱신 (i18n.js의 applyLanguage 활용)
    if (typeof applyLanguage === 'function') {
        const lang = localStorage.getItem('lang') || 'ko';
        applyLanguage(lang);
    }
}

function logout() {
    if(confirm('로그아웃 하시겠습니까?')) {
        localStorage.removeItem('ad_user');
        location.reload(); // 새로고침하여 UI 초기화
    }
}
