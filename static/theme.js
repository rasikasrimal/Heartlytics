(function(){
  const STORAGE_KEY = 'theme';
  const COOKIE_ATTRS = 'Path=/; Max-Age=31536000';

  function applyTheme(theme){
    const root = document.documentElement;
    root.dataset.bsTheme = theme;
    document.body.classList.toggle('theme-dark', theme === 'dark');
    document.cookie = `theme=${theme}; ${COOKIE_ATTRS}`;
    const meta = document.querySelector('meta[name="theme-color"]');
    if (meta){
      const bg = getComputedStyle(document.body).getPropertyValue('--bs-body-bg').trim();
      meta.content = bg || '#ffffff';
    }
    const btn = document.getElementById('theme-toggle');
    if (btn){
      const icon = btn.querySelector('i');
      if (icon){
        icon.className = theme === 'dark' ? 'bi bi-sun-fill' : 'bi bi-moon-fill';
      }
    }
  }

  function setTheme(mode){
    localStorage.setItem(STORAGE_KEY, mode);
    const theme = mode === 'system'
      ? (window.matchMedia('(prefers-color-scheme: dark)').matches ? 'dark' : 'light')
      : mode;
    applyTheme(theme);
    window.dispatchEvent(new Event('themechange'));
  }

  function toggleTheme(){
    const current = document.documentElement.dataset.bsTheme;
    setTheme(current === 'dark' ? 'light' : 'dark');
  }

  function init(){
    setTheme(localStorage.getItem(STORAGE_KEY) || 'light');
    const btn = document.getElementById('theme-toggle');
    if (btn){
      btn.addEventListener('click', toggleTheme);
    }
    // Expose for settings page
    window.setTheme = setTheme;
    if (window.matchMedia) {
      window.matchMedia('(prefers-color-scheme: dark)').addEventListener('change', () => {
        if (localStorage.getItem(STORAGE_KEY) === 'system') setTheme('system');
      });
    }
  }

  if (document.readyState !== 'loading') init();
  else document.addEventListener('DOMContentLoaded', init);
})();
