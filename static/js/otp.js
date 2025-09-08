function startOtpCountdown(id, seconds) {
  const btn = document.getElementById(id);
  if (!btn) return;
  let remaining = seconds;
  const label = btn.textContent;
  btn.disabled = true;
  const tick = () => {
    if (remaining <= 0) {
      btn.disabled = false;
      btn.textContent = label;
      return;
    }
    btn.textContent = `${label} (${remaining--})`;
    setTimeout(tick, 1000);
  };
  tick();
}
