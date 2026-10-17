(() => {
  const root = document.documentElement;
  root.classList.add('js');
  const theme = document.querySelector('.theme-toggle');
  const media = window.matchMedia('(prefers-color-scheme: dark)');
  try {
    const saved = localStorage.getItem('zw-theme');
    if (saved === 'light' || saved === 'dark') root.dataset.theme = saved;
  } catch (_) { /* Reading remains available when storage is blocked. */ }
  const isDark = () => root.dataset.theme ? root.dataset.theme === 'dark' : media.matches;
  const syncTheme = () => {
    theme.setAttribute('aria-pressed', String(isDark()));
    document.querySelector('meta[name="theme-color"]').content = isDark() ? '#19251f' : '#f6f5ef';
  };
  theme.hidden = false;
  syncTheme();
  media.addEventListener('change', syncTheme);
  theme.addEventListener('click', () => {
    root.dataset.theme = isDark() ? 'light' : 'dark';
    try { localStorage.setItem('zw-theme', root.dataset.theme); } catch (_) { /* Optional preference only. */ }
    syncTheme();
  });
  const menu = document.querySelector('.menu-toggle');
  const nav = document.querySelector('#navigation');
  menu.hidden = false;
  function closeMenu() {
    nav.classList.remove('is-open');
    menu.setAttribute('aria-expanded', 'false');
    menu.querySelector('span').textContent = '+';
  }
  menu.addEventListener('click', () => {
    const open = !nav.classList.contains('is-open');
    nav.classList.toggle('is-open', open);
    menu.setAttribute('aria-expanded', String(open));
    menu.querySelector('span').textContent = open ? '−' : '+';
  });
  nav.addEventListener('click', event => { if (event.target.closest('a')) closeMenu(); });
  document.addEventListener('keydown', event => {
    if (event.key === 'Escape' && nav.classList.contains('is-open')) { closeMenu(); menu.focus(); }
  });
})();
