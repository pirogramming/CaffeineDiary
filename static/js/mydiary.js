/**
 * mydiary.js — "나의 다이어리" 화면(/mydiary/) 전용 스크립트.
 *
 * 카드 3개를 기존 API로 채운다(신규 백엔드 엔드포인트 없이 연결):
 *   - 오늘의 카페인 : GET /feed-status/            (CALC-001 잔류량 그래프)
 *   - 어제의 수면   : GET /sleep-logs/?page_size=1 (가장 최근 기록 = 전날 밤)
 *   - 일주일 그래프 : GET /caffeine-logs/, /sleep-logs/ (최근 7일, 일별 집계는 프론트에서 계산)
 *
 * apiFetch/getCookie는 base.js(이 스크립트보다 먼저 로드됨)가 전역으로 제공한다.
 */

const CD_KST_TZ = 'Asia/Seoul';
const CD_COLOR_LINE = '#543131';       // --cd-brown-deep
const CD_COLOR_LINE_SOFT = 'rgba(84, 49, 49, 0.15)';
const CD_COLOR_MUTED = '#CABDB8';      // --cd-brown-light

function cdFormatKstTime(date) {
  return date.toLocaleTimeString('ko-KR', {
    timeZone: CD_KST_TZ,
    hour: '2-digit',
    minute: '2-digit',
    hour12: false,
  });
}

// "YYYY-MM-DD" (Asia/Seoul 기준). caffeine-logs의 start_date/end_date 파라미터와
// 같은 형식이라 그대로 쿼리스트링에 쓸 수 있다.
function cdKstDateKey(date) {
  return date.toLocaleDateString('en-CA', { timeZone: CD_KST_TZ });
}

function cdKstWeekdayLabel(date) {
  return date.toLocaleDateString('ko-KR', { timeZone: CD_KST_TZ, weekday: 'short' });
}

/**
 * 오늘의 카페인 — FeedStatusView가 CALC-001로 계산해 내려주는 하루치 잔류량
 * 배열(graph.mg)을 선그래프로 그린다. 화면 로직은 feed.js의 loadCutoffTime과
 * 동일하게, 프로필이 없으면(404) 설문으로 보낸다.
 */
async function loadTodayCaffeineChart() {
  const canvas = document.getElementById('todayCaffeineGraph');
  if (!canvas) return;

  const res = await apiFetch('/feed-status/');
  if (res.status === 404) {
    window.location.href = '/initial_survey/';
    return;
  }
  if (!res.ok) return;

  const data = await res.json();
  const graph = data.graph;
  if (!graph || !graph.mg?.length) return;

  const start = new Date(graph.start);
  const labels = graph.mg.map((_, i) =>
    cdFormatKstTime(new Date(start.getTime() + i * graph.interval_min * 60000))
  );

  const datasets = [
    {
      label: '체내 카페인(mg)',
      data: graph.mg,
      borderColor: CD_COLOR_LINE,
      backgroundColor: CD_COLOR_LINE_SOFT,
      borderWidth: 2,
      pointRadius: 0,
      tension: 0.3,
      fill: true,
    },
  ];
  if (graph.threshold_mg != null) {
    datasets.push({
      label: '임계치',
      data: graph.mg.map(() => graph.threshold_mg),
      borderColor: CD_COLOR_MUTED,
      borderWidth: 1,
      borderDash: [4, 4],
      pointRadius: 0,
      fill: false,
    });
  }

  new Chart(canvas, {
    type: 'line',
    data: { labels, datasets },
    options: {
      responsive: true,
      maintainAspectRatio: false,
      interaction: { intersect: false, mode: 'index' },
      plugins: {
        legend: { display: false },
        title: {
          display: true,
          text: `오늘 총 ${Math.round(data.today_total_mg ?? 0)}mg`,
          color: CD_COLOR_LINE,
          font: { size: 11 },
          padding: { bottom: 4 },
        },
      },
      scales: {
        x: { ticks: { maxTicksLimit: 5, font: { size: 9 } }, grid: { display: false } },
        y: { beginAtZero: true, ticks: { font: { size: 9 } } },
      },
    },
  });
}

/**
 * 어제의 수면 — 가장 최근 SleepLog 1건(전날 밤 기록한 값)을 수면질(1~5) 막대로
 * 보여준다. 취침시각 잔류 카페인량이 함께 있으면 부제로 덧붙인다.
 */
async function loadYesterdaySleepChart() {
  const canvas = document.getElementById('yesterdaySleepGraph');
  if (!canvas) return;

  const res = await apiFetch('/sleep-logs/?page_size=1');
  if (!res.ok) return;

  const data = await res.json();
  const log = (data.results || [])[0];
  const hasQuality = log?.sleep_quality != null;
  const quality = hasQuality ? log.sleep_quality : 0;

  const subtitle = !hasQuality
    ? '아직 기록된 수면 정보가 없어요'
    : log.residual_mg_at_sleep != null
      ? `수면질 ${quality}/5 · 취침 시 잔류 ${Math.round(log.residual_mg_at_sleep)}mg`
      : `수면질 ${quality}/5`;

  new Chart(canvas, {
    type: 'bar',
    data: {
      labels: ['수면질'],
      datasets: [
        {
          data: [quality],
          backgroundColor: hasQuality ? CD_COLOR_LINE : CD_COLOR_MUTED,
          borderRadius: 6,
          barThickness: 24,
        },
      ],
    },
    options: {
      indexAxis: 'y',
      responsive: true,
      maintainAspectRatio: false,
      plugins: {
        legend: { display: false },
        title: { display: true, text: subtitle, color: CD_COLOR_LINE, font: { size: 11 } },
      },
      scales: {
        x: { min: 0, max: 5, ticks: { stepSize: 1, font: { size: 9 } } },
        y: { display: false },
      },
    },
  });
}

/**
 * 일주일 그래프 — 오늘을 포함한 최근 7일간의 하루 총 섭취량(mg)과 수면질(1~5)을
 * 이중축 꺾은선그래프로 겹쳐 보여준다. 둘 다 일별 합산 API가 없어 목록을 받아
 * 프론트에서 날짜(Asia/Seoul)별로 집계한다(개인 다이어리 기록량 규모라
 * page_size=100이면 충분하다). 수면 기록이 없는 날은 null로 둬 선을 끊는다
 * (0점으로 그리면 "최저 수면질"과 구분이 안 된다).
 */
async function loadWeeklyChart() {
  const canvas = document.getElementById('weeklyGraph');
  if (!canvas) return;

  const days = Array.from({ length: 7 }, (_, i) => new Date(Date.now() - (6 - i) * 86400000));
  const startDate = cdKstDateKey(days[0]);
  const endDate = cdKstDateKey(days[6]);

  const [caffeineRes, sleepRes] = await Promise.all([
    apiFetch(`/caffeine-logs/?start_date=${startDate}&end_date=${endDate}&page_size=100`),
    apiFetch(`/sleep-logs/?start_date=${startDate}&end_date=${endDate}&page_size=100`),
  ]);
  if (!caffeineRes.ok) return;

  const caffeineLogs = (await caffeineRes.json()).results || [];
  const mgByDate = Object.fromEntries(days.map((d) => [cdKstDateKey(d), 0]));
  caffeineLogs.forEach((log) => {
    const key = cdKstDateKey(new Date(log.created_at));
    if (key in mgByDate) mgByDate[key] += log.caffeine_mg;
  });

  const qualityByDate = {};
  if (sleepRes.ok) {
    const sleepLogs = (await sleepRes.json()).results || [];
    sleepLogs.forEach((log) => {
      if (log.sleep_quality == null) return;
      // 하루 1건 제한(SLEEP-002)이라 겹쳐 써도 안전하다.
      qualityByDate[cdKstDateKey(new Date(log.created_at))] = log.sleep_quality;
    });
  }

  new Chart(canvas, {
    type: 'line',
    data: {
      labels: days.map((d) => cdKstWeekdayLabel(d)),
      datasets: [
        {
          label: '카페인(mg)',
          data: days.map((d) => Math.round(mgByDate[cdKstDateKey(d)])),
          borderColor: CD_COLOR_LINE,
          backgroundColor: CD_COLOR_LINE_SOFT,
          borderWidth: 2,
          pointRadius: 2,
          tension: 0.3,
          fill: true,
          yAxisID: 'y',
        },
        {
          label: '수면질(/5)',
          data: days.map((d) => qualityByDate[cdKstDateKey(d)] ?? null),
          borderColor: CD_COLOR_MUTED,
          borderWidth: 2,
          borderDash: [4, 4],
          pointRadius: 2,
          spanGaps: false,
          tension: 0.3,
          fill: false,
          yAxisID: 'y1',
        },
      ],
    },
    options: {
      responsive: true,
      maintainAspectRatio: false,
      interaction: { intersect: false, mode: 'index' },
      plugins: {
        legend: { display: true, labels: { boxWidth: 10, font: { size: 9 } } },
      },
      scales: {
        x: { grid: { display: false }, ticks: { font: { size: 10 } } },
        y: {
          position: 'left',
          beginAtZero: true,
          ticks: { font: { size: 9 } },
        },
        y1: {
          position: 'right',
          min: 0,
          max: 5,
          ticks: { stepSize: 1, font: { size: 9 } },
          grid: { drawOnChartArea: false },
        },
      },
    },
  });
}

loadTodayCaffeineChart();
loadYesterdaySleepChart();
loadWeeklyChart();
