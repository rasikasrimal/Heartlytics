(function(){
  function currentTheme(){
    return document.documentElement.getAttribute('data-bs-theme');
  }

  function buildLayout(layout){
    const root = document.documentElement;
    const styles = getComputedStyle(root);
    const theme = currentTheme();
    const bodyColor = styles.getPropertyValue('--bs-body-color').trim();
    const bodyBg = styles.getPropertyValue('--bs-body-bg').trim();
    const grid = styles.getPropertyValue('--grid-subtle').trim();
    const result = Object.assign({}, layout);
    result.font = Object.assign({family: 'Inter, system-ui, sans-serif', color: bodyColor}, result.font);
    // Always render charts with transparent backgrounds so they blend
    // with cards in both light and dark themes.
    result.paper_bgcolor = 'rgba(0,0,0,0)';
    result.plot_bgcolor = 'rgba(0,0,0,0)';
    result.hoverlabel = Object.assign({}, result.hoverlabel,
      theme === 'dark'
        ? {bgcolor: 'rgba(0,0,0,0.6)', font: {color: '#fff'}}
        : {bgcolor: bodyBg, font: {color: bodyColor}}
    );
    ['xaxis','yaxis','xaxis2','yaxis2','xaxis3','yaxis3'].forEach(ax => {
      result[ax] = Object.assign({}, result[ax], {color: bodyColor, gridcolor: grid});
    });
    if (result.coloraxis){
      result.coloraxis = Object.assign({}, result.coloraxis, {
        colorbar: Object.assign({}, (result.coloraxis || {}).colorbar, {tickfont: {color: bodyColor}})
      });
    }
    if (result.annotations){
      result.annotations = result.annotations.map(a => Object.assign({}, a, {
        font: Object.assign({}, a.font, {color: theme === 'dark' ? '#fff' : bodyColor})
      }));
    }
    return result;
  }

  function patchPlotly(){
    if (!window.Plotly) return;
    const origNew = Plotly.newPlot;
    const origReact = Plotly.react ? Plotly.react.bind(Plotly) : null;

    function patchDataForTheme(data){
      const theme = currentTheme();
      const patchedData = Array.isArray(data) ? data.map(tr => {
        const t = Object.assign({}, tr);
        if (t.type === 'heatmap') {
          t.colorscale = theme === 'dark' ? 'Viridis' : 'RdBu';
        }
        return t;
      }) : data;
      return patchedData;
    }

    Plotly.newPlot = function(id, data, layout, config){
      const patchedLayout = buildLayout(layout || {});
      const cfg = Object.assign({responsive: true, displayModeBar: false}, config || {});
      return origNew(id, patchDataForTheme(data), patchedLayout, cfg);
    };

    if (origReact) {
      Plotly.react = function(id, data, layout, config){
        const patchedLayout = buildLayout(layout || {});
        const cfg = Object.assign({responsive: true, displayModeBar: false}, config || {});
        return origReact(id, patchDataForTheme(data), patchedLayout, cfg);
      }
    }

    window.addEventListener('themechange', () => {
      document.querySelectorAll('.js-plotly-plot').forEach(el => {
        const updLayout = buildLayout(el.layout || {});
        Plotly.relayout(el, updLayout);
        if (el.data) {
          const heatIdx = [];
          el.data.forEach((t, i) => { if (t.type === 'heatmap') heatIdx.push(i); });
          if (heatIdx.length) {
            const scale = currentTheme() === 'dark' ? 'Viridis' : 'RdBu';
            Plotly.restyle(el, {colorscale: scale}, heatIdx);
            if (el.layout.annotations) {
              const styles = getComputedStyle(document.documentElement);
              const color = styles.getPropertyValue('--bs-body-color').trim();
              el.layout.annotations.forEach(a => {
                if (!a.font) a.font = {};
                a.font.color = currentTheme() === 'dark' ? '#fff' : color;
              });
              Plotly.relayout(el, {annotations: el.layout.annotations});
            }
          }
        }
      });
    });
  }

  function chartJsTheme(){
    if (!window.Chart) return;
    function apply(){
      const root = document.documentElement;
      const styles = getComputedStyle(root);
      const theme = currentTheme();
      const color = styles.getPropertyValue('--bs-body-color').trim();
      const grid = styles.getPropertyValue('--grid-subtle').trim();
      Chart.defaults.color = color;
      Chart.defaults.borderColor = grid;
      Chart.defaults.backgroundColor = 'transparent';
      if (Chart.defaults.scales) {
        for (const s of Object.values(Chart.defaults.scales)) {
          s.grid = Object.assign({color: grid}, s.grid || {});
        }
      }
      if (Chart.defaults.plugins && Chart.defaults.plugins.legend) {
        Chart.defaults.plugins.legend.labels.color = color;
      }
      if (Chart.defaults.plugins && Chart.defaults.plugins.tooltip) {
        Chart.defaults.plugins.tooltip.backgroundColor = theme === 'dark' ? 'rgba(0,0,0,0.6)' : 'rgba(255,255,255,0.9)';
        Chart.defaults.plugins.tooltip.titleColor = theme === 'dark' ? '#fff' : '#000';
        Chart.defaults.plugins.tooltip.bodyColor = theme === 'dark' ? '#fff' : '#000';
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
