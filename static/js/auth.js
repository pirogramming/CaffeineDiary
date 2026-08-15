/**
 * auth.js — 로그인 / 회원가입 폼 공통 스크립트
 * apiFetch, getCookie는 base.js에서 오는 게 아니라 base.html을 상속하지
 * 않는 독립 페이지라 여기서 자체적으로 정의한다 (base.js와 내용은 동일).
 */

function getCookie(name) {
    return document.cookie
        .split('; ')
        .find(row => row.startsWith(name + '='))
        ?.split('=')[1] ?? null;
}

async function apiFetch(url, options = {}) {
    const method = (options.method ?? 'GET').toUpperCase();
    const headers = { Accept: 'application/json', ...options.headers };

    if (!['GET', 'HEAD', 'OPTIONS'].includes(method)) {
        headers['Content-Type'] = 'application/json';
        headers['X-CSRFToken'] = getCookie('csrftoken');
    }
    return fetch(url, { ...options, headers, credentials: 'same-origin' });
}

function showError(message) {
    const el = document.getElementById('cd-auth-error');
    if (!el) return;
    el.textContent = message;
    el.hidden = false;
}

function clearError() {
    const el = document.getElementById('cd-auth-error');
    if (!el) return;
    el.hidden = true;
    el.textContent = '';
}

const form = document.getElementById('cd-auth-form');

form?.addEventListener('submit', async (event) => {
    event.preventDefault();
    clearError();

    const mode = form.dataset.authMode; // 'signup' | 'login' — 각 템플릿의 extra_js에서 설정
    const username = form.querySelector('[name="username"]')?.value.trim();
    const password = form.querySelector('[name="password"]')?.value;

    if (!username || !password) {
        showError('아이디와 비밀번호를 모두 입력해주세요.');
        return;
    }

    // 공통 규칙: 두 엔드포인트 모두 끝에 슬래시가 붙는 DRF API다.
    const endpoint = mode === 'signup' ? '/auth/signup/' : '/auth/login/';

    const res = await apiFetch(endpoint, {
        method: 'POST',
        body: JSON.stringify({ username, password }),
    });

    const data = await res.json().catch(() => ({}));

    if (!res.ok) {
        showError(data.message || '요청을 처리하지 못했어요. 다시 시도해주세요.');
        return;
    }

    // 성공 시 이동 경로 — 로그인/회원가입 각각 고정 경로로 이동
    // (백엔드가 응답에 next를 내려주더라도, 지금은 이 고정 규칙을 우선한다)
    // 로그인은 메인피드 화면(명세상 "메인피드 조회" = GET /feed, 지금 diary:feed)으로 이동한다.
    // 기존 '/sleep-logs'는 페이지가 아니라 API 경로라 브라우저로 들어가면 깨진다.
    window.location.href = mode === 'signup' ? '/initial_survey' : '/feed/';
});
