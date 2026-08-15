/**
 * daily_rating.js — 수면 평점 (SLEEP-002 / POST /sleep-logs)
 * API가 1~5만 허용하므로, 아무것도 안 고른 상태(0)로는 제출을 막는다.
 * 이전 화면(daily_time.html)에서 datetime-local로 받아 sessionStorage에 저장해둔 값을 그대로 꺼내 쓴다.
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
  const el = document.getElementById('cdDailyRatingError');
  if (!el) return;
  el.textContent = message;
  el.hidden = false;
}

function clearError() {
  const el = document.getElementById('cdDailyRatingError');
  if (!el) return;
  el.hidden = true;
  el.textContent = '';
}

const RATING_STORAGE_KEY = 'cd_daily_sleep_quality';

const beansWrap = document.querySelector('[data-rating-beans]');
const beans = beansWrap ? Array.from(beansWrap.querySelectorAll('.cd-daily-rating__bean')) : [];

function applySelection(selectedIndex) {
  beans.forEach((bean) => {
    const index = Number(bean.dataset.beanIndex);
    bean.classList.toggle('is-selected', index <= selectedIndex);
  });
}

beans.forEach((bean) => {
  const radio = bean.querySelector('.cd-daily-rating__bean-input');
  radio?.addEventListener('change', () => {
    applySelection(Number(bean.dataset.beanIndex));
    sessionStorage.setItem(RATING_STORAGE_KEY, radio.value); // 제출 전이라도 즉시 저장
  });
});

// time 화면으로 back 갔다가 다시 돌아온 경우 — 이전에 고른 원두를 복원한다.
(function restorePreviousRating() {
  const saved = sessionStorage.getItem(RATING_STORAGE_KEY);
  if (!saved) return;

  const radio = document.querySelector(`.cd-daily-rating__bean-input[value="${saved}"]`);
  if (!radio) return;

  radio.checked = true;
  applySelection(Number(radio.closest('.cd-daily-rating__bean').dataset.beanIndex));
})();

document.getElementById('cdDailyRatingForm')?.addEventListener('submit', async (event) => {
  event.preventDefault();
  clearError();

  const checked = document.querySelector('.cd-daily-rating__bean-input:checked');
  const sleepQuality = checked ? Number(checked.value) : 0;

  // API는 1~5만 허용 — 0(미선택)으로는 제출 자체를 막는다.
  if (sleepQuality < 1) {
    showError('원두를 하나 이상 선택해주세요.');
    return;
  }

  const actualBedtime = sessionStorage.getItem('cd_daily_actual_bedtime');
  if (!actualBedtime) {
    // daily_time.html을 안 거치고 이 화면으로 바로 들어온 경우
    showError('취침 시각 정보가 없어요. 이전 화면부터 다시 진행해주세요.');
    return;
  }

  const res = await apiFetch('/sleep-logs', {
    method: 'POST',
    body: JSON.stringify({
      sleep_quality: sleepQuality,
      actual_bedtime: actualBedtime,
    }),
  });

  const data = await res.json().catch(() => ({}));

  if (res.status === 201) {
    // TODO: data.threshold_mg / personalization_weight 등을 화면에 반영하고 싶으면 여기서 사용
    sessionStorage.removeItem('cd_daily_actual_bedtime');
    sessionStorage.removeItem(RATING_STORAGE_KEY);
    window.location.href = '/feed/';
    return;
  }

  if (res.status === 401) {
    window.location.href = '/auth/login';
    return;
  }

  if (res.status === 409) {
    // 이미 오늘자 기록이 있는 경우 — 에러로 막기보다 그냥 다음 화면으로 넘긴다
    sessionStorage.removeItem('cd_daily_actual_bedtime');
    sessionStorage.removeItem(RATING_STORAGE_KEY);
    window.location.href = '/feed/';
    return;
  }

  if (res.status === 400) {
    const fieldErrors = data.errors || {};
    const message = fieldErrors.sleep_quality || fieldErrors.actual_bedtime || data.message
      || '입력값을 확인해주세요.';
    showError(message);
    return;
  }

  // 500 등 그 외
  showError(data.message || '요청을 처리하지 못했어요. 다시 시도해주세요.');
});

document.getElementById('cdDailyRatingBack')?.addEventListener('click', () => {
  window.location.href = '/sleep-logs/time';
});