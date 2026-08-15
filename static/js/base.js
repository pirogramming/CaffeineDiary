/**
 * base.js — 로그인 후 화면 공통 헤더(base.html 및 밤샘모드 화면)에서 쓰는 스크립트.
 * 로그아웃 버튼에 실제 동작을 연결한다.
 */

function getCookie(name) {
  return document.cookie
    .split('; ')
    .find(row => row.startsWith(name + '='))
    ?.split('=')[1] ?? null;
}

document.getElementById('cd-logout-btn')?.addEventListener('click', async () => {
  // 로그인/회원가입 응답에서 세션과 함께 csrftoken도 발급되지만,
  // 혹시 없는 상태로 이 페이지에 온 경우를 대비해 세션 확인 API로 보장한다.
  if (!getCookie('csrftoken')) {
    await fetch('/auth/session/', { credentials: 'same-origin' });
  }

  const res = await fetch('/auth/logout/', {
    method: 'POST',
    credentials: 'same-origin',
    headers: {
      Accept: 'application/json',
      'X-CSRFToken': getCookie('csrftoken'),
    },
  });

  const data = await res.json().catch(() => ({}));
  window.location.href = data.next || '/auth/login';
});
