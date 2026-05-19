// assets/map_resize.js
(function () {
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

    let revealed        = false;
    let lastPanelHeight = 0;    // ← track height so afterplot only fires on real resize

    function reveal() {
        if (revealed) return;
        revealed = true;
        const inner = document.querySelector('.map-inner');
        if (inner) inner.style.opacity = '1';
    }

    // Plotly.relayout with map layout props triggers fillBelowLookup internally,
    // which reads MapLibre GL's style.layers. That object is undefined if the GL
    // style hasn't finished loading — which is async and not guaranteed by the
    // time _fullLayout.map exists. Retry with backoff instead of depending on
    // Plotly internals to detect GL readiness.
    function safeRelayout(plotDiv, update, attempt) {
        attempt = attempt || 0;
        if (attempt > 4) return;
        try {
            Plotly.relayout(plotDiv, update);
        } catch (e) {
            const delay = 100 * Math.pow(2, attempt);
            setTimeout(function () { safeRelayout(plotDiv, update, attempt + 1); }, delay);
        }
    }

    function applyResizeZoom(plotDiv, height) {
        const target = Math.min(ZOOM_MAX, Math.max(ZOOM_MIN,
            REF_ZOOM + Math.log2(height / REF_HEIGHT)));
        const current = plotDiv._fullLayout?.map?.zoom ?? DEFAULT_ZOOM;
        if (Math.abs(current - target) >= 0.05) {
            safeRelayout(plotDiv, {'map.zoom': target});
        }
    }

    function attach() {
        const panel   = document.querySelector('.map-panel');
        const plotDiv = getPlotlyDiv();
        if (!panel || !plotDiv) return false;
        if (!plotDiv._fullLayout?.map) return false;

        let zoomApplied = false;
        let _catchUpTimer = null;

        // Capture baseline height at attach time so afterplot comparisons are valid.
        lastPanelHeight = panel.getBoundingClientRect().height;

        plotDiv.on('plotly_afterplot', function () {
            clearTimeout(_catchUpTimer);
            const hasData = plotDiv.data && plotDiv.data.length > 0;
            if (revealed) {
                // Only re-zoom if the panel actually changed size.
                // afterplot fires on every data update (year change, metric switch,
                // prefecture click) — without this guard we'd reset zoom on each one.
                const h = panel.getBoundingClientRect().height;
                if (Math.abs(h - lastPanelHeight) > 2) {
                    lastPanelHeight = h;
                    applyResizeZoom(plotDiv, h);
                }
                return;
            }
            if (!plotDiv._fullLayout?.map) return;
            if (!hasData) return;
            if (!zoomApplied) {
                zoomApplied = true;
                setTimeout(function () { window.refitMap(); }, 0);
            } else {
                reveal();
            }
        });

        if (plotDiv.data && plotDiv.data.length > 0 && !zoomApplied) {
            _catchUpTimer = setTimeout(function () {
                if (!zoomApplied && !revealed) {
                    zoomApplied = true;
                    window.refitMap();
                }
            }, 300);
        }

        setTimeout(reveal, 3000);

        let _resizeTimer = null;
        window.addEventListener('resize', function () {
            if (!revealed) return;
            clearTimeout(_resizeTimer);
            _resizeTimer = setTimeout(function () {
                const pDiv = getPlotlyDiv();
                if (!pDiv || !panel) return;
                Plotly.Plots.resize(pDiv).then(function () {
                    const h = panel.getBoundingClientRect().height;
                    lastPanelHeight = h;    // ← keep in sync after window resize too
                    applyResizeZoom(pDiv, h);
                });
            }, 150);
        });

        return true;
    }

    const interval = setInterval(() => {
        if (attach()) clearInterval(interval);
    }, 200);

    // Exposed for the ⤢ button clientside callback.
    window.refitMap = function () {
        const panel   = document.querySelector('.map-panel');
        const plotDiv = getPlotlyDiv();
        if (!panel || !plotDiv) return window.dash_clientside.no_update;
        const h    = panel.getBoundingClientRect().height;
        const zoom = Math.min(ZOOM_MAX, Math.max(ZOOM_MIN,
            REF_ZOOM + Math.log2(h / REF_HEIGHT)));
        lastPanelHeight = h;    // ← keep in sync when button forces a refit
        safeRelayout(plotDiv, {
            'map.zoom':       zoom,
            'map.center.lat': CENTER_LAT,
            'map.center.lon': CENTER_LON,
        });
        return window.dash_clientside.no_update;
    };
})();