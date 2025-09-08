// Auth-related client-side interactions
// Password visibility toggle and signup form enhancements

document.addEventListener('DOMContentLoaded', () => {
  // Toggle password visibility
  document.querySelectorAll('.password-toggle').forEach(btn => {
    btn.addEventListener('click', () => {
      const input = btn.previousElementSibling;
      const icon = btn.querySelector('i');
      if (input.type === 'password') {
        input.type = 'text';
        icon.classList.replace('bi-eye', 'bi-eye-slash');
      } else {
        input.type = 'password';
        icon.classList.replace('bi-eye-slash', 'bi-eye');
      }
    });
  });

  const signupForm = document.getElementById('signupForm');
  if (signupForm) {
    const username = signupForm.querySelector('#username');
    const email = signupForm.querySelector('#email');
    const password = signupForm.querySelector('#password');
    const confirm = signupForm.querySelector('#confirm');
    const role = signupForm.querySelector('#role');
    const submit = document.getElementById('createAccount');
    const usernameError = username.closest('.mb-3').querySelector('.invalid-feedback');
    const emailError = email.closest('.mb-3').querySelector('.invalid-feedback');
    const bars = document.querySelectorAll('#' + password.id + '-bars [data-bar]');
    const caption = document.getElementById(password.id + '-caption');
    const hints = {};
    document.querySelectorAll('#' + password.id + '-strength [data-rule]').forEach(el => {
      hints[el.dataset.rule] = el;
    });
    const confirmError = confirm.closest('.mb-3').querySelector('.invalid-feedback');

    const strengthLabels = ['Very weak','Weak','Fair','Good','Strong'];

    function updatePassword() {
      const val = password.value;
      const checks = {
        length: val.length >= 8,
        uppercase: /[A-Z]/.test(val),
        lowercase: /[a-z]/.test(val),
        number: /\d/.test(val),
        special: /[!@#$%^&*]/.test(val)
      };
      let score = 0;
      Object.entries(checks).forEach(([rule, passed], idx) => {
        const text = hints[rule].textContent.slice(2);
        hints[rule].textContent = (passed ? '✅ ' : '❌ ') + text;
        hints[rule].classList.toggle('text-success', passed);
        hints[rule].classList.toggle('text-danger', !passed);
        bars[idx].style.opacity = passed ? 1 : 0.2;
        if (passed) score++;
      });
      caption.textContent = strengthLabels[score];
      password.classList.toggle('is-invalid', score < 5 && password.value.length > 0);
      password.classList.toggle('is-valid', score === 5);
      return score === 5;
    }

    function validateConfirm(passOk) {
      const match = confirm.value === password.value && passOk;
      confirm.classList.toggle('is-invalid', !match && confirm.value.length > 0);
      confirm.classList.toggle('is-valid', match);
      if (confirmError) confirmError.textContent = (!match && confirm.value.length > 0) ? 'Passwords do not match' : '';
      return match;
    }

    function validateEmailFormat() {
      const ok = email.checkValidity();
      email.classList.toggle('is-invalid', !ok);
      email.classList.toggle('is-valid', ok && email.value.trim() !== '');
      if (emailError) emailError.textContent = ok ? '' : 'Enter a valid email address';
      return ok;
    }

    function checkForm() {
      const passOk = updatePassword();
      const matchOk = validateConfirm(passOk);
      const userOk = username.value.trim() !== '';
      username.classList.toggle('is-invalid', !userOk && username.value.trim() !== '');
      username.classList.toggle('is-valid', userOk);
      if (usernameError && userOk) usernameError.textContent = '';
      const emailFormatOk = validateEmailFormat();
      if (emailFormatOk && emailError) emailError.textContent = '';
      const ready = userOk && emailFormatOk && role.value && passOk && matchOk;
      submit.disabled = !ready;
    }

    ['input', 'change'].forEach(evt => {
      username.addEventListener(evt, checkForm);
      email.addEventListener(evt, checkForm);
      role.addEventListener(evt, checkForm);
      password.addEventListener(evt, checkForm);
      confirm.addEventListener(evt, checkForm);
    });

    signupForm.addEventListener('submit', async e => {
      e.preventDefault();
      submit.disabled = true;
      const resp = await fetch(signupForm.action, {
        method: 'POST',
        body: new FormData(signupForm),
        headers: { 'X-Requested-With': 'XMLHttpRequest' }
      });
      submit.disabled = false;
      if (resp.ok) {
        const toastEl = document.getElementById('signupToast');
        if (toastEl && typeof bootstrap !== 'undefined') {
          new bootstrap.Toast(toastEl).show();
        }
        document.getElementById('signupSection').classList.add('d-none');
        document.getElementById('verifySection').classList.remove('d-none');
      } else {
        const data = await resp.json().catch(() => ({}));
        if (data.error === 'username') {
          username.classList.add('is-invalid');
          if (usernameError) usernameError.textContent = 'Username taken';
        } else if (data.error === 'email') {
          email.classList.add('is-invalid');
          if (emailError) emailError.textContent = 'Email already registered';
        }
      }
    });
  }

  const otpGroup = document.querySelector('[data-otp-group]');
  if (otpGroup) {
    const verifyBtn = document.getElementById('verifyBtn');
    const sendOtp = document.getElementById('sendOtp');
    const hidden = otpGroup.querySelector('input[type="hidden"]');
    otpGroup.addEventListener('input', () => {
      verifyBtn.disabled = hidden.value.length !== 6;
    });
    if (sendOtp) {
      sendOtp.addEventListener('click', () => {
        if (email.value) {
          console.log('OTP sent to', email.value);
        }
      });
    }
  }
});
