document.addEventListener('DOMContentLoaded', () => {
  const runBtn = document.getElementById('run-sim');
  const form = document.getElementById('sim-form');
  const variableSelect = document.getElementById('variable');
  const inputs = [...form.querySelectorAll('input, select')];
  if (variableSelect) {
    inputs.push(variableSelect);
  }
  let initialized = false;

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

  function fetchSimulation() {
    const formData = new FormData(form);
    if (variableSelect) {
      formData.append('variable', variableSelect.value);
    }
    return fetch('/simulations/run', {
      method: 'POST',
      body: formData
    }).then(res => res.json());
  }

  function renderPrediction(pred) {
    const container = document.getElementById('prediction');
    if (!pred) {
      container.innerHTML = '';
      return;
    }
    let html = `<h2>Prediction Result</h2><p><strong>${pred.label}</strong></p>`;
    if (pred.risk_pct !== null) {
      html += `<div class="progress mb-2" role="progressbar" aria-valuemin="0" aria-valuemax="100" aria-valuenow="${pred.risk_pct}"><div class="progress-bar bg-info" style="width:${pred.risk_pct}%">${pred.risk_pct}%</div></div>`;
    }
    if (pred.confidence_pct !== null) {
      html += `<p class="mb-0">Model confidence: ${pred.confidence_pct}%</p>`;
    }
    container.innerHTML = html;
  }

  function renderChart(res) {
    const data = res.results.exercise_angina;
    if (!data) {
      return;
    }
    const no = {x: data.no.map(r => r.value), y: data.no.map(r => r.risk_pct), mode:'lines', name:'No Angina', line:{color:'green'}};
    const yes = {x: data.yes.map(r => r.value), y: data.yes.map(r => r.risk_pct), mode:'lines', name:'Yes Angina', line:{color:'red'}};
    const cur = {x:[data.current.value], y:[data.current.risk_pct], mode:'markers+text', text:["You're here"], textposition:'top center', marker:{color:data.current.angina ? 'red':'green', size:8}, showlegend:false};
    Plotly.newPlot('exercise-angina-chart', [no, yes, cur], {xaxis:{title:data.label, range:[data.vmin, data.vmax]}, yaxis:{title:'Risk (%)', range:[0,100]}, margin:{t:30}});
  }

  function runSimulation() {
    fetchSimulation().then(res => {
      renderPrediction(res.prediction);
      renderChart(res);
    });
  }

  runBtn.addEventListener('click', (e) => {
    e.preventDefault();
    initialized = true;
    runSimulation();
  });

  inputs.forEach(inp => {
    inp.addEventListener('input', () => {
      if (initialized) {
        runSimulation();
      }
    });
  });

  const tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
  tooltipTriggerList.map(t => new bootstrap.Tooltip(t));
});

