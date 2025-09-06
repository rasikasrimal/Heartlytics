(function(){
  function plotlyTheme(layout){
    const root = document.documentElement;
    const theme = root.getAttribute('data-bs-theme');
    const styles = getComputedStyle(root);
    const bodyColor = styles.getPropertyValue('--bs-body-color').trim();
    const bodyBg = styles.getPropertyValue('--bs-body-bg').trim();
    const border = styles.getPropertyValue('--border-subtle').trim() || styles.getPropertyValue('--bs-border-color').trim();
    layout = Object.assign({
      font: {family: 'Inter, sans-serif', color: bodyColor},
      colorway: ['#dc2626', '#1e3a8a', '#f97316', '#0ea5e9', '#6366f1']
    }, layout || {});
    if (theme === 'dark'){
      layout.paper_bgcolor = 'rgba(0,0,0,0)';
      layout.plot_bgcolor = 'rgba(0,0,0,0)';
    } else {
      layout.paper_bgcolor = bodyBg;
      layout.plot_bgcolor = bodyBg;
    }
    if (layout.xaxis){
      layout.xaxis.color = bodyColor;
      layout.xaxis.gridcolor = border;
    }
    if (layout.yaxis){
      layout.yaxis.color = bodyColor;
      layout.yaxis.gridcolor = border;
    }
    return layout;
  }

  function patchPlotly(){
    if (!window.Plotly) return;
    const orig = Plotly.newPlot;
    Plotly.newPlot = function(id, data, layout, config){
      layout = plotlyTheme(layout);
      config = Object.assign({responsive: true, displayModeBar: false}, config || {});
      return orig(id, data, layout, config);
    };
    window.addEventListener('themechange', () => {
      document.querySelectorAll('.js-plotly-plot').forEach(el => {
        const update = plotlyTheme({});
        Plotly.relayout(el, update);
      });
    });
  }

  function chartJsTheme(){
    if (!window.Chart) return;
    function apply(){
      const root = document.documentElement;
      const styles = getComputedStyle(root);
      const color = styles.getPropertyValue('--bs-body-color').trim();
      const border = styles.getPropertyValue('--border-subtle').trim() || styles.getPropertyValue('--bs-border-color').trim();
      Chart.defaults.color = color;
      Chart.defaults.backgroundColor = 'transparent';
      if (Chart.defaults.scales){
        for (const s of Object.values(Chart.defaults.scales)){
          s.grid = Object.assign({color: border}, s.grid || {});
        }
      }
      if (Chart.defaults.plugins && Chart.defaults.plugins.legend){
        Chart.defaults.plugins.legend.labels.color = color;
      }
    }
    apply();
    window.addEventListener('themechange', apply);
  }

  function init(){
    patchPlotly();
    chartJsTheme();
  }
  if (document.readyState !== 'loading') init();
  else document.addEventListener('DOMContentLoaded', init);
})();
