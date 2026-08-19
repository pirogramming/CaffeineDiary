/**
 * tour.js — 회원가입 직후 feed로 넘어올 때 nav바를 하나씩 설명하는 온보딩 투어
 *
 * 실행 조건: URL에 ?first_visit=1 이 있으면 무조건 시작한다("최초 1회만"이
 * 아니라 회원가입 → feed 진입이라는 동작 자체에 붙는 연출). daily_rating.js가
 * 회원가입 직후 설문(sleep-logs/rating) 제출 성공 시 /feed/?first_visit=1
 * 로 보내는 것과 짝을 이룬다.
 *
 * nav바의 각 항목은 base.html에서 data-tour="..." 속성으로 표시해뒀다
 * (href가 바뀌어도 셀렉터가 안 깨지도록 href 대신 이 속성으로 찾는다).
 */

(function () {
  const steps = [
    { selector: '[data-tour="main"]', title: '메인 화면', desc: '마신 카페인 음료를 기록하면서 오늘의 카페인 마감 시간을 확인할 수 있어요.' },
    { selector: '[data-tour="feed"]', title: '나의 다이어리', desc: '마신 카페인의 양, 수면 시간 등 지금까지 기록한 카페인 일지를 한눈에 볼 수 있어요.' },
    { selector: '[data-tour="drinks"]', title: '음료 추가', desc: '즐겨 마시는 카페인 음료를 등록하고 수정할 수 있어요.' },
    { selector: '[data-tour="allnight"]', title: '밤샘 모드', desc: '밤을 새울 계획이라면 여기에서 시간을 설정하고 계획을 추천받아 보세요.' },
    { selector: '[data-tour="mypage"]', title: '마이페이지', desc: '내 수면 시각과 체중을 수정할 수 있어요.' },
  ];

  function shouldRunTour() {
    const params = new URLSearchParams(window.location.search);
    if (params.get('first_visit') === '1') return true;
    // 회원가입 직후 초기 설문(initial_survey/*)은 일일 수면설문(/sleep-logs/rating,
    // daily_rating.js)을 거치지 않고 SurveySleepView가 곧장 /feed/로 보내므로
    // first_visit 파라미터가 붙지 않는다. 그래서 가입 시 auth.js가 심어둔
    // cd_pending_tour 플래그를 여기서 직접 보고, 초기 설문 경로에서도 투어가 뜨게 한다.
    return sessionStorage.getItem('cd_pending_tour') === '1';
  }

  // 쿼리스트링을 지워서, 새로고침했을 때 투어가 다시 시작되지 않게 한다
  // (localStorage로도 막히지만, 주소창이 지저분해 보이는 것도 같이 정리).
  function cleanUrl() {
    const url = new URL(window.location.href);
    url.searchParams.delete('first_visit');
    window.history.replaceState({}, '', url.pathname + url.search);
  }

  let currentIndex = 0;
  let els = {};
  let resizeHandler = null;

  function buildDom() {
    const spotlight = document.createElement('div');
    spotlight.className = 'cd-tour-spotlight';

    const catcher = document.createElement('div');
    catcher.className = 'cd-tour-catcher';

    const card = document.createElement('div');
    card.className = 'cd-tour-card';
    card.innerHTML = `
      <div class="cd-tour-card__body">
        <img src="/static/images/dailysurvey-logo.svg" alt="" class="cd-tour-card__icon">
        <div class="cd-tour-card__bubble">
          <p class="cd-tour-card__title"></p>
          <p class="cd-tour-card__desc"></p>
          <p class="cd-tour-card__progress"></p>
        </div>
      </div>
    `;

    document.body.appendChild(spotlight);
    document.body.appendChild(catcher);
    document.body.appendChild(card);

    els = { spotlight, catcher, card };

    card.addEventListener('click', advance);
    catcher.addEventListener('click', advance);

    // 화면 크기가 바뀌면(반응형 레이아웃으로 nav 위치 자체가 이동하므로)
    // 현재 단계를 다시 그려서 스포트라이트/카드가 새 위치를 따라가게 한다.
    resizeHandler = () => renderStep();
    window.addEventListener('resize', resizeHandler);
  }

  function renderStep() {
    const step = steps[currentIndex];
    const target = document.querySelector(step.selector);

    els.card.querySelector('.cd-tour-card__title').textContent = step.title;
    els.card.querySelector('.cd-tour-card__desc').textContent = step.desc;
    els.card.querySelector('.cd-tour-card__progress').textContent =
      `${currentIndex + 1} / ${steps.length} · 클릭해서 계속`;

    const isMobile = window.matchMedia('(max-width: 480px)').matches;

    // 모바일이거나(햄버거 메뉴 안에 nav가 숨어있어 못 가리킴), 대상 요소를
    // 못 찾은 경우 스포트라이트 없이 카드만 화면 중앙 하단에 띄운다.
    if (!target || isMobile) {
      els.spotlight.style.display = 'none';
      els.card.classList.add('cd-tour-card--centered');
      return;
    }

    els.card.classList.remove('cd-tour-card--centered');
    els.spotlight.style.display = 'block';

    const rect = target.getBoundingClientRect();
    const pad = 8;
    els.spotlight.style.top = `${rect.top - pad}px`;
    els.spotlight.style.left = `${rect.left - pad}px`;
    els.spotlight.style.width = `${rect.width + pad * 2}px`;
    els.spotlight.style.height = `${rect.height + pad * 2}px`;

    // 카드는 강조된 영역 바로 아래에 두되, 화면 아래쪽에 공간이 부족하면 위로
    const cardRect = els.card.getBoundingClientRect();
    const spaceBelow = window.innerHeight - rect.bottom;
    const top = spaceBelow > cardRect.height + 24
      ? rect.bottom + 30
      : rect.top - cardRect.height - 16;

    els.card.style.top = `${Math.max(16, top)}px`;
    els.card.style.left = `${Math.max(16, Math.min(rect.left, window.innerWidth - cardRect.width - 16))}px`;
  }

  function advance() {
    currentIndex += 1;
    if (currentIndex >= steps.length) {
      endTour();
      return;
    }
    renderStep();
  }

  function endTour() {
    if (resizeHandler) {
      window.removeEventListener('resize', resizeHandler);
      resizeHandler = null;
    }
    els.spotlight?.remove();
    els.catcher?.remove();
    els.card?.remove();
  }

  function startTour() {
    if (!shouldRunTour()) return;
    // 어느 경로(파라미터 / 세션 플래그)로 들어왔든 투어는 최초 1회만. 새로고침·
    // 재방문에 다시 뜨지 않도록 두 신호를 모두 소비한다(플래그 제거 + URL 정리).
    sessionStorage.removeItem('cd_pending_tour');
    buildDom();
    renderStep();
    cleanUrl();
  }

  document.addEventListener('DOMContentLoaded', startTour);
})();