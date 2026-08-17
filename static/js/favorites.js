/**
 * favorites.js — 즐겨찾는 음료(최대 3개) 목록을 GET /users/me/drinks/로 채우고,
 * "추가"/"수정" 오버레이(종류→브랜드→메뉴→사이즈)로 선택한 프리셋을
 * POST .../from-preset/(추가) 또는 PATCH .../<id>/(교체)로 저장한다.
 */
(function () {
  const listEl = document.getElementById('favorite-drinks-list');
  const overlay = document.getElementById('editOverlay');
  const closeBtn = document.getElementById('overlay-close-btn');
  const saveBtn = document.getElementById('wizard-save-btn');

  const steps = {
    type: overlay.querySelector('[data-step="1"]'),
    brand: overlay.querySelector('[data-step="2"]'),
    menu: overlay.querySelector('[data-step="3"]'),
    size: overlay.querySelector('[data-step="4"]'),
  };

  let wizard = { mode: 'add', editingId: null, type: null, brand: null, name: null, size: null, presetsForType: [] };

  function iconForType(type) {
    return window.CD_DRINK_ICONS[type] || window.CD_DRINK_ICONS.other;
  }

  // ── 즐겨찾기 목록 ──────────────────────────────────────────────

  async function loadFavorites() {
    const res = await apiFetch('/users/me/drinks/');
    const list = res.ok ? await res.json() : [];
    const favorites = list.filter((d) => d.is_favorite).slice(0, 3);

    listEl.innerHTML = '';
    for (let i = 0; i < 3; i++) {
      listEl.appendChild(favorites[i] ? renderFilledCard(favorites[i]) : renderEmptyCard());
    }
  }

  function renderFilledCard(drink) {
    const wrap = document.createElement('div');
    wrap.className = 'favorite_drinks';
    wrap.innerHTML = `
      <img src="${iconForType(drink.type)}" alt="" class="drink_img">
      <div class="drink_info1">
        <div class="info_left">
          <span class="drink_brand">${drink.brand_display}</span>
          <span class="drink_size">${drink.size || '-'}</span>
        </div>
        <span class="divider"></span>
        <div class="info_right">
          <span class="drink_name">${drink.name}</span>
          <span class="drink_caffeine">${drink.caffeine_mg}mg</span>
        </div>
      </div>
      <button type="button" class="edit_btn">수정</button>
    `;
    wrap.querySelector('.edit_btn').addEventListener('click', () => openWizard('edit', drink.id));
    return wrap;
  }

  function renderEmptyCard() {
    const wrap = document.createElement('div');
    wrap.className = 'favorite_drinks is-empty';
    wrap.innerHTML = `
      <img src="${window.CD_DRINK_ICONS.other}" alt="" class="drink_img">
      <div class="drink_info1">
        <div class="info_right">
          <span class="drink_name">비어있음</span>
        </div>
      </div>
      <button type="button" class="edit_btn">추가</button>
    `;
    wrap.querySelector('.edit_btn').addEventListener('click', () => openWizard('add'));
    return wrap;
  }

  // ── 오버레이 마법사 ────────────────────────────────────────────

  function showStep(key) {
    Object.values(steps).forEach((el) => { el.style.display = 'none'; });
    steps[key].style.display = '';
  }

  function clearOptionList(stepEl) {
    stepEl.querySelector('.option_list').innerHTML = '';
  }

  function renderOptionList(stepEl, items, onSelect) {
    const list = stepEl.querySelector('.option_list');
    list.innerHTML = '';
    items.forEach(({ value, label }) => {
      const item = document.createElement('div');
      item.className = 'option_item';
      item.dataset.value = value;
      item.innerHTML = `<span>${label}</span>`;
      item.addEventListener('click', () => {
        list.querySelectorAll('.option_item').forEach((el) => el.classList.remove('is-selected'));
        item.classList.add('is-selected');
        onSelect(value);
      });
      list.appendChild(item);
    });
  }

  function openWizard(mode, editingId) {
    wizard = { mode, editingId: editingId ?? null, type: null, brand: null, name: null, size: null, presetsForType: [] };
    steps.type.querySelectorAll('.option_item').forEach((el) => el.classList.remove('is-selected'));
    clearOptionList(steps.brand);
    clearOptionList(steps.menu);
    clearOptionList(steps.size);
    showStep('type');
    overlay.style.display = 'flex';
  }

  function closeWizard() {
    overlay.style.display = 'none';
  }

  async function loadBrandOptions() {
    const res = await apiFetch('/users/me/drinks/presets/?type=' + encodeURIComponent(wizard.type));
    wizard.presetsForType = res.ok ? await res.json() : [];

    const seen = new Map();
    wizard.presetsForType.forEach((p) => { if (!seen.has(p.brand)) seen.set(p.brand, p.brand_name); });
    renderOptionList(steps.brand, [...seen.entries()].map(([value, label]) => ({ value, label })), (value) => {
      wizard.brand = value;
    });
  }

  function loadMenuOptions() {
    const names = [...new Set(
      wizard.presetsForType.filter((p) => p.brand === wizard.brand).map((p) => p.name)
    )];
    renderOptionList(steps.menu, names.map((n) => ({ value: n, label: n })), (value) => {
      wizard.name = value;
    });
  }

  function loadSizeOptions() {
    const matches = wizard.presetsForType.filter((p) => p.brand === wizard.brand && p.name === wizard.name);
    renderOptionList(
      steps.size,
      matches.map((p) => ({ value: p.size, label: `${p.size} · ${p.caffeine_mg}mg` })),
      (value) => { wizard.size = value; }
    );
  }

  async function saveDrink() {
    let res;
    if (wizard.mode === 'add') {
      res = await apiFetch('/users/me/drinks/from-preset/', {
        method: 'POST',
        body: JSON.stringify({ brand: wizard.brand, name: wizard.name, size: wizard.size, is_favorite: true }),
      });
    } else {
      const preset = wizard.presetsForType.find(
        (p) => p.brand === wizard.brand && p.name === wizard.name && p.size === wizard.size
      );
      res = await apiFetch(`/users/me/drinks/${wizard.editingId}/`, {
        method: 'PATCH',
        body: JSON.stringify({
          type: wizard.type,
          brand: wizard.brand,
          custom_brand_name: '',
          name: wizard.name,
          size: wizard.size,
          caffeine_mg: preset.caffeine_mg,
          is_favorite: true,
        }),
      });
    }
    if (!res.ok) {
      alert('저장에 실패했어요. 다시 시도해주세요.');
      return;
    }
    closeWizard();
    await loadFavorites();
  }

  steps.type.querySelectorAll('.option_item').forEach((el) => {
    el.addEventListener('click', () => {
      steps.type.querySelectorAll('.option_item').forEach((o) => o.classList.remove('is-selected'));
      el.classList.add('is-selected');
      wizard.type = el.dataset.type;
    });
  });

  steps.type.querySelector('.next_btn').addEventListener('click', async () => {
    if (!wizard.type) { alert('종류를 선택해주세요.'); return; }
    await loadBrandOptions();
    showStep('brand');
  });

  steps.brand.querySelector('.next_btn').addEventListener('click', () => {
    if (!wizard.brand) { alert('브랜드를 선택해주세요.'); return; }
    loadMenuOptions();
    showStep('menu');
  });

  steps.menu.querySelector('.next_btn').addEventListener('click', () => {
    if (!wizard.name) { alert('메뉴를 선택해주세요.'); return; }
    loadSizeOptions();
    showStep('size');
  });

  saveBtn.addEventListener('click', () => {
    if (!wizard.size) { alert('사이즈를 선택해주세요.'); return; }
    saveDrink();
  });

  closeBtn.addEventListener('click', closeWizard);
  overlay.addEventListener('click', (e) => { if (e.target === overlay) closeWizard(); });

  loadFavorites();
})();
