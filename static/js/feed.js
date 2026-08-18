/* feed.js — "나의 다이어리" 메인 화면 (/feed/) 전용 스크립트 */

function formatCutoffTime(isoString) {
  return new Date(isoString).toLocaleTimeString('ko-KR', {
    timeZone: 'Asia/Seoul',
    hour: 'numeric',
    minute: '2-digit',
    hour12: false,
  });
}

// "한잔 마시기" 버튼에 현재 골라진 음료. 이 값이 바뀔 때마다 loadCutoffTime()을
// 다시 불러 그 음료 기준으로 마감시간을 재계산한다(selectDrink 참고).
// loadCutoffTime이 페이지 로드 시 제일 먼저 호출되므로, TDZ 에러를 피하려면
// 이 선언이 그보다 위에 있어야 한다.
let selectedDrink = null;

// /feed-status/의 warnings(CUTOFF_EXCEEDED, DAILY_LIMIT_EXCEEDED, MARGINAL_EFFECT —
// 뒤의 둘은 CALC-006 한계효용 판정)를 마감시간 문구 위에 빨간 글씨로 띄운다.
function renderFeedWarnings(warnings) {
  const el = document.getElementById('cd-feed-warning');
  if (!el) return;

  if (!Array.isArray(warnings) || !warnings.length) {
    el.hidden = true;
    el.textContent = '';
    return;
  }
  el.textContent = warnings.map((w) => w.message).join(' · ');
  el.hidden = false;
}

// 선택된 음료(selectedDrink)가 있으면 그 음료의 caffeine_mg 기준으로 CALC-002/003/006을
// 다시 계산해달라고 서버에 drink_id를 실어 보낸다(diary.views.FeedStatusView._resolve_ref_dose).
// 선택된 음료가 없으면(페이지 첫 로드) 기존처럼 서버 기본값(가장 최근 즐겨찾기)을 쓴다.
async function loadCutoffTime() {
  const el = document.getElementById('cd-feed-cutoff-time');
  if (!el) return;

  const query = selectedDrink
    ? `?compact=true&drink_id=${selectedDrink.id}`
    : '?compact=true';
  const res = await apiFetch(`/feed-status/${query}`);
  if (res.status === 404) {
    // 백엔드가 내려주는 next("/signup/profile")는 실제로 등록된 페이지 경로가
    // 아니라(spec용 placeholder) 실제 설문 화면인 /initial_survey/로 보낸다.
    window.location.href = '/initial_survey/';
    return;
  }
  if (!res.ok) return;

  const data = await res.json();

  // SLEEP-001: 오늘 아직 안 낸 수면설문이 있으면(diary.views.FeedStatusView.
  // _sleep_survey_required) 마감시간을 보여주는 대신 설문부터 받는다.
  if (data.sleep_survey_required) {
    window.location.href = '/sleep-logs/time';
    return;
  }

  el.textContent = data.cutoff_at ? formatCutoffTime(data.cutoff_at) : '-';
  renderFeedWarnings(data.warnings);
}

loadCutoffTime();

// 즐겨찾는 음료(최대 3개)를 작은 컵 버튼 3개에 매핑한다. 슬롯보다 즐겨찾기가
// 적으면 남는 슬롯은 숨긴다.
let favoriteDrinks = [];

async function loadFavoriteCups() {
  const slots = document.querySelectorAll('#cd-feed-fav-row .cd-feed-fav-slot');
  if (!slots.length) return;

  const res = await apiFetch('/users/me/drinks/');
  const list = res.ok ? await res.json() : [];
  favoriteDrinks = list.filter((d) => d.is_favorite).slice(0, slots.length);

  slots.forEach((slot, i) => {
    const drink = favoriteDrinks[i];
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

// 한잔 마시기 버튼 — 즐겨찾는 음료를 고르면 여기에 아이콘/이름이 반영되고,
// 버튼을 누르면 그 음료로 카페인 로그를 남긴다(마감시간 등은 서버의 calcs 엔진이 재계산).
const bigDrinkBtn = document.getElementById('cd-feed-drink-btn');
const defaultCupIcon = document.getElementById('cd-feed-drink-default-icon');
const selectedCupIcon = document.getElementById('cd-feed-drink-selected-icon');
const selectedDrinkName = document.getElementById('cd-feed-drink-selected-name');

// coffee_icon4~6은 기본 컵과 같은 손잡이 달린 비대칭 그림(색만 다름)이라,
// "한잔 마시기" 글자도 기본 컵과 같은 위치(왼쪽 40%)를 그대로 써야 한다.
const CUP_SHAPED_ICON_KEYS = ['coffee_icon4', 'coffee_icon5', 'coffee_icon6'];

function selectDrink(drink) {
  selectedDrink = drink;
  bigDrinkBtn?.classList.toggle(
    'cd-feed-cup--has-selection',
    !CUP_SHAPED_ICON_KEYS.includes(drink.icon_key)
  );
  if (defaultCupIcon) defaultCupIcon.style.display = 'none';
  if (selectedCupIcon) {
    // base.css의 "img, svg { display: block; }" 규칙이 [hidden]보다 우선 적용돼
    // hidden 속성만으로는 안 감춰진다 — 인라인 style로 직접 제어한다.
    selectedCupIcon.src = cdIconForDrink(drink);
    selectedCupIcon.alt = drink.name;
    selectedCupIcon.style.display = 'block';
  }
  if (selectedDrinkName) {
    selectedDrinkName.textContent = drink.name;
    selectedDrinkName.hidden = false;
  }
  bigDrinkBtn?.setAttribute('aria-label', `한잔 마시기 — ${drink.name} 기록`);

  loadCutoffTime();
}

// 즐겨찾는 음료 클릭 → 한잔 마시기 버튼에 그 음료를 선택 상태로 반영
document.getElementById('cd-feed-fav-row')?.addEventListener('click', (e) => {
  const btn = e.target.closest('.cd-feed-cup');
  if (!btn || !btn.dataset.drinkId) return;
  const drink = favoriteDrinks.find((d) => String(d.id) === btn.dataset.drinkId);
  if (drink) selectDrink(drink);
});

// 한잔 마시기 — 선택된 음료로 POST /caffeine-logs/를 호출해 기록을 남기고,
// 서버 calcs 엔진이 반영한 새 마감시간을 다시 불러온다.
bigDrinkBtn?.addEventListener('click', async () => {
  if (!selectedDrink) {
    alert('즐겨찾는 음료를 먼저 선택해주세요.');
    return;
  }

  const res = await apiFetch('/caffeine-logs/', {
    method: 'POST',
    body: JSON.stringify({ drink_id: selectedDrink.id }),
  });

  if (!res.ok) {
    alert('기록에 실패했어요. 다시 시도해주세요.');
    return;
  }

  await loadCutoffTime();
});

// 커스텀 마시기 — 즐겨찾기에 없는 음료를 이름+카페인량 직접 입력으로 기록한다.
const customOverlay = document.getElementById('cd-custom-overlay');
const customNameInput = document.getElementById('cd-custom-name');
const customMgInput = document.getElementById('cd-custom-mg');

function openCustomModal() {
  if (!customOverlay) return;
  customNameInput.value = '';
  customMgInput.value = '';
  customOverlay.hidden = false;
  customNameInput.focus();
}

function closeCustomModal() {
  if (customOverlay) customOverlay.hidden = true;
}

document.getElementById('cd-feed-custom-drink-btn')?.addEventListener('click', openCustomModal);
document.getElementById('cd-custom-close')?.addEventListener('click', closeCustomModal);
// 카드 바깥(반투명 배경)을 클릭하면 닫는다.
customOverlay?.addEventListener('click', (e) => {
  if (e.target === customOverlay) closeCustomModal();
});

document.getElementById('cd-custom-submit')?.addEventListener('click', async () => {
  const name = customNameInput.value.trim();
  const caffeineMg = Number(customMgInput.value);

  if (!name) {
    alert('음료 이름을 입력해주세요.');
    return;
  }
  // 서버(diary.serializers.CaffeineLogSerializer)도 0 < mg <= 1000으로 검증한다.
  if (!customMgInput.value || !(caffeineMg > 0 && caffeineMg <= 1000)) {
    alert('카페인량은 1~1000mg 사이로 입력해주세요.');
    return;
  }

  const res = await apiFetch('/caffeine-logs/', {
    method: 'POST',
    body: JSON.stringify({ name, caffeine_mg: caffeineMg }),
  });

  if (!res.ok) {
    const data = await res.json().catch(() => ({}));
    const firstError = Object.values(data.errors || {})[0];
    alert(firstError || data.message || '기록에 실패했어요. 다시 시도해주세요.');
    return;
  }

  closeCustomModal();
  await loadCutoffTime();
});