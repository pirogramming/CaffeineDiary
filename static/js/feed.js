/* feed.js — "나의 다이어리" 메인 화면 (/feed/) 전용 스크립트 */

function formatCutoffTime(isoString) {
  return new Date(isoString).toLocaleTimeString('ko-KR', {
    timeZone: 'Asia/Seoul',
    hour: 'numeric',
    minute: '2-digit',
    hour12: false,
  });
}

async function loadCutoffTime() {
  const el = document.getElementById('cd-feed-cutoff-time');
  if (!el) return;

  const res = await apiFetch('/feed-status/?compact=true');
  if (res.status === 404) {
    const data = await res.json().catch(() => ({}));
    window.location.href = data.next || '/signup/profile';
    return;
  }
  if (!res.ok) return;

  const data = await res.json();
  el.textContent = data.cutoff_at ? formatCutoffTime(data.cutoff_at) : '-';
}

loadCutoffTime();

// TODO: 실제 연결 시 POST /caffeine-logs 로 교체
document.getElementById('cd-feed-drink-btn')?.addEventListener('click', () => {
  console.log('한잔 마시기 클릭 — 카페인 로그 생성 API 연결 예정');
});

document.getElementById('cd-feed-custom-drink-btn')?.addEventListener('click', () => {
  console.log('커스텀 마시기 클릭 — 음료 선택 플로우 연결 예정');
});