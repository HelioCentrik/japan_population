// assets/map_resize.js
(function () {
    // Keep in sync with config.py MAP_REF_* / MAP_ZOOM_* constants.
    const REF_HEIGHT   = window.MAP_CONFIG.refHeight;
    const REF_ZOOM     = window.MAP_CONFIG.refZoom;
    const ZOOM_MIN     = window.MAP_CONFIG.zoomMin;
    const ZOOM_MAX     = window.MAP_CONFIG.zoomMax;
    const DEFAULT_ZOOM = window.MAP_CONFIG.defaultZoom;
    const CENTER_LAT   = window.MAP_CONFIG.centerLat;
    const CENTER_LON   = window.MAP_CONFIG.centerLon;

    function getPlotlyDiv() {
        return document.querySelector('#map-graph .js-plotly-plot');
    }

    let revealed = false;

    function reveal() {
        if (revealed) return;
        revealed = true;
        const inner = document.querySelector('.map-inner');
        if (inner) inner.style.opacity = '1';
    }

    // Use Plotly.relayout (not mbMap.setZoom) so _fullLayout.map.zoom stays in sync.
    // uirevision-based Plotly.react reads _fullLayout to restore the viewport; calling
    // mbMap.setZoom directly leaves that value stale and causes filters to revert the zoom.
    function applyResizeZoom(plotDiv, height) {
        const target = Math.min(ZOOM_MAX, Math.max(ZOOM_MIN,
            REF_ZOOM + Math.log2(height / REF_HEIGHT)));
        const current = plotDiv._fullLayout?.map?.zoom ?? DEFAULT_ZOOM;
        if (Math.abs(current - target) >= 0.05) {
            Plotly.relayout(plotDiv, {'map.zoom': target});
        }
    }

    function attach() {
        const panel   = document.querySelector('.map-panel');
        const plotDiv = getPlotlyDiv();
        if (!panel || !plotDiv) return false;

        // Reveal once the initial-zoom Patch has landed (layout zoom rises above the
        // figure default). Does not attempt its own correction before that point.
        plotDiv.on('plotly_afterplot', function () {
            if (revealed) return;
            const layoutZoom = plotDiv._fullLayout?.map?.zoom ?? DEFAULT_ZOOM;
            if (layoutZoom > DEFAULT_ZOOM + 0.1) {
                reveal();
            }
        });

        // Fallback: reveal anyway if the Patch never lands.
        setTimeout(reveal, 3000);

        // On window resize: first tell Plotly about the new container size, then
        // set the correct zoom through Plotly so _fullLayout stays authoritative.
        let _resizeTimer = null;
        window.addEventListener('resize', function () {
            if (!revealed) return;
            clearTimeout(_resizeTimer);
            _resizeTimer = setTimeout(function () {
                const pDiv = getPlotlyDiv();
                if (!pDiv || !panel) return;
                Plotly.Plots.resize(pDiv).then(function () {
                    applyResizeZoom(pDiv, panel.getBoundingClientRect().height);
                });
            }, 150);
        });

        return true;
    }

    const interval = setInterval(() => {
        if (attach()) clearInterval(interval);
    }, 200);

    // Exposed for the ⤢ button clientside callback.
    // Recomputes zoom from current panel height and applies via Plotly.relayout.
    window.refitMap = function () {
        const panel   = document.querySelector('.map-panel');
        const plotDiv = getPlotlyDiv();
        if (!panel || !plotDiv) return window.dash_clientside.no_update;
        const height = panel.getBoundingClientRect().height;
        const zoom   = Math.min(ZOOM_MAX, Math.max(ZOOM_MIN,
            REF_ZOOM + Math.log2(height / REF_HEIGHT)));
        Plotly.relayout(plotDiv, {
            'map.zoom':       zoom,
            'map.center.lat': CENTER_LAT,
            'map.center.lon': CENTER_LON,
        });
        return window.dash_clientside.no_update;
    };
})();
