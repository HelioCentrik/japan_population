// assets/map_resize.js
(function () {
    const REF_HEIGHT = 582;
    const REF_ZOOM   = 3.75;
    const ZOOM_MIN   = 2.5;
    const ZOOM_MAX   = 5.5;

    // _targetZoom: formula-computed zoom for the current panel height.
    // JS is the single authority on zoom — Dash figures carry a default that
    // is only used before this module fires.
    let _targetZoom = null;
    let _busy       = false; // reentrancy guard — prevents relayout loops

    function computeZoom(height) {
        return Math.min(ZOOM_MAX, Math.max(ZOOM_MIN,
            REF_ZOOM + Math.log2(height / REF_HEIGHT)));
    }

    function getPlotlyDiv() {
        return document.querySelector('#map-graph .js-plotly-plot');
    }

    function currentZoom(plotDiv) {
        try { return plotDiv._fullLayout.mapbox.zoom; }
        catch (_) { return null; }
    }

    function applyZoom(plotDiv) {
        if (_busy || _targetZoom === null) return;
        const cur = currentZoom(plotDiv);
        // Skip if zoom already matches — avoids redundant relayouts
        if (cur !== null && Math.abs(cur - _targetZoom) < 0.001) return;
        _busy = true;
        Plotly.relayout(plotDiv, { 'mapbox.zoom': _targetZoom })
            .then(() => {
                _busy = false;
                // A Dash figure update may have landed while we were busy
                // (its plotly_afterplot was suppressed by the guard).
                // Check one more time to catch that case.
                applyZoom(plotDiv);
            });
    }

    function attach() {
        const panel   = document.querySelector('.map-panel');
        const plotDiv = getPlotlyDiv();
        if (!panel || !plotDiv) return false;

        // Recompute and apply zoom whenever the panel resizes
        new ResizeObserver(entries => {
            for (const entry of entries) {
                _targetZoom = computeZoom(entry.contentRect.height);
                applyZoom(plotDiv);
            }
        }).observe(panel);

        // Re-impose zoom after every Plotly operation.  Dash year/metric
        // changes return a full figure that resets mapbox.zoom to the baked-in
        // default; uirevision only reliably preserves user-gesture state, not
        // state set via Plotly.relayout.  This listener is the safety net.
        plotDiv.on('plotly_afterplot', () => applyZoom(plotDiv));

        return true;
    }

    const interval = setInterval(() => {
        if (attach()) clearInterval(interval);
    }, 200);
})();
