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

    function dashboardZoomReady() {
        return window.__dashboardZoomSettled === true;
    }

    function scheduleStartupSettleResize() {
        // The initial Plotly hover/bbox geometry can be stale even after the
        // dashboard zoom flag is true. A manual side-panel resize fixes it by
        // forcing Plotly to remeasure. Do that once, immediately after reveal.
        requestAnimationFrame(function () {
            requestAnimationFrame(function () {
                window.dispatchEvent(new Event('resize'));
            });
        });
    }

    function reveal() {
        if (revealed) return;
        revealed = true;

        const inner = document.querySelector('.map-inner');
        if (inner) inner.style.opacity = '1';

        resizeCharts();
        scheduleStartupSettleResize();
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

    function applyResizeZoom(plotDiv, height) {
        const target = Math.min(
            ZOOM_MAX,
            Math.max(ZOOM_MIN, REF_ZOOM + Math.log2(height / REF_HEIGHT))
        );

        const current = plotDiv._fullLayout?.map?.zoom ?? DEFAULT_ZOOM;

        if (Math.abs(current - target) >= 0.05) {
            return safeRelayout(plotDiv, {'map.zoom': target});
        }

        return Promise.resolve(true);
    }

    // getBoundingClientRect() returns zoomed viewport coords when CSS zoom is on
    // .dashboard-outer. Divide by the computed zoom factor to recover the
    // logical height that the map zoom formula expects.
    function logicalHeight(panel) {
        const outer = document.querySelector('.dashboard-outer');
        const zoom  = parseFloat(outer && getComputedStyle(outer).zoom) || 1;
        return panel.getBoundingClientRect().height / zoom;
    }

    function resizeCharts() {
        const jobs = [
            '#pyramid-chart .js-plotly-plot',
            '#timeseries-chart .js-plotly-plot',
        ].map(function (sel) {
            const el = document.querySelector(sel);
            return el ? safePlotlyResize(el) : Promise.resolve(false);
        });

        return Promise.all(jobs);
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
                const zoom = Math.min(
                    ZOOM_MAX,
                    Math.max(ZOOM_MIN, REF_ZOOM + Math.log2(h / REF_HEIGHT))
                );

                lastPanelHeight = h;

                return safeRelayout(plotDiv, {
                    'map.zoom':       zoom,
                    'map.center.lat': CENTER_LAT,
                    'map.center.lon': CENTER_LON,
                });
            })
            .then(function () {
                resizeCharts();
                return true;
            });
    }

    function attach() {
        const panel   = document.querySelector('.map-panel');
        const plotDiv = getPlotlyDiv();

        if (!dashboardZoomReady()) return false;
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
                // data update: year change, metric switch, prefecture click.
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
                setTimeout(function () {
                    window.refitMap();
                }, 0);
            } else {
                reveal();

                // Belt-and-suspenders: Plotly can fire an internal re-render after
                // our relayout that resets the viewport. Re-apply zoom post-reveal.
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

                safePlotlyResize(pDiv).then(function () {
                    const h = logicalHeight(panel);
                    lastPanelHeight = h;
                    applyResizeZoom(pDiv, h);
                    resizeCharts();
                });
            }, 150);
        });

        return true;
    }

    let _zoomSettleRaf = null;

    window.addEventListener('dashboard:zoom-settled', function () {
        if (_zoomSettleRaf) cancelAnimationFrame(_zoomSettleRaf);

        _zoomSettleRaf = requestAnimationFrame(function () {
            _zoomSettleRaf = null;

            if (revealed) {
                refitMapPlot();
            }
        });
    });

    const interval = setInterval(function () {
        if (attach()) clearInterval(interval);
    }, 200);

    // Exposed for the ⤢ button clientside callback.
    window.refitMap = function () {
        refitMapPlot();
        return window.dash_clientside.no_update;
    };
})();