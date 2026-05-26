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
    let startupSettling = false;
    let lastPanelHeight = 0;
    let _settleRaf      = null;
    let _resizeTimer    = null;

    function dashboardZoomReady() {
        return window.__dashboardZoomSettled === true;
    }

    function revealNow() {
        if (revealed) return;

        revealed = true;
        startupSettling = false;

        const mapInner = document.querySelector('.map-inner');
        if (mapInner) mapInner.style.opacity = '1';

        ['.map-inner', '#pyramid-chart', '#timeseries-chart'].forEach(function (sel) {
            const el = document.querySelector(sel);
            if (el) el.classList.add('dashboard-chart-visible');
        });
    }

    function retryRelayout(plotDiv, update, attempt, error) {
        if (attempt >= 4) {
            console.warn('[map_resize] safeRelayout gave up after 5 attempts', error);
            return Promise.resolve(false);
        }

        const delay = 100 * Math.pow(2, attempt);

        return new Promise(function (resolve) {
            setTimeout(function () {
                resolve(safeRelayout(plotDiv, update, attempt + 1));
            }, delay);
        });
    }

    // Plotly.relayout with map layout props can fail while MapLibre style/layers
    // are still async-loading. Plotly.relayout returns a Promise, so try/catch
    // alone does not catch all failures.
    function safeRelayout(plotDiv, update, attempt) {
        attempt = attempt || 0;

        try {
            return Promise.resolve(Plotly.relayout(plotDiv, update))
                .then(function () {
                    return true;
                })
                .catch(function (e) {
                    return retryRelayout(plotDiv, update, attempt, e);
                });
        } catch (e) {
            return retryRelayout(plotDiv, update, attempt, e);
        }
    }

    function safePlotlyResize(plotDiv) {
        if (!plotDiv) return Promise.resolve(false);

        try {
            return Promise.resolve(Plotly.Plots.resize(plotDiv))
                .then(function () {
                    return true;
                })
                .catch(function () {
                    return false;
                });
        } catch (e) {
            return Promise.resolve(false);
        }
    }

    // getBoundingClientRect() returns zoomed viewport coords when CSS zoom is on
    // .dashboard-outer. Divide by computed zoom to recover logical dashboard units.
    function logicalHeight(panel) {
        const outer = document.querySelector('.dashboard-outer');
        const zoom  = parseFloat(outer && getComputedStyle(outer).zoom) || 1;
        return panel.getBoundingClientRect().height / zoom;
    }

    function targetZoomForHeight(height) {
        return Math.min(
            ZOOM_MAX,
            Math.max(ZOOM_MIN, REF_ZOOM + Math.log2(height / REF_HEIGHT))
        );
    }

    function resizeOtherCharts() {
        const jobs = [
            '#pyramid-chart .js-plotly-plot',
            '#timeseries-chart .js-plotly-plot',
        ].map(function (sel) {
            const el = document.querySelector(sel);
            return el ? safePlotlyResize(el) : Promise.resolve(false);
        });

        return Promise.all(jobs);
    }

    function applyResizeZoom(plotDiv, height) {
        const target  = targetZoomForHeight(height);
        const current = plotDiv._fullLayout?.map?.zoom ?? DEFAULT_ZOOM;

        if (Math.abs(current - target) >= 0.05) {
            return safeRelayout(plotDiv, {'map.zoom': target});
        }

        return Promise.resolve(true);
    }

    function refitMapPlot() {
        const panel   = document.querySelector('.map-panel');
        const plotDiv = getPlotlyDiv();

        if (!panel || !plotDiv || !dashboardZoomReady()) {
            return Promise.resolve(false);
        }

        return safePlotlyResize(plotDiv)
            .then(function () {
                const h = logicalHeight(panel);
                const zoom = targetZoomForHeight(h);

                lastPanelHeight = h;

                return safeRelayout(plotDiv, {
                    'map.zoom':       zoom,
                    'map.center.lat': CENTER_LAT,
                    'map.center.lon': CENTER_LON,
                });
            })
            .then(function () {
                return resizeOtherCharts();
            })
            .then(function () {
                return true;
            });
    }

    function hasMapData() {
        const plotDiv = getPlotlyDiv();
        return !!(plotDiv && plotDiv.data && plotDiv.data.length > 0);
    }

    function scheduleStartupSettleResize() {
        // This intentionally uses the real resize event path because direct
        // Plotly resize/relayout did not fix Plotly's initial stale hover bbox.
        // Keep the map hidden during this pass, then reveal from the resize handler.
        if (revealed || startupSettling) return;
        if (!dashboardZoomReady()) return;
        if (!hasMapData()) return;

        startupSettling = true;

        requestAnimationFrame(function () {
            requestAnimationFrame(function () {
                window.dispatchEvent(new Event('resize'));
            });
        });

        // Safety hatch: never leave the map invisible forever.
        setTimeout(function () {
            if (!revealed) revealNow();
        }, 1500);
    }

    function schedulePostRevealSettle(centerMap) {
        if (_settleRaf) cancelAnimationFrame(_settleRaf);

        _settleRaf = requestAnimationFrame(function () {
            _settleRaf = null;

            if (!revealed) {
                scheduleStartupSettleResize();
                return;
            }

            if (centerMap) {
                refitMapPlot();
                return;
            }

            const panel   = document.querySelector('.map-panel');
            const plotDiv = getPlotlyDiv();

            if (!panel || !plotDiv || !dashboardZoomReady()) return;

            const h = logicalHeight(panel);
            lastPanelHeight = h;
            applyResizeZoom(plotDiv, h);
            resizeOtherCharts();
        });
    }

    function attach() {
        const panel   = document.querySelector('.map-panel');
        const plotDiv = getPlotlyDiv();

        if (!dashboardZoomReady()) return false;
        if (!panel || !plotDiv) return false;
        if (!plotDiv._fullLayout?.map) return false;

        lastPanelHeight = logicalHeight(panel);

        plotDiv.on('plotly_afterplot', function () {
            if (!plotDiv._fullLayout?.map) return;
            if (!hasMapData()) return;

            if (!revealed) {
                scheduleStartupSettleResize();
                return;
            }

            // After reveal, only re-zoom on real panel-height changes.
            // Data updates fire afterplot too; those should not constantly refit.
            const h = logicalHeight(panel);

            if (Math.abs(h - lastPanelHeight) > 2) {
                lastPanelHeight = h;
                schedulePostRevealSettle(false);
            }
        });

        // Catch-up path in case data exists before listener attach.
        setTimeout(scheduleStartupSettleResize, 300);

        // Last-resort fallback.
        setTimeout(function () {
            if (!revealed) {
                scheduleStartupSettleResize();

                setTimeout(function () {
                    if (!revealed) revealNow();
                }, 1500);
            }
        }, 3000);

        return true;
    }

    window.addEventListener('resize', function () {
        if (!revealed && !startupSettling) return;

        clearTimeout(_resizeTimer);

        _resizeTimer = setTimeout(function () {
            const panel   = document.querySelector('.map-panel');
            const plotDiv = getPlotlyDiv();

            if (!panel || !plotDiv) return;

            safePlotlyResize(plotDiv)
                .then(function () {
                    const h = logicalHeight(panel);
                    lastPanelHeight = h;
                    return applyResizeZoom(plotDiv, h);
                })
                .then(function () {
                    return resizeOtherCharts();
                })
                .then(function () {
                    if (startupSettling) {
                        revealNow();
                    }
                });
        }, 150);
    });

    window.addEventListener('dashboard:zoom-settled', function () {
        // dashboard_zoom.js owns zoom/counter-zoom.
        // map_resize.js responds after that contract is stable.
        schedulePostRevealSettle(true);
    });

    const interval = setInterval(function () {
        if (attach()) clearInterval(interval);
    }, 200);

    // Exposed for the ⤢ button clientside callback.
    window.refitMap = function () {
        schedulePostRevealSettle(true);
        return window.dash_clientside.no_update;
    };
})();