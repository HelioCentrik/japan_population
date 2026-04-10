// assets/map_resize.js
// Sole authority on map zoom.
//
// Zoom is computed from panel height using a log2 scale anchored at REF_HEIGHT
// → REF_ZOOM.  It is applied via Plotly.relayout when the panel first mounts
// and whenever it resizes (window resize, layout reflow, etc.).
//
// Filter changes (year, metric, prefecture) use Dash Patch() in app.py and
// never include layout in their payload, so mapbox.zoom is never overwritten
// by a callback.  No plotly_afterplot listener is needed.
(function () {
    const REF_HEIGHT = 582;
    const REF_ZOOM   = 3.75;
    const ZOOM_MIN   = 2.5;
    const ZOOM_MAX   = 5.5;

    function computeZoom(height) {
        return Math.min(ZOOM_MAX, Math.max(ZOOM_MIN,
            REF_ZOOM + Math.log2(height / REF_HEIGHT)));
    }

    function attach() {
        const panel   = document.querySelector('.map-panel');
        const plotDiv = document.querySelector('#map-graph .js-plotly-plot');
        if (!panel || !plotDiv) return false;

        new ResizeObserver(entries => {
            for (const entry of entries) {
                Plotly.relayout(plotDiv, {
                    'mapbox.zoom': computeZoom(entry.contentRect.height)
                });
            }
        }).observe(panel);

        return true;
    }

    const interval = setInterval(() => {
        if (attach()) clearInterval(interval);
    }, 200);
})();
