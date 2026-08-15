/**
 * daily_time.js — 어제 취침 시각 입력
 * 프론트에서 어제 날짜 + 입력한 시:분을 조합해 ISO 8601(타임존 오프셋 포함)로 만들어 sessionStorage에 저장
 * 다음 화면(daily_rating.html)이 POST /sleep-logs 호출 시 이 값을 그대로 꺼내 쓴다.
 */

function showTimeError(message) {
  const el = document.getElementById('cdDailyTimeError');
  if (!el) return;
  el.textContent = message;
  el.hidden = false;
}

function clearTimeError() {
  const el = document.getElementById('cdDailyTimeError');
  if (!el) return;
  el.hidden = true;
  el.textContent = '';
}

/**
 * "8:00" / "08:00" / "23:45" 같은 HH:MM 문자열을 시/분으로 파싱한다.
 * @returns {{hour:number, minute:number}|null} 형식이 안 맞으면 null
 */
function parseTimeInput(value) {
  const match = value.trim().match(/^([0-1]?\d|2[0-3]):([0-5]\d)$/);
  if (!match) return null;
  return { hour: Number(match[1]), minute: Number(match[2]) };
}

/**
 * 어제 날짜 + {hour, minute}을 조합해 타임존 오프셋 포함 ISO 8601 문자열로 만든다.
 */
function toYesterdayISO({ hour, minute }) {
  const date = new Date();
  date.setDate(date.getDate() - 1);
  date.setHours(hour, minute, 0, 0);

  const pad = (n) => String(n).padStart(2, '0');
  const offsetMin = -date.getTimezoneOffset();
  const sign = offsetMin >= 0 ? '+' : '-';
  const offsetH = pad(Math.floor(Math.abs(offsetMin) / 60));
  const offsetM = pad(Math.abs(offsetMin) % 60);

  const local =
    `${date.getFullYear()}-${pad(date.getMonth() + 1)}-${pad(date.getDate())}` +
    `T${pad(date.getHours())}:${pad(date.getMinutes())}:00`;

  return `${local}${sign}${offsetH}:${offsetM}`;
}

const input = document.getElementById('cdDailyTimeInput');
const sendBtn = document.getElementById('cdDailyTimeSend');
const inputRow = document.getElementById('cdDailyTimeInputRow');
const answerWrap = document.getElementById('cdDailyTimeAnswerWrap');
const answerText = document.getElementById('cdDailyTimeAnswer');
const nextBtn = document.getElementById('cdDailyTimeNext');

// rating 화면에서 back으로 돌아온 경우 — sessionStorage에 이미 값이 있으면
// "처음 상태"가 아니라 이전에 입력했던 답변을 그대로 복원해서 보여준다.
(function restorePreviousAnswer() {
  const existing = sessionStorage.getItem('cd_daily_actual_bedtime');
  if (!existing) return;

  const match = existing.match(/T(\d{2}):(\d{2})/);
  if (!match) return;

  answerText.textContent = `${Number(match[1])}:${match[2]}`;
  answerWrap.hidden = false;
  inputRow.hidden = true;
  nextBtn.disabled = false;
})();

function handleSend() {
  clearTimeError();

  const raw = input.value;
  const parsed = parseTimeInput(raw);
  if (!parsed) {
    showTimeError('시간을 "8:00"처럼 시:분 형식으로 입력해주세요.');
    return;
  }

  const iso = toYesterdayISO(parsed);
  sessionStorage.setItem('cd_daily_actual_bedtime', iso);

  // 입력한 내용을 말풍선으로 보여준다
  answerText.textContent = raw.trim();
  answerWrap.hidden = false;
  answerWrap.classList.add('is-visible');

  inputRow.hidden = true;
  nextBtn.disabled = false;
}

sendBtn?.addEventListener('click', handleSend);
input?.addEventListener('keydown', (e) => {
  if (e.key === 'Enter') handleSend();
});

// next → 레이팅 화면으로 이동
nextBtn?.addEventListener('click', () => {
  if (nextBtn.disabled) return;
  window.location.href = '/sleep-logs/rating';
});