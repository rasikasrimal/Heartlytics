document.addEventListener('DOMContentLoaded', () => {
  const nameInput = document.getElementById('username');
  const emailInput = document.getElementById('email');
  const passwordInput = document.getElementById('password');
  const confirmInput = document.getElementById('confirm');
  const submitBtn = document.getElementById('create-account');
  const bars = document.querySelectorAll('#password-strength div');
  const strengthText = document.getElementById('password-strength-text');
  const pwError = document.querySelector('#password-field .invalid-feedback');
  const confirmError = document.querySelector('#confirm-field .invalid-feedback');

  function scorePassword(val) {
    return [
      val.length >= 8,
      /[A-Z]/.test(val),
      /[a-z]/.test(val),
      /\d/.test(val),
      /[^A-Za-z0-9]/.test(val)
    ].filter(Boolean).length;
  }

  function updateStrength() {
    const val = passwordInput.value;
    const score = scorePassword(val);
    bars.forEach((bar, idx) => {
      bar.className = 'flex-grow-1 rounded';
      if (idx < score) {
        if (score <= 2) bar.classList.add('bg-danger');
        else if (score <= 4) bar.classList.add('bg-warning');
        else bar.classList.add('bg-success');
      } else {
        bar.classList.add('bg-body-secondary');
      }
    });
    if (score <= 2) strengthText.textContent = 'Weak password';
    else if (score <= 4) strengthText.textContent = 'Medium strength';
    else strengthText.textContent = 'Strong password';
    return score;
  }

  function validate() {
    const score = updateStrength();
    const match = passwordInput.value && passwordInput.value === confirmInput.value;
    const allFilled = nameInput.value && emailInput.value && passwordInput.value && confirmInput.value;
    const strong = score === 5;
    submitBtn.disabled = !(allFilled && strong && match);

    if (!strong && passwordInput.value) {
      passwordInput.classList.add('is-invalid');
      pwError.classList.remove('d-none');
    } else {
      passwordInput.classList.remove('is-invalid');
      pwError.classList.add('d-none');
    }

    if (confirmInput.value && !match) {
      confirmInput.classList.add('is-invalid');
      confirmError.classList.remove('d-none');
    } else {
      confirmInput.classList.remove('is-invalid');
      confirmError.classList.add('d-none');
    }
  }

  [nameInput, emailInput, passwordInput, confirmInput].forEach(el => {
    el.addEventListener('input', validate);
  });
  validate();
});
