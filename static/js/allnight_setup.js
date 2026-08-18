/* allnight_setup.js — 밤샘모드 시작 전, 목표 시각을 물어보는 채팅형 화면.
 * POST /night-sessions/로 시작하고, 성공하면 계산된 스케줄을 바로 조회해
 * 추천 메시지를 보여준 뒤 진행 화면(chatFrame의 data-redirect-url)으로 이동한다.
 */

const chatFrame = document.getElementById('chatFrame');
const chatContainer = document.getElementById('chatContainer');
const chatInput = document.getElementById('chatInput');
const chatSendBtn = document.getElementById('sendBtn');
const caffeineIconSrc = window.CAFFEINE_ICON_URL || '';
const modeUrl = chatFrame?.dataset.redirectUrl || '/allnight-mode/';

function scrollToBottom() {
  chatContainer.scrollTop = chatContainer.scrollHeight;
}

function addBotMessage(text, { start = false } = {}) {
  const wrap = document.createElement('div');
  wrap.className = 'chatbot';

  const profile = document.createElement('div');
  profile.className = 'bot_profile';
  const icon = document.createElement('img');
  icon.src = caffeineIconSrc;
  icon.alt = '';
  icon.className = 'bot_icon';
  const name = document.createElement('span');
  name.className = 'bot_name';
  name.textContent = 'caffeine bot';
  profile.append(icon, name);

  const bubble = document.createElement('p');
  bubble.className = start ? 'start_bubble' : 'bot_bubble';
  bubble.textContent = text;

  wrap.append(profile, bubble);
  chatContainer.appendChild(wrap);
  scrollToBottom();
}

function addUserMessage(text) {
  const wrap = document.createElement('div');
  wrap.className = 'chat_user';
  const bubble = document.createElement('p');
  bubble.className = 'user_bubble';
  bubble.textContent = text;
  wrap.appendChild(bubble);
  chatContainer.appendChild(wrap);
  scrollToBottom();
}

// "8:00" / "08:00" / "23:59" 같은 HH:MM만 인식한다. 이미 지난 시각이면 내일로 본다
// (target_sleeptime의 "다음 도래 시각" 규칙과 동일).
function parseTargetTime(input) {
  const match = input.trim().match(/^([01]?\d|2[0-3]):([0-5]\d)$/);
  if (!match) return null;

  const hours = Number(match[1]);
  const minutes = Number(match[2]);
  const now = new Date();
  const target = new Date(now.getFullYear(), now.getMonth(), now.getDate(), hours, minutes, 0, 0);
  if (target <= now) target.setDate(target.getDate() + 1);
  return target;
}

function setInputEnabled(enabled) {
  chatInput.disabled = !enabled;
  chatSendBtn.disabled = !enabled;
}

async function handleSend() {
  const text = chatInput.value.trim();
  if (!text) return;

  addUserMessage(text);
  chatInput.value = '';

  const target = parseTargetTime(text);
  if (!target) {
    addBotMessage('시간 형식을 이해하지 못했어요. "08:00"처럼 입력해주세요.');
    return;
  }

  setInputEnabled(false);

  const res = await apiFetch('/night-sessions/', {
    method: 'POST',
    body: JSON.stringify({ target_awake_until: target.toISOString() }),
  });
  const data = await res.json().catch(() => ({}));

  if (res.status === 404) {
    addBotMessage('프로필이 없어서 시작할 수 없어요. 설문부터 진행할게요.');
    window.location.href = '/initial_survey/';
    return;
  }
  if (res.status === 409) {
    addBotMessage('이미 진행 중인 밤샘모드가 있어요. 그 화면으로 이동할게요.');
    window.location.href = modeUrl;
    return;
  }
  if (!res.ok) {
    const firstError = Object.values(data.errors || {})[0];
    addBotMessage(firstError || data.message || '시작하지 못했어요. 다시 시도해주세요.');
    setInputEnabled(true);
    chatInput.focus();
    return;
  }

  // 시작 성공 — 방금 계산된 스케줄을 바로 조회해 추천 잔 수/용량을 보여준다.
  const currentRes = await apiFetch('/night-sessions/current/');
  if (currentRes.ok) {
    const current = await currentRes.json();
    const doses = current.schedule || [];
    if (doses.length > 0) {
      addBotMessage(
        `${doses[0].dose_mg}mg씩 ${doses.length}번 나눠 마시는 걸 추천해요 (총 ${current.total_mg}mg).`
      );
    }
    if (current.warnings && current.warnings.length) {
      addBotMessage(current.warnings[0].message);
    }
  }

  addBotMessage('밤샘모드를 시작했어요! 진행 화면으로 이동할게요.', { start: true });
  setTimeout(() => {
    window.location.href = modeUrl;
  }, 1500);
}

chatSendBtn?.addEventListener('click', handleSend);
chatInput?.addEventListener('keydown', (e) => {
  if (e.key === 'Enter') {
    e.preventDefault();
    handleSend();
  }
});

// 이미 진행 중인 밤샘모드가 있으면 채팅으로 다시 시작할 필요 없이 바로 넘어간다.
(async () => {
  const res = await apiFetch('/night-sessions/current/');
  if (!res.ok) return;
  const data = await res.json().catch(() => ({}));
  if (data.status === 'active') {
    window.location.href = modeUrl;
  }
})();
