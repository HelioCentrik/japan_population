// assets/dashboard_zoom.js
(function () {
    if (!window.DASHBOARD_CONFIG) {
        console.warn('[dashboard_zoom] DASHBOARD_CONFIG not found');
        return;
    }

    const DESIGN_W = window.DASHBOARD_CONFIG.w;
    const DESIGN_H = window.DASHBOARD_CONFIG.h;   // ← add

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
        const zoomH = window.innerHeight / DESIGN_H;   // ← add
        outer.style.zoom = Math.min(zoomW, zoomH);     // ← was: available / DESIGN_W
    }

    // Window resize — debounced
    let _resizeTimer = null;
    window.addEventListener('resize', function () {
        clearTimeout(_resizeTimer);
        _resizeTimer = setTimeout(applyZoom, 100);
    });

    // Side panel open/close fires as the CSS transition runs — ResizeObserver
    // catches the width change mid-transition and keeps zoom live during the slide
    function attachObserver() {
        const panel = document.querySelector('.side-panel');
        if (!panel) return false;
        new ResizeObserver(applyZoom).observe(panel);
        return true;
    }

    // Poll until DOM is ready, then wire up and apply initial zoom
    const _init = setInterval(function () {
        if (!document.querySelector('.dashboard-outer')) return;
        clearInterval(_init);
        attachObserver();
        applyZoom();
    }, 100);

})();