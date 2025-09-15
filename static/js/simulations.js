document.addEventListener('DOMContentLoaded', () => {
  const runBtn = document.getElementById('run-sim');
  const form = document.getElementById('sim-form');
  const variableSelect = document.getElementById('variable');
  const status = document.getElementById('sim-status');
  const announcer = document.getElementById('sim-status-announcer');
  const prediction = document.getElementById('prediction');
  const chart = document.getElementById('exercise-angina-chart');
  const inputs = [...form.querySelectorAll('input, select')];
  if (variableSelect) {
    inputs.push(variableSelect);
  }
  let initialized = false;
  let controller = null;
  let debounceTimer = null;
  let loaderTimer = null;
  let loaderVisible = false;
  let loaderStart = 0;

  function updateSliderValue(id) {
    const input = document.getElementById(id);
    const output = document.getElementById(id + '-value');
    if (input && output) {
      output.textContent = input.value;
    }
  }

  ['age', 'bp', 'chol', 'fbs', 'mhr', 'st_dep', 'nmv'].forEach(id => {
    updateSliderValue(id);
    const el = document.getElementById(id);
    if (el) {
      el.addEventListener('input', () => updateSliderValue(id));
    }
  });

  function showLoader() {
    loaderVisible = true;
    loaderStart = Date.now();
    status.innerHTML = '<span class="spinner-border spinner-border-sm" aria-hidden="true"></span>';
  }

  function hideLoader() {
    loaderVisible = false;
    status.innerHTML = '';
  }

  function showUpdated() {
    const ts = new Date();
    status.innerHTML = `<i class="bi bi-check2-circle text-success" aria-hidden="true"></i><time datetime="${ts.toISOString()}">Updated just now</time>`;
    announcer.textContent = 'Simulation updated';
    prediction.setAttribute('aria-busy', 'false');
  }

  function highlight() {
    [prediction, chart].forEach(el => {
      if (!el) return;
      el.classList.remove('update-flash');
      // trigger reflow
      void el.offsetWidth;
      el.classList.add('update-flash');
    });
  }

  function showToast(msg) {
    const toastEl = document.createElement('div');
    toastEl.className = 'toast align-items-center text-bg-danger border-0 position-fixed top-0 end-0 m-3';
    toastEl.innerHTML = `<div class="d-flex"><div class="toast-body">${msg}</div><button type="button" class="btn-close btn-close-white me-2 m-auto" data-bs-dismiss="toast"></button></div>`;
    document.body.appendChild(toastEl);
    const toast = new bootstrap.Toast(toastEl, { delay: 3000 });
    toastEl.addEventListener('hidden.bs.toast', () => toastEl.remove());
    toast.show();
  }

  function renderPrediction(pred) {
    if (!pred) {
      prediction.innerHTML = '';
      return;
    }

    // Derive risk band and classes similar to /predict
    const riskPct = pred.risk_pct;
    const confidencePct = pred.confidence_pct;
    let riskBand = null;
    if (riskPct !== null && riskPct !== undefined) {
      if (riskPct < 30) riskBand = 'Low';
      else if (riskPct < 60) riskBand = 'Moderate';
      else riskBand = 'High';
    }
    const isPositive = (pred.label || '').toLowerCase().includes('heart disease') && (pred.label || '').toLowerCase() !== 'no heart disease';
    const badgeClass = isPositive ? 'danger' : 'success';
    const barClass = riskBand === 'Low' ? 'success' : riskBand === 'Moderate' ? 'warning' : 'danger';

    let html = '';
    html += '<div class="mb-4">';
    html += `<span class="badge rounded-pill fs-5 bg-${badgeClass}">${isPositive ? 'Risk Detected' : 'No Heart Disease'}</span>`;
    if (riskBand) {
      html += `<span class="badge bg-secondary fs-6 ms-2">${riskBand} risk band</span>`;
    }
    html += '</div>';

    if (riskPct !== null && riskPct !== undefined) {
      html += '<h5 class="mb-2">Risk Percentage</h5>';
      html += `<div class="progress progress-hover mb-4" role="progressbar" aria-valuenow="${riskPct}" aria-valuemin="0" aria-valuemax="100" data-bs-toggle="tooltip" title="${riskBand || ''} Risk (${riskPct}%)">`;
      html += `<div class="progress-bar progress-bar-striped progress-bar-animated bg-${barClass} fw-semibold" data-target="${riskPct}" style="width:0;">${riskPct}%</div>`;
      html += '</div>';
    } else {
      html += '<div class="alert alert-warning mb-3">Probability unavailable (model doesn\'t expose <code>predict_proba</code>).</div>';
    }

    if (confidencePct !== null && confidencePct !== undefined) {
      html += '<h5 class="mb-2">Model Confidence</h5>';
      html += `<div class="progress progress-hover mb-4" role="progressbar" aria-valuenow="${confidencePct}" aria-valuemin="0" aria-valuemax="100" data-bs-toggle="tooltip" title="Model is ${confidencePct}% confident in this prediction">`;
      html += `<div class="progress-bar progress-bar-striped progress-bar-animated bg-info fw-semibold" data-target="${confidencePct}" style="width:0;">${confidencePct}%</div>`;
      html += '</div>';
    }

    html += '<p class="small text-muted mb-0">Educational demo — not a medical diagnosis.</p>';

    prediction.innerHTML = html;

    // Animate progress bars to target width
    prediction.querySelectorAll('.progress-bar[data-target]').forEach(bar => {
      const target = bar.getAttribute('data-target');
      // Allow reflow then animate
      requestAnimationFrame(() => {
        setTimeout(() => { bar.style.width = `${target}%`; }, 150);
      });
    });

    // initialize tooltips inside the freshly rendered prediction block
    prediction.querySelectorAll('[data-bs-toggle="tooltip"]').forEach(el => {
      new bootstrap.Tooltip(el);
    });
  }

  function renderChart(res) {
    const data = res.results.exercise_angina;
    if (!data) return;
    const no = {x: data.no.map(r => r.value), y: data.no.map(r => r.risk_pct), mode:'lines', name:'No Angina', line:{color:'green'}};
    const yes = {x: data.yes.map(r => r.value), y: data.yes.map(r => r.risk_pct), mode:'lines', name:'Yes Angina', line:{color:'red'}};
    const cur = {x:[data.current.value], y:[data.current.risk_pct], mode:'markers+text', text:["You're here"], textposition:'top center', marker:{color:data.current.angina ? 'red':'green', size:8}, showlegend:false};
    Plotly.newPlot('exercise-angina-chart', [no, yes, cur], {xaxis:{title:data.label, range:[data.vmin, data.vmax]}, yaxis:{title:'Risk (%)', range:[0,100]}, margin:{t:30}});
  }

  function fetchSimulation(signal) {
    const formData = new FormData(form);
    if (variableSelect) {
      formData.append('variable', variableSelect.value);
    }
    return fetch('/simulations/run', {
      method: 'POST',
      body: formData,
      signal
    }).then(res => {
      if (!res.ok) throw new Error('Network');
      return res.json();
    });
  }

  function runSimulation() {
    if (controller) controller.abort();
    controller = new AbortController();
    const { signal } = controller;

    prediction.setAttribute('aria-busy', 'true');
    if (chart) chart.setAttribute('aria-busy', 'true');
    announcer.textContent = 'Updating simulation...';

    if (loaderVisible) hideLoader();
    clearTimeout(loaderTimer);
    loaderTimer = setTimeout(() => {
      showLoader();
    }, 120);

    fetchSimulation(signal)
      .then(res => {
        clearTimeout(loaderTimer);
        const finalize = () => {
          renderPrediction(res.prediction);
          renderChart(res);
          highlight();
          hideLoader();
          showUpdated();
          if (chart) chart.setAttribute('aria-busy', 'false');
        };
        if (loaderVisible) {
          const elapsed = Date.now() - loaderStart;
          const remaining = Math.max(200 - elapsed, 0);
          setTimeout(finalize, remaining);
        } else {
          finalize();
        }
      })
      .catch(err => {
        if (err.name === 'AbortError') return;
        clearTimeout(loaderTimer);
        hideLoader();
        prediction.setAttribute('aria-busy', 'false');
        if (chart) chart.setAttribute('aria-busy', 'false');
        announcer.textContent = 'Simulation update failed';
        showToast('Simulation update failed');
      });
  }

  runBtn.addEventListener('click', (e) => {
    e.preventDefault();
    initialized = true;
    runSimulation();
  });

  inputs.forEach(inp => {
    inp.addEventListener('input', () => {
      if (!initialized) return;
      if (debounceTimer) clearTimeout(debounceTimer);
      debounceTimer = setTimeout(() => {
        runSimulation();
      }, 300);
    });
  });

  const tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
  tooltipTriggerList.map(t => new bootstrap.Tooltip(t));
});

