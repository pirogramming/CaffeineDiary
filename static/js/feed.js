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
    // 백엔드가 내려주는 next("/signup/profile")는 실제로 등록된 페이지 경로가
    // 아니라(spec용 placeholder) 실제 설문 화면인 /initial_survey/로 보낸다.
    window.location.href = '/initial_survey/';
    return;
  }
  if (!res.ok) return;

  const data = await res.json();
  el.textContent = data.cutoff_at ? formatCutoffTime(data.cutoff_at) : '-';
}

loadCutoffTime();

// 즐겨찾는 음료(최대 3개)를 작은 컵 버튼 3개에 매핑한다. 슬롯보다 즐겨찾기가
// 적으면 남는 슬롯은 숨긴다.
async function loadFavoriteCups() {
  const slots = document.querySelectorAll('#cd-feed-fav-row .cd-feed-fav-slot');
  if (!slots.length) return;

  const res = await apiFetch('/users/me/drinks/');
  const list = res.ok ? await res.json() : [];
  const favorites = list.filter((d) => d.is_favorite).slice(0, slots.length);

  slots.forEach((slot, i) => {
    const drink = favorites[i];
    if (!drink) {
      slot.hidden = true;
      return;
    }
    const btn = slot.querySelector('.cd-feed-cup');
    const icon = slot.querySelector('.cd-feed-cup__icon');
    const name = slot.querySelector('.cd-feed-cup__name');
    icon.src = cdIconForDrink(drink);
    icon.alt = drink.name;
    name.textContent = drink.name;
    btn.setAttribute('aria-label', `즐겨찾는 음료 — ${drink.name}`);
    btn.dataset.drinkId = drink.id;
    slot.hidden = false;
  });
}

loadFavoriteCups();

// TODO: 실제 연결 시 POST /caffeine-logs 로 교체
document.getElementById('cd-feed-drink-btn')?.addEventListener('click', () => {
  console.log('한잔 마시기 클릭 — 카페인 로그 생성 API 연결 예정');
});

// TODO: 실제 연결 시 POST /caffeine-logs 로 교체 (drink.dataset.drinkId 사용)
document.getElementById('cd-feed-fav-row')?.addEventListener('click', (e) => {
  const btn = e.target.closest('.cd-feed-cup');
  if (!btn || !btn.dataset.drinkId) return;
  console.log('즐겨찾는 음료 클릭 — drink_id=' + btn.dataset.drinkId + ', 카페인 로그 생성 API 연결 예정');
});

document.getElementById('cd-feed-custom-drink-btn')?.addEventListener('click', () => {
  console.log('커스텀 마시기 클릭 — 음료 선택 플로우 연결 예정');
});