document.addEventListener('DOMContentLoaded', () => {
  document.querySelectorAll('.avatar-edit').forEach(el => {
    el.addEventListener('mouseenter', () => el.classList.add('hover'));
    el.addEventListener('mouseleave', () => el.classList.remove('hover'));
  });
});
