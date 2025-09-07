document.addEventListener('DOMContentLoaded', () => {
  document.querySelectorAll('[data-file-preview]').forEach(input => {
    const preview = document.getElementById(input.dataset.filePreview);
    if (!preview) return;
    input.addEventListener('change', () => {
      if (input.files && input.files[0]) {
        preview.src = URL.createObjectURL(input.files[0]);
        preview.classList.remove('d-none');
      }
    });
  });

  document.querySelectorAll('.toggle-password').forEach(btn => {
    btn.addEventListener('click', () => {
      const input = btn.previousElementSibling;
      if (input.type === 'password') {
        input.type = 'text';
        btn.innerHTML = '<i class="bi bi-eye-slash"></i>';
      } else {
        input.type = 'password';
        btn.innerHTML = '<i class="bi bi-eye"></i>';
      }
      input.focus();
    });
  });

  if (document.body) {
    new bootstrap.ScrollSpy(document.body, { target: '#settingsNav', offset: 100 });
  }
});
