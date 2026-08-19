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
    // 단, 프로필이 없는 계정을 곧장 /feed/로 보내면 feed.js가 /feed-status/에서
    // 404(PROFILE_NOT_FOUND)를 받고 다시 튕겨나가므로 여기서 먼저 걸러낸다.
    // 기존 '/sleep-logs'는 페이지가 아니라 API 경로라 브라우저로 들어가면 깨진다.
    if (mode === 'signup') {
        // "회원가입 → feed 진입" 흐름이라는 표시를 남겨둔다. sleep-logs/time·rating을
        // 포함한 초기 설문 흐름을 다 거쳐 /feed/에 도착했을 때 온보딩 투어(tour.js)가
        // 뜨게 하려는 것 — daily_rating.js가 이 값을 보고 /feed/?first_visit=1로
        // 보낸 뒤 이 표시를 지운다.
        sessionStorage.setItem('cd_pending_tour', '1');
        window.location.href = '/initial_survey';
    } else {
        window.location.href = data.has_profile ? '/feed/' : '/initial_survey';
    }
});