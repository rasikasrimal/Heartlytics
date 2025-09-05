async function fetchAndPlot(url, canvasId) {
  try {
    const res = await fetch(url);
    if (!res.ok) throw new Error(res.statusText);
    const data = await res.json();
    const ctx = document.getElementById(canvasId);
    if (!ctx) return;
    let labels = [];
    let values = [];
    if (data.points) {
      labels = data.points.map(p => p.label);
      values = data.points.map(p => p.value);
    } else if (data.ages && data.risks) {
      labels = data.ages;
      values = data.risks;
    } else if (data.before !== undefined && data.after !== undefined) {
      labels = ['Before', 'After'];
      values = [data.before, data.after];
    }
    new Chart(ctx, {
      type: 'line',
      data: {labels: labels, datasets: [{label: 'Risk %', data: values}]},
      options: {responsive: true}
    });
  } catch (err) {
    console.error('Simulation module failed:', url, err);
  }
}

document.addEventListener('DOMContentLoaded', () => {
  fetchAndPlot('/simulations/what-if/api', 'whatIfChart');
  fetchAndPlot('/simulations/age-projection/api', 'ageProjectionChart');
  fetchAndPlot('/simulations/lifestyle-impact/api', 'lifestyleImpactChart');
});
