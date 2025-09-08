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

    const usernameGroup = username.closest('.mb-3');
    const emailGroup = email.closest('.mb-3');
    usernameGroup.style.position = 'relative';
    emailGroup.style.position = 'relative';
    const usernameSpinner = document.createElement('div');
    usernameSpinner.className = 'spinner-border spinner-border-sm position-absolute top-50 end-0 translate-middle-y me-2 d-none';
    usernameSpinner.setAttribute('role', 'status');
    usernameSpinner.setAttribute('aria-hidden', 'true');
    usernameGroup.appendChild(usernameSpinner);
    const emailSpinner = document.createElement('div');
    emailSpinner.className = 'spinner-border spinner-border-sm position-absolute top-50 end-0 translate-middle-y me-2 d-none';
    emailSpinner.setAttribute('role', 'status');
    emailSpinner.setAttribute('aria-hidden', 'true');
    emailGroup.appendChild(emailSpinner);

    const usernameCache = new Map();
    const emailCache = new Map();

    const debounce = (fn, delay = 400) => {
      let timer;
      return (...args) => {
        clearTimeout(timer);
        timer = setTimeout(() => fn(...args), delay);
      };
    };

    let usernameValid = false;
    let emailValid = false;

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
      if (!ok) {
        email.classList.add('is-invalid');
        email.classList.remove('is-valid');
        if (emailError) emailError.textContent = 'Enter a valid email address.';
      } else {
        email.classList.remove('is-invalid');
        if (emailError) emailError.textContent = '';
      }
      return ok;
    }

    function setUsernameState(available) {
      usernameValid = available;
      username.classList.toggle('is-valid', available);
      username.classList.toggle('is-invalid', !available && username.value.trim() !== '');
      if (usernameError) usernameError.textContent = available ? '' : 'username already taken';
    }

    const usernameAvailability = async () => {
      const value = username.value.trim();
      if (!value) {
        username.classList.remove('is-valid', 'is-invalid');
        if (usernameError) usernameError.textContent = '';
        usernameValid = false;
        return false;
      }
      if (usernameCache.has(value)) {
        setUsernameState(usernameCache.get(value));
        return usernameCache.get(value);
      }
      usernameSpinner.classList.remove('d-none');
      try {
        const resp = await fetch(`/auth/check-username?username=${encodeURIComponent(value)}`);
        const data = await resp.json();
        const ok = !!data.available;
        usernameCache.set(value, ok);
        setUsernameState(ok);
        return ok;
      } catch {
        usernameValid = false;
        return false;
      } finally {
        usernameSpinner.classList.add('d-none');
      }
    };

    const debouncedUsername = debounce(usernameAvailability);
    username.addEventListener('input', () => {
      usernameValid = false;
      username.classList.remove('is-valid', 'is-invalid');
      if (usernameError) usernameError.textContent = '';
      debouncedUsername();
    });
    username.addEventListener('blur', debouncedUsername);

    function setEmailState(available) {
      emailValid = available;
      email.classList.toggle('is-valid', available);
      email.classList.toggle('is-invalid', !available && email.value.trim() !== '');
      if (emailError) emailError.textContent = available ? '' : 'email already registered — Sign in?';
    }

    const emailAvailability = async () => {
      const value = email.value.trim();
      if (!value) {
        email.classList.remove('is-valid', 'is-invalid');
        if (emailError) emailError.textContent = '';
        emailValid = false;
        return false;
      }
      if (!validateEmailFormat()) {
        emailValid = false;
        return false;
      }
      if (emailCache.has(value)) {
        setEmailState(emailCache.get(value));
        return emailCache.get(value);
      }
      emailSpinner.classList.remove('d-none');
      try {
        const resp = await fetch(`/auth/check-email?email=${encodeURIComponent(value)}`);
        const data = await resp.json();
        const ok = !!data.available;
        emailCache.set(value, ok);
        setEmailState(ok);
        return ok;
      } catch {
        emailValid = false;
        return false;
      } finally {
        emailSpinner.classList.add('d-none');
      }
    };

    const debouncedEmail = debounce(emailAvailability);
    email.addEventListener('input', () => {
      emailValid = false;
      if (!validateEmailFormat()) return;
      email.classList.remove('is-valid');
      if (emailError) emailError.textContent = '';
      debouncedEmail();
    });
    email.addEventListener('blur', debouncedEmail);

    function formIsValid() {
      const passOk = updatePassword();
      const matchOk = validateConfirm(passOk);
      const roleOk = !!role.value;
      return usernameValid && emailValid && passOk && matchOk && roleOk;
    }

    password.addEventListener('input', () => {
      const passOk = updatePassword();
      validateConfirm(passOk);
    });
    confirm.addEventListener('input', () => {
      validateConfirm(updatePassword());
    });

    signupForm.addEventListener('submit', async e => {
      e.preventDefault();
      await Promise.all([usernameAvailability(), emailAvailability()]);
      if (!formIsValid()) return;
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
          setUsernameState(false);
        } else if (data.error === 'email') {
          setEmailState(false);
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
