// OTP segmented input handler
// Handles auto-tab, backspace navigation, and pasting full codes

document.addEventListener('DOMContentLoaded', () => {
  const group = document.getElementById('otp-group');
  if (!group) return;
  const inputs = group.querySelectorAll('.otp-input');
  const hidden = document.getElementById('otp-hidden');

  const updateHidden = () => {
    hidden.value = Array.from(inputs).map(i => i.value).join('');
  };

  inputs.forEach((input, idx) => {
    input.addEventListener('input', (e) => {
      const val = e.target.value.replace(/\D/g, '');
      e.target.value = val;
      if (val && idx < inputs.length - 1) {
        inputs[idx + 1].focus();
      }
      updateHidden();
    });
    input.addEventListener('keydown', (e) => {
      if (e.key === 'Backspace' && !e.target.value && idx > 0) {
        inputs[idx - 1].focus();
      }
    });
  });

  group.addEventListener('paste', (e) => {
    const text = (e.clipboardData || window.clipboardData).getData('text').replace(/\D/g, '');
    if (text.length === inputs.length) {
      inputs.forEach((input, i) => input.value = text[i]);
      updateHidden();
    }
    e.preventDefault();
  });
});
