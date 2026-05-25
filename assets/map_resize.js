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
    let lastPanelHeight = 0;

    function reveal() {
        if (revealed) return;
        revealed = true;
        const inner = document.querySelector('.map-inner');
        if (inner) inner.style.opacity = '1';
        resizeCharts();
    }

    // Plotly.relayout with map layout props triggers fillBelowLookup internally,
    // which reads MapLibre GL's style.layers. That object is undefined if the GL
    // style hasn't finished loading — which is async and not guaranteed by the
    // time _fullLayout.map exists. Retry with backoff instead of depending on
    // Plotly internals to detect GL readiness.
    function safeRelayout(plotDiv, update, attempt) {
        attempt = attempt || 0;
        if (attempt > 4) {
            console.warn('[map_resize] safeRelayout gave up after 5 attempts');
            return;
        }
        try {
            Plotly.relayout(plotDiv, update);
        } catch (e) {
            const delay = 100 * Math.pow(2, attempt);
            setTimeout(function () { safeRelayout(plotDiv, update, attempt + 1); }, delay);
        }
    }

    function applyResizeZoom(plotDiv, height) {
        const target  = Math.min(ZOOM_MAX, Math.max(ZOOM_MIN,
            REF_ZOOM + Math.log2(height / REF_HEIGHT)));
        const current = plotDiv._fullLayout?.map?.zoom ?? DEFAULT_ZOOM;
        if (Math.abs(current - target) >= 0.05) {
            safeRelayout(plotDiv, {'map.zoom': target});
        }
    }

    // getBoundingClientRect() returns zoomed viewport coords when CSS zoom is on
    // .dashboard-outer. Divide by the zoom factor to recover the logical height
    // that the map zoom formula expects.
    function logicalHeight(panel) {
        const outer = document.querySelector('.dashboard-outer');
        const zoom  = parseFloat(outer && outer.style.zoom) || 1;
        return panel.getBoundingClientRect().height / zoom;
    }

    function resizeCharts() {
        ['#pyramid-chart .js-plotly-plot', '#timeseries-chart .js-plotly-plot'].forEach(function (sel) {
            const el = document.querySelector(sel);
            if (el) Plotly.Plots.resize(el);
        });
    }

    function attach() {
        const panel   = document.querySelector('.map-panel');
        const plotDiv = getPlotlyDiv();
        if (!panel || !plotDiv) return false;
        if (!plotDiv._fullLayout?.map) return false;

        let zoomApplied   = false;
        let _catchUpTimer = null;

        lastPanelHeight = logicalHeight(panel);

        plotDiv.on('plotly_afterplot', function () {
            clearTimeout(_catchUpTimer);
            const hasData = plotDiv.data && plotDiv.data.length > 0;
            if (revealed) {
                // Only re-zoom on genuine panel resize — afterplot fires on every
                // data update (year change, metric switch, prefecture click).
                const h = logicalHeight(panel);
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
                // Belt-and-suspenders: Plotly can fire an internal re-render after
                // our relayout that resets the viewport. Re-apply zoom 250ms post-reveal
                // to correct it. applyResizeZoom's tolerance guard makes this a no-op
                // if zoom is already correct, so no visible flash.
                setTimeout(window.refitMap, 250);
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

        // Fallback reveal in case the second afterplot never fires.
        // Also calls refitMap so the viewport is correct even via this path.
        setTimeout(function () {
            if (!revealed) {
                reveal();
                window.refitMap();
            }
        }, 3000);

        let _resizeTimer = null;
        window.addEventListener('resize', function () {
            if (!revealed) return;
            clearTimeout(_resizeTimer);
            _resizeTimer = setTimeout(function () {
                const pDiv = getPlotlyDiv();
                if (!pDiv || !panel) return;
                Plotly.Plots.resize(pDiv).then(function () {
                    const h = logicalHeight(panel);
                    lastPanelHeight = h;
                    applyResizeZoom(pDiv, h);
                    resizeCharts();
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
        const h    = logicalHeight(panel);
        const zoom = Math.min(ZOOM_MAX, Math.max(ZOOM_MIN,
            REF_ZOOM + Math.log2(h / REF_HEIGHT)));
        lastPanelHeight = h;
        safeRelayout(plotDiv, {
            'map.zoom':       zoom,
            'map.center.lat': CENTER_LAT,
            'map.center.lon': CENTER_LON,
        });
        resizeCharts();
        return window.dash_clientside.no_update;
    };
})();