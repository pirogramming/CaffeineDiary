/**
 * base.js — 모든 화면 공통 스크립트.
 * base.html이 로드하며, 아래 함수들은 이 파일 이후에 로드되는
 * 페이지별 스크립트(extra_js 블록)에서도 전역으로 사용할 수 있다.
 */

/**
 * 쿠키 값을 이름으로 읽어온다.
 */
function getCookie(name) {
  return document.cookie
    .split('; ')
    .find(row => row.startsWith(name + '='))
    ?.split('=')[1] ?? null;
}

/**
 * fetch 래퍼. 상태를 변경하는 요청(GET/HEAD/OPTIONS 이외)에는
 * X-CSRFToken 헤더를 자동으로 실어 보낸다.
 */
async function apiFetch(url, options = {}) {
  const method = (options.method ?? 'GET').toUpperCase();
  const headers = { Accept: 'application/json', ...options.headers };

  if (!['GET', 'HEAD', 'OPTIONS'].includes(method)) {
    headers['Content-Type'] = 'application/json';
    headers['X-CSRFToken'] = getCookie('csrftoken');
  }
  return fetch(url, { ...options, headers, credentials: 'same-origin' });
}

// 상단 네비게이션의 로그아웃 버튼 — 모든 페이지에 공통으로 존재하므로 여기서 한 번만 연결
document.getElementById('cd-logout-btn')?.addEventListener('click', async () => {
  // 로그인/회원가입 응답에서 세션과 함께 csrftoken도 발급되지만,
  // 혹시 없는 상태로 이 페이지에 온 경우를 대비해 세션 확인 API로 보장한다.
  if (!getCookie('csrftoken')) {
    await fetch('/auth/session/', { credentials: 'same-origin' });
  }

  const res = await apiFetch('/auth/logout/', { method: 'POST' });
  const data = await res.json().catch(() => ({}));
  window.location.href = data.next || '/auth/login';
});

// 480px 미만에서만 보이는 햄버거 버튼 — 누르면 .cd-nav가 오른쪽에서 드로어로 열린다.
const navToggle = document.getElementById('cd-nav-toggle');
const nav = document.getElementById('cd-nav');
const navBackdrop = document.getElementById('cd-nav-backdrop');

function openNav() {
  nav.classList.add('is-open');
  navBackdrop.hidden = false;
  // hidden 속성을 지운 다음 프레임에 opacity 트랜지션이 걸리도록 한 박자 늦춰 클래스 부여
  requestAnimationFrame(() => navBackdrop.classList.add('is-open'));
  navToggle.setAttribute('aria-expanded', 'true');
}

function closeNav() {
  nav.classList.remove('is-open');
  navBackdrop.classList.remove('is-open');
  navToggle.setAttribute('aria-expanded', 'false');
  // 트랜지션(0.25s)이 끝난 뒤에 완전히 숨겨서, 사라지는 애니메이션이 잘리지 않게 한다.
  setTimeout(() => { navBackdrop.hidden = true; }, 250);
}

navToggle?.addEventListener('click', () => {
  const isOpen = navToggle.getAttribute('aria-expanded') === 'true';
  isOpen ? closeNav() : openNav();
});

navBackdrop?.addEventListener('click', closeNav);

// 드로어 안의 메뉴를 클릭해서 페이지 이동할 때도 자연스럽게 닫히도록
nav?.querySelectorAll('.cd-nav__link').forEach((link) => {
  link.addEventListener('click', closeNav);
});
