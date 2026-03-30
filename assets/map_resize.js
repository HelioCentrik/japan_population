// assets/map_resize.js
// Dynamically adjusts Mapbox zoom as the map panel resizes.
// Reference point: 582px panel height → zoom 3.75 (calibrated visually).
(function () {
    const REF_HEIGHT = 582;
    const REF_ZOOM   = 3.75;
    const ZOOM_MIN   = 2.5;
    const ZOOM_MAX   = 5.5;

    function getPlotlyDiv() {
        // dcc.Graph wraps a .js-plotly-plot — that's the element Plotly.relayout expects
        return document.querySelector('#choropleth-map .js-plotly-plot');
    }

    function updateZoom(height) {
        const plotDiv = getPlotlyDiv();
        if (!plotDiv) return;
        const zoom = Math.min(ZOOM_MAX, Math.max(ZOOM_MIN, REF_ZOOM + Math.log2(height / REF_HEIGHT)));
        Plotly.relayout(plotDiv, { 'mapbox.zoom': zoom });
    }

    function attach() {
        const panel = document.querySelector('.map-panel');
        if (!panel) return false;
        new ResizeObserver(entries => {
            for (const entry of entries) {
                updateZoom(entry.contentRect.height);
            }
        }).observe(panel);
        return true;
    }

    // Dash renders async — poll until the panel exists
    const interval = setInterval(() => {
        if (attach()) clearInterval(interval);
    }, 200);
})();