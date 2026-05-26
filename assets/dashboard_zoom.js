// assets/dashboard_zoom.js
(function () {
    if (!window.DASHBOARD_CONFIG) {
        console.warn('[dashboard_zoom] DASHBOARD_CONFIG not found');
        return;
    }

    const DESIGN_W = window.DASHBOARD_CONFIG.w;
    const DESIGN_H = window.DASHBOARD_CONFIG.h;

    let _lastZ = null;
    let _settleRaf = null;

    window.__dashboardZoomDebug = window.__dashboardZoomDebug || {};
    window.__dashboardZoomSettled = false;
    window.__dashboardZoomValue = null;

    const CHART_SELECTORS = ['#map-graph', '#pyramid-chart', '#timeseries-chart'];

    function snapshotChartZooms() {
        return Object.fromEntries(
            CHART_SELECTORS.map(function (sel) {
                const el = document.querySelector(sel);
                return [sel, el ? {
                    inlineZoom: el.style.zoom || null,
                    computedZoom: getComputedStyle(el).zoom,
                    rect: el.getBoundingClientRect().toJSON
                        ? el.getBoundingClientRect().toJSON()
                        : {
                            left: el.getBoundingClientRect().left,
                            top: el.getBoundingClientRect().top,
                            width: el.getBoundingClientRect().width,
                            height: el.getBoundingClientRect().height,
                        }
                } : null];
            })
        );
    }

    function emitZoomSettled() {
        if (_lastZ === null) return;

        window.__dashboardZoomSettled = true;
        window.__dashboardZoomValue = _lastZ;

        window.dispatchEvent(new CustomEvent('dashboard:zoom-settled', {
            detail: {
                zoom: _lastZ,
                counterZoom: 1 / _lastZ,
            },
        }));
    }

    function scheduleZoomSettled() {
        if (_settleRaf) cancelAnimationFrame(_settleRaf);

        // Two RAFs lets the browser apply outer zoom + chart counter-zoom
        // before downstream code measures Plotly/chart rects.
        _settleRaf = requestAnimationFrame(function () {
            _settleRaf = requestAnimationFrame(function () {
                _settleRaf = null;
                emitZoomSettled();
            });
        });
    }

    function applyChartCounterZoom() {
        if (_lastZ === null) return false;

        const cz = String(1 / _lastZ);
        let allFound = true;

        CHART_SELECTORS.forEach(function (sel) {
            const el = document.querySelector(sel);
            if (el) {
                el.style.zoom = cz;
            } else {
                allFound = false;
            }
        });

        const outer = document.querySelector('.dashboard-outer');

        window.__dashboardZoomDebug = {
            source: 'applyChartCounterZoom',
            lastZ: _lastZ,
            counterZoom: cz,
            outerInlineZoom: outer ? outer.style.zoom || null : null,
            outerComputedZoom: outer ? getComputedStyle(outer).zoom : null,
            chartZooms: snapshotChartZooms(),
            allFound: allFound,
            ts: performance.now(),
        };

        if (allFound) {
            scheduleZoomSettled();
        }

        return allFound;
    }

    function applyZoom() {
        const outer    = document.querySelector('.dashboard-outer');
        const controls = document.querySelector('.side-panel-controls');
        const panel    = document.querySelector('.side-panel');
        if (!outer) return;

        const controlsW = controls ? controls.getBoundingClientRect().width : 0;
        const panelW    = panel    ? panel.getBoundingClientRect().width    : 0;
        const available = window.innerWidth - controlsW - panelW;

        if (available < 1) return;

        const zoomW = available / DESIGN_W;
        const zoomH = window.innerHeight / DESIGN_H;
        const Z     = Math.min(zoomW, zoomH);

        _lastZ = Z;
        window.__dashboardZoomSettled = false;
        window.__dashboardZoomValue = null;

        outer.style.zoom = Z;

        window.__dashboardZoomDebug = {
            source: 'applyZoom-before-counter',
            lastZ: _lastZ,
            outerInlineZoom: outer.style.zoom || null,
            outerComputedZoom: getComputedStyle(outer).zoom,
            available: available,
            zoomW: zoomW,
            zoomH: zoomH,
            chartZooms: snapshotChartZooms(),
            ts: performance.now(),
        };

        applyChartCounterZoom();
    }

    // Window resize — debounced
    let _resizeTimer = null;
    window.addEventListener('resize', function () {
        clearTimeout(_resizeTimer);
        _resizeTimer = setTimeout(applyZoom, 100);
    });

    // Side panel open/close fires as the CSS transition runs — ResizeObserver
    // catches the width change mid-transition and keeps zoom live during the slide.
    function attachObserver() {
        const panel = document.querySelector('.side-panel');
        if (!panel) return false;
        new ResizeObserver(applyZoom).observe(panel);
        return true;
    }

    // Poll until outer DOM ready, then wire up.
    const _init = setInterval(function () {
        if (!document.querySelector('.dashboard-outer')) return;
        clearInterval(_init);
        attachObserver();
        applyZoom();
    }, 100);

    // Separate poll for chart counter-zoom — charts render after outer DOM via React.
    const _chartInit = setInterval(function () {
        if (applyChartCounterZoom()) clearInterval(_chartInit);
    }, 200);

    document.addEventListener('mousemove', function(e) {
        window.__lastMouseX = e.clientX;
        window.__lastMouseY = e.clientY;
    });

})();