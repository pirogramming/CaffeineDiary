/**
 * favorites.js — 즐겨찾는 음료(최대 3개) 목록을 GET /users/me/drinks/로 채우고,
 * "추가"/"수정" 오버레이(종류→브랜드→메뉴→사이즈→아이콘)로 선택한 프리셋을
 * POST .../from-preset/(추가) 또는 PATCH .../<id>/(교체)로 저장한다.
 * 브랜드 단계에서 "직접입력"을 고르면 메뉴/사이즈 프리셋 단계 대신 자유 입력
 * 폼으로 가고, POST/PATCH .../drinks/(직접입력 전용 엔드포인트)로 저장한다.
 * 메뉴(음료명) 단계에서 "직접입력"을 고르면(브랜드는 카탈로그 유지) 이름과
 * 카페인량만 직접 입력받고, 사이즈는 그 브랜드의 기존 사이즈 목록을 그대로
 * 보여준다 — DrinkSerializer가 브랜드가 custom이 아니면 사이즈를 카탈로그
 * 라벨로만 허용하기 때문에(자유 입력 사이즈는 서버에서 거부된다) 이 단계의
 * 사이즈는 항상 카탈로그에서 골라야 한다.
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
    menuCustom: overlay.querySelector('[data-step="menu-custom"]'),
    size: overlay.querySelector('[data-step="4"]'),
    custom: overlay.querySelector('[data-step="custom"]'),
    icon: overlay.querySelector('[data-step="5"]'),
  };

  const customBrandInput = document.getElementById('custom-brand-input');
  const customNameInput = document.getElementById('custom-name-input');
  const customSizeInput = document.getElementById('custom-size-input');
  const customCaffeineInput = document.getElementById('custom-caffeine-input');
  const customNextBtn = document.getElementById('wizard-custom-next-btn');

  const customMenuNameInput = document.getElementById('custom-menu-name-input');
  const customMenuCaffeineInput = document.getElementById('custom-menu-caffeine-input');
  const menuCustomNextBtn = document.getElementById('wizard-menu-custom-next-btn');

  const MENU_CUSTOM_VALUE = '__custom__'; // 실제 메뉴명과 겹치지 않도록 예약된 값

  let wizard = {
    mode: 'add', editingId: null,
    type: null, brand: null, name: null, size: null, iconKey: null,
    nameIsCustom: false, customBrandName: '', caffeineMg: null,
    presetsForType: [],
  };

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
      <img src="${cdIconForDrink(drink)}" alt="" class="drink_img">
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

  function renderIconOptionList(stepEl, options, onSelect) {
    const list = stepEl.querySelector('.option_list');
    list.innerHTML = '';
    options.forEach(({ key, src }) => {
      const item = document.createElement('div');
      item.className = 'option_item';
      item.dataset.value = key;
      item.innerHTML = `<img src="${src}" alt="">`;
      item.addEventListener('click', () => {
        list.querySelectorAll('.option_item').forEach((el) => el.classList.remove('is-selected'));
        item.classList.add('is-selected');
        onSelect(key);
      });
      list.appendChild(item);
    });
  }

  function openWizard(mode, editingId) {
    wizard = {
      mode, editingId: editingId ?? null,
      type: null, brand: null, name: null, size: null, iconKey: null,
      nameIsCustom: false, customBrandName: '', caffeineMg: null,
      presetsForType: [],
    };
    steps.type.querySelectorAll('.option_item').forEach((el) => el.classList.remove('is-selected'));
    clearOptionList(steps.brand);
    clearOptionList(steps.menu);
    clearOptionList(steps.size);
    clearOptionList(steps.icon);
    customBrandInput.value = '';
    customNameInput.value = '';
    customSizeInput.value = '';
    customCaffeineInput.value = '';
    customMenuNameInput.value = '';
    customMenuCaffeineInput.value = '';
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
    const options = [...seen.entries()].map(([value, label]) => ({ value, label }));
    options.push({ value: 'custom', label: '직접입력' });
    renderOptionList(steps.brand, options, (value) => {
      wizard.brand = value;
    });
  }

  function loadMenuOptions() {
    const names = [...new Set(
      wizard.presetsForType.filter((p) => p.brand === wizard.brand).map((p) => p.name)
    )];
    const options = names.map((n) => ({ value: n, label: n }));
    options.push({ value: MENU_CUSTOM_VALUE, label: '직접입력' });
    renderOptionList(steps.menu, options, (value) => {
      wizard.nameIsCustom = value === MENU_CUSTOM_VALUE;
      wizard.name = wizard.nameIsCustom ? null : value;
    });
    // 새로 그린 목록이라 전부 보이는 상태 — 검색창만 비워서 이전 검색어가 안 남게 한다.
    if (menuSearchInput) menuSearchInput.value = '';
  }

  // 메뉴 목록을 검색어로 실시간 필터링한다. 한 글자 입력될 때마다(input 이벤트) 다시 걸러진다.
  const menuSearchInput = steps.menu.querySelector('[data-option-search]');
  menuSearchInput?.addEventListener('input', () => {
    const q = menuSearchInput.value.trim().toLowerCase();
    steps.menu.querySelectorAll('.option_item').forEach((item) => {
      if (item.dataset.value === MENU_CUSTOM_VALUE) return; // "직접입력"은 검색과 무관하게 항상 노출
      item.hidden = q.length > 0 && !item.textContent.trim().toLowerCase().includes(q);
    });
  });

  function loadSizeOptions() {
    const matches = wizard.presetsForType.filter((p) => p.brand === wizard.brand && p.name === wizard.name);
    renderOptionList(
      steps.size,
      matches.map((p) => ({ value: p.size, label: `${p.size} · ${p.caffeine_mg}mg` })),
      (value) => { wizard.size = value; }
    );
  }

  // 메뉴가 직접입력이면 특정 이름에 매칭되는 프리셋이 없으므로, 사이즈는 그
  // 브랜드가 취급하는 사이즈 라벨 전체(이름 무관)에서 고른다. 카페인량은
  // 프리셋에 없으니 라벨에 mg를 붙이지 않는다 — 사용자가 직접 입력한 값을 쓴다.
  function loadSizeOptionsForBrand() {
    const sizes = [...new Set(
      wizard.presetsForType.filter((p) => p.brand === wizard.brand).map((p) => p.size)
    )].filter(Boolean);
    renderOptionList(
      steps.size,
      sizes.map((s) => ({ value: s, label: s })),
      (value) => { wizard.size = value; }
    );
  }

  function loadIconOptions() {
    const options = window.CD_DRINK_ICON_OPTIONS[wizard.type] || window.CD_DRINK_ICON_OPTIONS.other;
    renderIconOptionList(steps.icon, options, (key) => {
      wizard.iconKey = key;
    });
  }

  async function saveDrink() {
    let res;
    if (wizard.brand === 'custom' || wizard.nameIsCustom) {
      // 브랜드 전체 직접입력이거나, 브랜드는 카탈로그인데 메뉴명만 직접입력인 경우.
      // 두 경우 다 카페인량을 서버 프리셋에서 조회할 수 없으므로 사용자가 입력한
      // 값을 그대로 쓴다. custom_brand_name은 brand=custom일 때만 의미가 있다
      // (DrinkSerializer.validate가 그 외엔 어차피 빈 값으로 정리하지만 명시한다).
      const payload = {
        type: wizard.type,
        brand: wizard.brand,
        custom_brand_name: wizard.brand === 'custom' ? wizard.customBrandName : '',
        name: wizard.name,
        size: wizard.size,
        caffeine_mg: wizard.caffeineMg,
        icon_key: wizard.iconKey,
        is_favorite: true,
      };
      res = wizard.mode === 'add'
        ? await apiFetch('/users/me/drinks/', { method: 'POST', body: JSON.stringify(payload) })
        : await apiFetch(`/users/me/drinks/${wizard.editingId}/`, { method: 'PATCH', body: JSON.stringify(payload) });
    } else if (wizard.mode === 'add') {
      res = await apiFetch('/users/me/drinks/from-preset/', {
        method: 'POST',
        body: JSON.stringify({
          brand: wizard.brand, name: wizard.name, size: wizard.size,
          icon_key: wizard.iconKey, is_favorite: true,
        }),
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
          icon_key: wizard.iconKey,
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
    if (wizard.brand === 'custom') {
      showStep('custom');
      return;
    }
    loadMenuOptions();
    showStep('menu');
  });

  customNextBtn.addEventListener('click', () => {
    const name = customNameInput.value.trim();
    const caffeine = Number(customCaffeineInput.value);
    if (!name) { alert('음료 이름을 입력해주세요.'); return; }
    if (!customCaffeineInput.value || !(caffeine > 0 && caffeine <= 1000)) {
      alert('카페인 함량을 1~1000mg 사이로 입력해주세요.');
      return;
    }
    wizard.customBrandName = customBrandInput.value.trim();
    wizard.name = name;
    wizard.size = customSizeInput.value.trim();
    wizard.caffeineMg = caffeine;
    loadIconOptions();
    showStep('icon');
  });

  steps.menu.querySelector('.next_btn').addEventListener('click', () => {
    if (!wizard.name && !wizard.nameIsCustom) { alert('메뉴를 선택해주세요.'); return; }
    if (wizard.nameIsCustom) {
      showStep('menuCustom');
      return;
    }
    loadSizeOptions();
    showStep('size');
  });

  menuCustomNextBtn.addEventListener('click', () => {
    const name = customMenuNameInput.value.trim();
    const caffeine = Number(customMenuCaffeineInput.value);
    if (!name) { alert('음료 이름을 입력해주세요.'); return; }
    if (!customMenuCaffeineInput.value || !(caffeine > 0 && caffeine <= 1000)) {
      alert('카페인 함량을 1~1000mg 사이로 입력해주세요.');
      return;
    }
    wizard.name = name;
    wizard.caffeineMg = caffeine;
    loadSizeOptionsForBrand();
    showStep('size');
  });

  steps.size.querySelector('.next_btn').addEventListener('click', () => {
    if (!wizard.size) { alert('사이즈를 선택해주세요.'); return; }
    loadIconOptions();
    showStep('icon');
  });

  saveBtn.addEventListener('click', () => {
    if (!wizard.iconKey) { alert('아이콘을 선택해주세요.'); return; }
    saveDrink();
  });

  closeBtn.addEventListener('click', closeWizard);
  overlay.addEventListener('click', (e) => { if (e.target === overlay) closeWizard(); });

  loadFavorites();
})();
