/**
 * survey.js — 설문 화면 공통 스크립트 (1~4단계, 영수증 카드)
 * "내가 직접 입력" 입력창을 누르면 그 라디오가 자동 선택되면서 입력 가능해지고,
 * 다른 보기를 고르면 다시 잠긴다.
 *
 * disabled 대신 readonly를 쓰는 이유: disabled된 입력창은 브라우저에 따라
 * 클릭 이벤트 자체를 무시하는 경우가 있어 "눌러도 안 써지는" 문제가 생긴다.
 * readonly는 포커스/클릭은 항상 정상 동작하고, 값만 못 바꾸게 막아준다.
 */

document.querySelectorAll('[data-survey-options]').forEach((list) => {
  const customInput = list.querySelector('.cd-receipt__custom-input');
  const customRadio = list.querySelector('.cd-receipt__radio[value="custom"]');
  if (!customInput || !customRadio) return;

  const activateCustom = () => {
    customRadio.checked = true;
    customInput.readOnly = false;
    customInput.focus();
  };

  // 입력창을 직접 클릭/포커스하면 라디오도 같이 선택된다
  customInput.addEventListener('focus', activateCustom);
  customInput.addEventListener('click', activateCustom);

  // 다른(커스텀이 아닌) 보기를 선택하면 입력창을 다시 잠그고 비운다
  list.querySelectorAll('.cd-receipt__radio').forEach((radio) => {
    if (radio === customRadio) return;
    radio.addEventListener('change', () => {
      if (radio.checked) {
        customInput.readOnly = true;
        customInput.value = '';
      }
    });
  });

  // 커스텀 라디오를 라벨 클릭 등으로 선택했을 때도 입력창을 열어준다
  customRadio.addEventListener('change', () => {
    customInput.readOnly = !customRadio.checked;
    if (customRadio.checked) customInput.focus();
  });
});