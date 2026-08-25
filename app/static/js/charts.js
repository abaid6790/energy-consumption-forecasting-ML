// Shared Plotly rendering helpers used across dashboard/forecast/analytics/anomalies pages.

const PLOTLY_LAYOUT_BASE = {
    margin: { t: 10, r: 20, b: 40, l: 50 },
    paper_bgcolor: 'rgba(0,0,0,0)',
    plot_bgcolor: 'rgba(0,0,0,0)',
    font: { family: 'Inter, sans-serif', color: '#0F172A', size: 12 },
    xaxis: { gridcolor: '#E2E8F0', showgrid: true },
    yaxis: { gridcolor: '#E2E8F0', showgrid: true },
    legend: { orientation: 'h', y: -0.2 },
};

function renderLineChart(elementId, series, yTitle) {
    const traces = series.map(s => ({
        x: s.x,
        y: s.y,
        type: 'scatter',
        mode: s.mode || 'lines',
        name: s.name,
        line: { color: s.color, width: 2, dash: s.dash || 'solid' },
        fill: s.fill,
        fillcolor: s.fillcolor,
    }));
    const layout = Object.assign({}, PLOTLY_LAYOUT_BASE, {
        yaxis: Object.assign({}, PLOTLY_LAYOUT_BASE.yaxis, { title: yTitle }),
    });
    Plotly.newPlot(elementId, traces, layout, { responsive: true, displayModeBar: false });
}

function renderBarChart(elementId, x, y, yTitle, color) {
    const trace = {
        x: x,
        y: y,
        type: 'bar',
        marker: { color: color || '#2563EB' },
    };
    const layout = Object.assign({}, PLOTLY_LAYOUT_BASE, {
        yaxis: Object.assign({}, PLOTLY_LAYOUT_BASE.yaxis, { title: yTitle }),
    });
    Plotly.newPlot(elementId, [trace], layout, { responsive: true, displayModeBar: false });
}

function renderForecastChart(elementId, historyX, historyY, forecastX, forecastY, lowerY, upperY, unit) {
    const traces = [
        {
            x: historyX, y: historyY, type: 'scatter', mode: 'lines',
            name: 'Historical', line: { color: '#0F172A', width: 2 }
        },
        {
            x: forecastX, y: forecastY, type: 'scatter', mode: 'lines+markers',
            name: 'Forecast', line: { color: '#2563EB', width: 2, dash: 'dash' }
        }
    ];
    if (lowerY && upperY) {
        traces.push({
            x: forecastX.concat([...forecastX].reverse()),
            y: upperY.concat([...lowerY].reverse()),
            fill: 'toself',
            fillcolor: 'rgba(37,99,235,0.12)',
            line: { color: 'transparent' },
            name: 'Confidence Interval',
            showlegend: true,
            type: 'scatter'
        });
    }
    const layout = Object.assign({}, PLOTLY_LAYOUT_BASE, {
        yaxis: Object.assign({}, PLOTLY_LAYOUT_BASE.yaxis, { title: `Energy Consumption (${unit || 'kW'})` }),
    });
    Plotly.newPlot(elementId, traces, layout, { responsive: true, displayModeBar: false });
}

function renderAnomalyChart(elementId, points) {
    const normal = points.filter(p => !p.is_anomaly);
    const anomalies = points.filter(p => p.is_anomaly);
    const traces = [
        {
            x: points.map(p => p.timestamp), y: points.map(p => p.value),
            type: 'scatter', mode: 'lines', name: 'Consumption',
            line: { color: '#0F172A', width: 1.5 }
        },
        {
            x: anomalies.map(p => p.timestamp), y: anomalies.map(p => p.value),
            type: 'scatter', mode: 'markers', name: 'Anomaly',
            marker: { color: '#DC2626', size: 9, symbol: 'x' }
        }
    ];
    Plotly.newPlot(elementId, traces, PLOTLY_LAYOUT_BASE, { responsive: true, displayModeBar: false });
}
