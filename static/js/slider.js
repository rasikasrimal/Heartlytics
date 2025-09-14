// Generic bindings for slider rows: range <-> number, +/- buttons, keyboard
(function(){
  function clamp(val, min, max){
    val = isNaN(val) ? min : val;
    if (min !== undefined && val < min) val = min;
    if (max !== undefined && val > max) val = max;
    return val;
  }

  function stepOf(el){
    const s = parseFloat(el.getAttribute('step'));
    return isNaN(s) || s <= 0 ? 1 : s;
  }

  function bindRow(row){
    const range = row.querySelector('input[type="range"]');
    const number = row.querySelector('input[type="number"]');
    const dec = row.querySelector('.btn-decrement');
    const inc = row.querySelector('.btn-increment');
    if (!range || !number) return;

    // Init number to range value
    number.value = range.value;

    // Helper to update optional display span like #age-value
    function updateDisplay(){
      const span = document.getElementById(range.id + '-value');
      if (span) span.textContent = range.value;
    }

    // Range -> Number
    range.addEventListener('input', function(){
      number.value = range.value;
      updateDisplay();
    });

    // Number -> Range
    function syncFromNumber(){
      const min = parseFloat(range.min); const max = parseFloat(range.max);
      let v = clamp(parseFloat(number.value), min, max);
      // Snap to step
      const step = stepOf(range);
      if (!isNaN(step) && step > 0) {
        v = Math.round(v / step) * step;
      }
      number.value = v;
      range.value = v;
      updateDisplay();
    }
    number.addEventListener('input', syncFromNumber);
    number.addEventListener('change', syncFromNumber);

    // +/- buttons
    if (dec) dec.addEventListener('click', function(){
      const step = stepOf(range); const min = parseFloat(range.min);
      let v = parseFloat(range.value) - step; v = clamp(v, min, parseFloat(range.max));
      range.value = v; number.value = v; updateDisplay();
    });
    if (inc) inc.addEventListener('click', function(){
      const step = stepOf(range); const max = parseFloat(range.max);
      let v = parseFloat(range.value) + step; v = clamp(v, parseFloat(range.min), max);
      range.value = v; number.value = v; updateDisplay();
    });

    // Keyboard on range: arrow keys adjust
    range.addEventListener('keydown', function(e){
      const step = stepOf(range);
      if (e.key === 'ArrowLeft' || e.key === 'ArrowDown'){
        e.preventDefault();
        let v = parseFloat(range.value) - step;
        range.value = clamp(v, parseFloat(range.min), parseFloat(range.max));
        number.value = range.value; updateDisplay();
      } else if (e.key === 'ArrowRight' || e.key === 'ArrowUp'){
        e.preventDefault();
        let v = parseFloat(range.value) + step;
        range.value = clamp(v, parseFloat(range.min), parseFloat(range.max));
        number.value = range.value; updateDisplay();
      }
    });
  }

  function init(){
    document.querySelectorAll('.slider-row').forEach(bindRow);
  }

  if (document.readyState !== 'loading') init();
  else document.addEventListener('DOMContentLoaded', init);
})();

