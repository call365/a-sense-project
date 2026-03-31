document.addEventListener('DOMContentLoaded', () => {
    // 1. Detect Language
    let lang = localStorage.getItem('lang');
    if (!lang) {
        // Default to English if browser is not Korean
        const browserLang = navigator.language || navigator.userLanguage; 
        lang = browserLang.startsWith('ko') ? 'ko' : 'en';
        localStorage.setItem('lang', lang);
    }
    
    // 2. Initial Render
    applyLanguage(lang);

    // 3. Setup Toggle Button
    const toggleBtn = document.getElementById('lang-toggle');
    if(toggleBtn) {
        updateToggleButton(toggleBtn, lang);
        toggleBtn.onclick = (e) => {
            e.preventDefault();
            const currentLang = localStorage.getItem('lang');
            const newLang = currentLang === 'ko' ? 'en' : 'ko';
            setLanguage(newLang);
        };
    }
});

function setLanguage(newLang) {
    localStorage.setItem('lang', newLang);
    applyLanguage(newLang);
}

function applyLanguage(lang) {
    document.documentElement.lang = lang;
    
    // Update all elements with data-i18n attribute
    const elements = document.querySelectorAll('[data-i18n]');
    elements.forEach(el => {
        const key = el.getAttribute('data-i18n');
        if (translations[lang] && translations[lang][key]) {
            el.innerHTML = translations[lang][key];
        }
    });
    
    // Update Toggle Button Text
    const toggleBtn = document.getElementById('lang-toggle');
    if(toggleBtn) {
        updateToggleButton(toggleBtn, lang);
    }
}

function updateToggleButton(btn, lang) {
    // If current lang is KO, show option to switch to EN, and vice versa
    btn.innerHTML = lang === 'ko' ? '<i class="fas fa-globe"></i> EN' : '<i class="fas fa-globe"></i> KR';
}
