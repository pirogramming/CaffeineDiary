/**
 * main.js — 루트(/) 브랜드 스플래시 화면 전용 스크립트
 * 지금은 페이지 진입 시 로고/버튼이 살짝 떠오르며 나타나는 연출만 담당한다. 
 * 버튼(회원가입/로그인)은 그냥 <a> 링크라
 * 별도 이벤트 바인딩이 필요 없다.
 */

document.addEventListener('DOMContentLoaded', () => {
  const content = document.querySelector('.cd-landing__content');
  if (!content) return;

  const prefersReducedMotion = window.matchMedia('(prefers-reduced-motion: reduce)').matches;
  if (prefersReducedMotion) return;

  content.style.opacity = '0';
  content.style.transform = 'translateY(12px)';
  content.style.transition = 'opacity 0.5s ease, transform 0.5s ease';

  requestAnimationFrame(() => {
    content.style.opacity = '1';
    content.style.transform = 'translateY(0)';
  });
});