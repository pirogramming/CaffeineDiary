/* allnight_mode.js — 밤샘모드 진행 화면.
 * GET /night-sessions/current/로 상태를 받아 카운트다운/스케줄을 그리고,
 * 종료 버튼은 PATCH로 수동 종료한다. 목표시각 도달 시 서버가 자동 종료하므로
 * 주기적으로 다시 조회해 그 상태 변화를 반영한다.
 */

const timerEl = document.getElementById('allnightTimer');
const warningEl = document.getElementById('allnightWarning');
const finishBtn = document.getElementById('allnightFinishBtn');
const scheduleListEl = document.getElementById('allnightScheduleList');
const scheduleToggle = document.getElementById('allnightScheduleToggle');

let targetTime = null; // Date — target_awake_until
let tickTimer = null;
let pollTimer = null;

function formatRemaining(ms) {
    const totalSec = Math.max(0, Math.round(ms / 1000));
    const h = Math.floor(totalSec / 3600);
    const m = Math.floor((totalSec % 3600) / 60);
    const s = totalSec % 60;
    return `${h}:${String(m).padStart(2, '0')}:${String(s).padStart(2, '0')}`;
}

// favoriteDrinks의 각 음료(최대 3개)를 "이름-N잔" 줄로 만든다. dose_mg가 모든
// 회차에서 동일하므로(calc_night_schedule) 한 번만 계산해 모든 스케줄 항목에
// 그대로 재사용한다.
function cupLinesByDrink(favoriteDrinks) {
    return favoriteDrinks
        .filter((d) => d.dose_cups != null)
        .map((d) => `${d.name} : ${d.dose_cups}잔`);
}

function renderSchedule(schedule, favoriteDrinks) {
    scheduleListEl.innerHTML = '';
    const cupLines = cupLinesByDrink(favoriteDrinks || []);

    // schedule은 서버(calc_night_schedule)가 회차 순서 그대로 내려주므로,
    // 배열 위치(i+1)가 곧 회차 번호(N번째 섭취)다.
    schedule.forEach((dose, i) => {
        const li = document.createElement('li');
        if (dose.done) li.classList.add('is-done');

        const timeSpan = document.createElement('span');
        timeSpan.className = 'time';
        timeSpan.textContent = new Date(dose.at).toLocaleTimeString('ko-KR', {
            hour: 'numeric',
            minute: '2-digit',
            hour12: false,
        });

        const workSpan = document.createElement('span');
        workSpan.className = 'work';

        const titleLine = document.createElement('span');
        titleLine.className = 'work_title';
        titleLine.textContent = `${i + 1}번째 섭취 (${dose.dose_mg}mg)`;
        workSpan.appendChild(titleLine);

        // 즐겨찾는 음료 3종을 한 줄로 잇지 않고 각각 세로로 한 줄씩 나열한다.
        cupLines.forEach((line) => {
            const cupLine = document.createElement('span');
            cupLine.className = 'work_cup';
            cupLine.textContent = line;
            workSpan.appendChild(cupLine);
        });

        li.append(timeSpan, workSpan);
        scheduleListEl.appendChild(li);
    });
}

function stopTimers() {
    if (tickTimer) clearInterval(tickTimer);
    if (pollTimer) clearInterval(pollTimer);
}

function tick() {
    if (!targetTime) return;
    const remaining = targetTime - Date.now();
    timerEl.textContent = formatRemaining(remaining);
    if (remaining <= 0) refresh(); // 목표시각 도달 -> 서버 상태 재확인(자동종료 반영)
}

async function refresh() {
    const res = await apiFetch('/night-sessions/current/');

    if (res.status === 404) {
        const data = await res.json().catch(() => ({}));
        stopTimers();
        window.location.href = data.next || '/';
        return;
    }
    if (!res.ok) return; // 일시적 오류 — 다음 폴링에서 재시도

    const data = await res.json();

    if (data.status === 'ended') {
        stopTimers();
        alert(
            `밤샘모드가 종료됐어요.\n` +
            `${data.reached_target ? '목표 시각까지 완주했어요!' : '중간에 종료했어요.'}\n` +
            `총 섭취량: ${data.total_intake_mg}mg`
        );
        // 서버가 내려주는 next("/")는 API 명세용 값 — 화면 이동은 메인피드로 보낸다.
        window.location.href = '/feed/';
        return;
    }

    targetTime = new Date(data.target_awake_until);
    timerEl.textContent = formatRemaining(targetTime - Date.now());
    renderSchedule(data.schedule || [], data.favorite_drinks || []);

    if (data.warnings && data.warnings.length) {
        warningEl.textContent = data.warnings[0].message;
        warningEl.hidden = false;
    } else {
        warningEl.hidden = true;
    }
}

finishBtn?.addEventListener('click', async () => {
    if (!confirm('밤샘모드를 종료할까요?')) return;
    finishBtn.disabled = true;

    const res = await apiFetch('/night-sessions/current/', {
        method: 'PATCH',
        body: JSON.stringify({ status: 'ended' }),
    });

    if (!res.ok) {
        alert('종료하지 못했어요. 다시 시도해주세요.');
        finishBtn.disabled = false;
        return;
    }

    const data = await res.json();
    stopTimers();
    alert(`밤샘모드를 종료했어요.\n총 섭취량: ${data.total_intake_mg}mg`);
    window.location.href = '/feed/';
});

// 오늘의 스케줄 토글 — collapsed 클래스를 켜고 끄면 allnight_mode.css의
// max-height 트랜지션으로 접히고 펼쳐진다.
scheduleToggle?.addEventListener('click', () => {
    scheduleToggle.classList.toggle('collapsed');
    scheduleListEl.classList.toggle('collapsed');
});

refresh().then(() => {
    tickTimer = setInterval(tick, 1000);
    pollTimer = setInterval(refresh, 60000);
});

// 모바일 햄버거 메뉴 — base.js와 동일한 로직.
// 이 페이지는 base.html을 상속하지 않고 헤더를 직접 그려서 id가 달라(navToggle 등),
// base.js의 cd-nav-toggle 기반 로직이 안 먹는다 — 여기서 따로 연결한다.
document.addEventListener('DOMContentLoaded', function () {
    const navToggle = document.getElementById('navToggle');
    const navMenu = document.getElementById('navMenu');
    const navBackdrop = document.getElementById('navBackdrop');

    if (navToggle && navMenu && navBackdrop) {
        function openNav() {
            navMenu.classList.add('is-open');
            navBackdrop.hidden = false;
            requestAnimationFrame(function () {
                navBackdrop.classList.add('is-open');
            });
            navToggle.setAttribute('aria-expanded', 'true');
        }

        function closeNav() {
            navMenu.classList.remove('is-open');
            navBackdrop.classList.remove('is-open');
            navToggle.setAttribute('aria-expanded', 'false');
            setTimeout(function () {
                navBackdrop.hidden = true;
            }, 250);
        }

        navToggle.addEventListener('click', function () {
            const isOpen = navToggle.getAttribute('aria-expanded') === 'true';
            isOpen ? closeNav() : openNav();
        });

        navBackdrop.addEventListener('click', closeNav);

        navMenu.querySelectorAll('a, button').forEach(function (el) {
            el.addEventListener('click', closeNav);
        });
    }
});
