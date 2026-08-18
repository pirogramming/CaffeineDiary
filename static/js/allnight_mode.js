document.addEventListener('DOMContentLoaded', function () {
    // 오늘의 스케줄 토글
    const scheduleToggle = document.getElementById('scheduleToggle');
    const scheduleList = document.getElementById('scheduleList');

    if (scheduleToggle && scheduleList) {
        scheduleToggle.addEventListener('click', function () {
            scheduleToggle.classList.toggle('collapsed');
            scheduleList.classList.toggle('collapsed');
        });
    }
});

document.addEventListener('DOMContentLoaded', function () {
    // 모바일 햄버거 메뉴 — base.js와 동일한 로직
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