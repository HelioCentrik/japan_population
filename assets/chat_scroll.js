// Auto-scroll ai-chat-output to bottom whenever content changes.
// Uses MutationObserver — no Dash callback wiring required.

(function () {
    function attachScrollObserver() {
        var el = document.getElementById("ai-chat-output");
        if (!el) {
            setTimeout(attachScrollObserver, 400);
            return;
        }

        var observer = new MutationObserver(function () {
            el.scrollTop = el.scrollHeight;
        });

        observer.observe(el, { childList: true, subtree: true });

        // Scroll on initial attach in case history was restored
        el.scrollTop = el.scrollHeight;
    }

    if (document.readyState === "loading") {
        document.addEventListener("DOMContentLoaded", attachScrollObserver);
    } else {
        attachScrollObserver();
    }
})();