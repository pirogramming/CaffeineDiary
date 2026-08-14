// 모든 테스트 페이지 공용 스크립트. 디자인 없음, fetch 결과를 그대로 화면에 출력하는 용도.

function getCookie(name) {
  const m = document.cookie.match(new RegExp("(?:^|; )" + name + "=([^;]*)"));
  return m ? decodeURIComponent(m[1]) : null;
}

async function apiFetch(path, method = "GET", body = null) {
  const headers = { "Content-Type": "application/json" };
  if (method !== "GET") {
    const csrftoken = getCookie("csrftoken");
    if (csrftoken) headers["X-CSRFToken"] = csrftoken;
  }
  const res = await fetch(path, {
    method,
    headers,
    credentials: "include",
    body: body !== null ? JSON.stringify(body) : undefined,
  });
  let data = null;
  try {
    data = await res.json();
  } catch (e) {
    // 204 No Content 등 본문이 없는 응답
  }
  return { status: res.status, ok: res.ok, data };
}

function renderResult(elId, result) {
  document.getElementById(elId).textContent =
    "HTTP " + result.status + "\n\n" + JSON.stringify(result.data, null, 2);
}

// 상단 nav의 로그인 상태 표시 + 모든 페이지 최초 진입 시 CSRF 쿠키 확보(session은 ensure_csrf_cookie)
async function initNav() {
  const result = await apiFetch("/auth/session/");
  const el = document.getElementById("auth-status");
  if (!el) return;
  if (result.data && result.data.is_authenticated) {
    el.textContent = "로그인됨 (user_id=" + result.data.user_id + ")";
  } else {
    el.textContent = "로그인 안 됨";
  }
}

async function doLogout() {
  const result = await apiFetch("/auth/logout/", "POST");
  alert("POST /auth/logout/\nHTTP " + result.status + "\n" + JSON.stringify(result.data));
  initNav();
}
