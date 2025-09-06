document.addEventListener('DOMContentLoaded', () => {
  const nav = document.getElementById('topNav');
  if (!nav) return;
  const onScroll = () => {
    if (window.scrollY > 0) {
      nav.classList.add('nav-elevated');
    } else {
      nav.classList.remove('nav-elevated');
    }
  };
  onScroll();
  window.addEventListener('scroll', onScroll, { passive: true });
});
