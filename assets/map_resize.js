// assets/map_resize.js
(function () {
    const REF_HEIGHT = 582;
    const REF_ZOOM   = 3.75;
    const ZOOM_MIN   = 2.5;
    const ZOOM_MAX   = 5.5;

    function getPlotlyDiv() {
        return document.querySelector('#map-graph .js-plotly-plot');  // was #choropleth-map
    }

    function updateZoom(height) {
        const plotDiv = getPlotlyDiv();
        if (!plotDiv) return;
        const zoom = Math.min(ZOOM_MAX, Math.max(ZOOM_MIN, REF_ZOOM + Math.log2(height / REF_HEIGHT)));
        Plotly.relayout(plotDiv, { 'mapbox.zoom': zoom });
    }

    function attach() {
        const panel   = document.querySelector('.map-panel');
        const plotDiv = getPlotlyDiv();
        if (!panel || !plotDiv) return false;   // wait for both before attaching

        new ResizeObserver(entries => {
            for (const entry of entries) {
                updateZoom(entry.contentRect.height);
            }
        }).observe(panel);

        return true;
    }

    const interval = setInterval(() => {
        if (attach()) clearInterval(interval);
    }, 200);
})();