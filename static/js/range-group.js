// Enhances all input[type=range] with a small number box and +/- step buttons
// - Two-way sync: slider <-> number
// - +/- buttons step by input.step (default 1)
// - Arrow keys on the number input also step value
// - Appends min/max info for accessibility

document.addEventListener('DOMContentLoaded', () => {
  const ranges = Array.from(document.querySelectorAll('input[type="range"]'));
  if (!ranges.length) return;

  const processed = new WeakSet();

  const clamp = (val, min, max) => Math.min(max, Math.max(min, val));

  const getStep = (el) => {
    const raw = el.getAttribute('step');
    if (!raw || raw === 'any') return 1;
    const s = parseFloat(raw);
    return Number.isFinite(s) && s > 0 ? s : 1;
  };

  const decimals = (n) => {
    if (!isFinite(n)) return 0;
    const s = n.toString();
    const i = s.indexOf('.');
    return i === -1 ? 0 : (s.length - i - 1);
  };

  const roundToStep = (val, step, min) => {
    // Align value to nearest step offset from min
    const d = decimals(step);
    const scaled = Math.round((val - min) / step) * step + min;
    return parseFloat(scaled.toFixed(d));
  };

  function enhanceRange(range) {
    if (processed.has(range)) return;
    processed.add(range);

    const min = parseFloat(range.getAttribute('min') || '0');
    const max = parseFloat(range.getAttribute('max') || '100');
    const step = getStep(range);
    const d = decimals(step);

    // Build inline group: [-] [range] [+] [number]
    const group = document.createElement('div');
    group.className = 'd-flex align-items-center range-group';

    const btnDec = document.createElement('button');
    btnDec.type = 'button';
    btnDec.className = 'btn btn-outline-secondary range-btn';
    btnDec.setAttribute('aria-label', 'Decrease');
    btnDec.textContent = '−';

    const btnInc = document.createElement('button');
    btnInc.type = 'button';
    btnInc.className = 'btn btn-outline-secondary range-btn';
    btnInc.setAttribute('aria-label', 'Increase');
    btnInc.textContent = '+';

    const num = document.createElement('input');
    num.type = 'number';
    num.className = 'form-control form-control-sm range-number';
    num.min = String(min);
    num.max = String(max);
    num.step = String(step);
    num.value = range.value;
    // Better mobile keyboards
    num.setAttribute('inputmode', d > 0 ? 'decimal' : 'numeric');

    // Move the range into the group, keeping its id/attrs intact
    range.classList.add('flex-grow-1');
    range.style.margin = '0';

    // Replace the original range in DOM with the group container
    const parent = range.parentElement;
    parent.insertBefore(group, range);
    group.appendChild(btnDec);
    group.appendChild(range);
    group.appendChild(btnInc);
    group.appendChild(num);

    // Update any companion span like #<id>-value
    const updateValueSpan = () => {
      const out = document.getElementById(range.id + '-value');
      if (out) out.textContent = range.value;
    };

    // Keep number within bounds and aligned to step
    const setNumber = (v, syncSlider = true) => {
      let nv = parseFloat(v);
      if (!Number.isFinite(nv)) nv = min;
      nv = clamp(nv, min, max);
      nv = roundToStep(nv, step, min);
      num.value = nv.toFixed(d);
      if (d === 0) num.value = String(parseInt(num.value, 10));
      if (syncSlider) {
        range.value = String(nv);
        // Fire input so existing logic reacts (charts, text, etc.)
        range.dispatchEvent(new Event('input', { bubbles: true }));
      }
      updateValueSpan();
    };

    // Sync: slider -> number
    range.addEventListener('input', () => {
      num.value = parseFloat(range.value).toFixed(d);
      if (d === 0) num.value = String(parseInt(num.value, 10));
      updateValueSpan();
    });

    // Sync: number -> slider (realtime)
    num.addEventListener('input', () => {
      setNumber(num.value, true);
    });

    // Buttons
    const bump = (dir) => {
      const current = parseFloat(range.value);
      const next = clamp(current + dir * step, min, max);
      setNumber(next, true);
      // Keep focus on num for quick repeated taps
      num.focus();
      num.select();
    };
    btnDec.addEventListener('click', () => bump(-1));
    btnInc.addEventListener('click', () => bump(1));

    // Keyboard on number: arrows adjust by step
    num.addEventListener('keydown', (e) => {
      if (e.key === 'ArrowUp' || e.key === 'ArrowRight') {
        e.preventDefault();
        bump(1);
      } else if (e.key === 'ArrowDown' || e.key === 'ArrowLeft') {
        e.preventDefault();
        bump(-1);
      }
    });

    // Show min/max in existing helper text for accessibility
    const field = group.closest('.mb-3');
    const helper = field ? field.querySelector('.form-text') : null;
    if (helper && !helper.querySelector('.range-minmax')) {
      const mm = document.createElement('small');
      mm.className = 'text-muted range-minmax ms-2';
      // Use en dash for range
      mm.textContent = `(min ${min}, max ${max})`;
      helper.appendChild(mm);
    }
  }

  ranges.forEach(enhanceRange);
});
