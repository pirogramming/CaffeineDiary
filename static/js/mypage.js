/**
 * mypage.js — 마이페이지(닉네임/체중/목표 취침시각)를 GET /users/me/profile/로 채운다.
 */
(async function loadMypageProfile() {
  const res = await apiFetch('/users/me/profile/');
  if (!res.ok) return;
  const data = await res.json();

  document.getElementById('mypage-nickname').textContent = data.username;
  document.getElementById('mypage-weight').textContent = data.body_weight_kg;
  document.getElementById('mypage-sleep').textContent = data.target_bedtime;
})();
