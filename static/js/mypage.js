/**
 * mypage.js — 마이페이지(닉네임/체중/목표 취침시각)를 GET /users/me/profile/로 채우고,
 * "수정" 버튼으로 닉네임/체중/취침시각을 PATCH 저장한다.
 */
(function () {
  const nicknameEl = document.getElementById('mypage-nickname');
  const nicknameEdit = document.getElementById('mypage-nickname-edit');
  const nicknameInput = document.getElementById('mypage-nickname-input');
  const weightDisplay = document.getElementById('mypage-weight');
  const weightInput = document.getElementById('mypage-weight-input');
  const sleepDisplay = document.getElementById('mypage-sleep');
  const sleepInput = document.getElementById('mypage-sleep-input');
  const editBtn = document.getElementById('mypage-edit-btn');
  const editLabel = document.getElementById('mypage-edit-label');

  let editing = false;

  async function loadProfile() {
    const res = await apiFetch('/users/me/profile/');
    if (!res.ok) return;
    const data = await res.json();

    nicknameEl.textContent = data.nickname || data.username;
    nicknameInput.value = data.nickname || data.username;
    weightDisplay.textContent = data.body_weight_kg;
    sleepDisplay.textContent = data.target_bedtime;
    weightInput.value = data.body_weight_kg;
    sleepInput.value = data.target_bedtime;
  }

  function enterEditMode() {
    editing = true;
    nicknameEl.hidden = true;
    nicknameEdit.hidden = false;
    weightDisplay.hidden = true;
    weightInput.hidden = false;
    sleepDisplay.hidden = true;
    sleepInput.hidden = false;
    editLabel.textContent = '저장';
  }

  function exitEditMode() {
    editing = false;
    nicknameEl.hidden = false;
    nicknameEdit.hidden = true;
    weightDisplay.hidden = false;
    weightInput.hidden = true;
    sleepDisplay.hidden = false;
    sleepInput.hidden = true;
    editLabel.textContent = '수정';
  }

  async function saveProfile() {
    const res = await apiFetch('/users/me/profile/', {
      method: 'PATCH',
      body: JSON.stringify({
        nickname: nicknameInput.value.trim(),
        body_weight_kg: Number(weightInput.value),
        target_bedtime: sleepInput.value,
      }),
    });
    if (!res.ok) {
      alert('저장에 실패했어요. 입력값을 확인해주세요.');
      return;
    }
    const data = await res.json();
    nicknameEl.textContent = data.nickname;
    nicknameInput.value = data.nickname;
    weightDisplay.textContent = data.body_weight_kg;
    sleepDisplay.textContent = data.target_bedtime;
    exitEditMode();
  }

  editBtn?.addEventListener('click', () => {
    if (editing) {
      saveProfile();
    } else {
      enterEditMode();
    }
  });

  loadProfile();
})();
