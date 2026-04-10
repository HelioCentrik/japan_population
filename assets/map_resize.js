// assets/map_resize.js
(function () {
    // Keep in sync with config.py MAP_REF_* / MAP_ZOOM_* constants.
    const REF_HEIGHT   = 582;
    const REF_ZOOM     = 3.75;
    const ZOOM_MIN     = 2.5;
    const ZOOM_MAX     = 5.5;
    const DEFAULT_ZOOM = 2.5;   // zoom baked into cached figures; Patch raises this on load

    function getPlotlyDiv() {
        return document.querySelector('#map-graph .js-plotly-plot');
    }

    function getMbMap(plotDiv) {
        return plotDiv?._fullLayout?.mapbox?._subplot?.map;
    }

    let revealed = false;

    function reveal() {
        if (revealed) return;
        revealed = true;
        const inner = document.querySelector('.map-inner');
        if (inner) inner.style.opacity = '1';
    }

function applyResizeZoom(height) {
    const plotDiv = getPlotlyDiv();
    const mbMap   = getMbMap(plotDiv);
    if (!mbMap) return;
    const target = Math.min(ZOOM_MAX, Math.max(ZOOM_MIN,
        REF_ZOOM + Math.log2(height / REF_HEIGHT)));
    if (Math.abs(mbMap.getZoom() - target) >= 0.05) {
        mbMap.setZoom(target);
    }
}

    function attach() {
        const panel   = document.querySelector('.map-panel');
        const plotDiv = getPlotlyDiv();
        if (!panel || !plotDiv) return false;

        // Reveal once the server Patch has landed — detected by layout zoom rising
        // above the figure default. Does NOT attempt its own zoom correction before
        // that point; the Patch handles initial zoom, uirevision preserves it after.
        plotDiv.on('plotly_afterplot', function () {
            if (revealed) return;
            const layoutZoom = plotDiv._fullLayout?.mapbox?.zoom ?? DEFAULT_ZOOM;
            if (layoutZoom > DEFAULT_ZOOM + 0.1) {
                reveal();
            }
        });

        // Fallback: if Patch never lands (e.g. clientside callback failure), reveal anyway.
        setTimeout(reveal, 3000);

        // Subsequent window resizes — nudge MB GL zoom after the map is already visible.
        let _resizeTimer = null;
        window.addEventListener('resize', function () {
            if (!revealed) return;
            clearTimeout(_resizeTimer);
            _resizeTimer = setTimeout(function () {
                const pDiv = getPlotlyDiv();
                if (!pDiv || !panel) return;
                Plotly.Plots.resize(pDiv).then(function () {
                    applyResizeZoom(panel.getBoundingClientRect().height);
                });
            }, 150);   // 150ms debounce — enough for layout to settle after maximize
        });

        return true;
    }

    const interval = setInterval(() => {
        if (attach()) clearInterval(interval);
    }, 200);
})();