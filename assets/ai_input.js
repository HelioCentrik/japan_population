// assets/ai_input.js

document.addEventListener('input', function (e) {
    if (!e.target || e.target.id !== 'ai-input') return;
    const el = e.target;
    el.style.height = 'auto';
    el.style.height = el.scrollHeight + 'px';
});

// Dash sets .value as a JS property (not an HTML attribute) so MutationObserver
// won't catch it. A lightweight poll is the reliable fix.
setInterval(function () {
    const el = document.getElementById('ai-input');
    if (el && el.value === '') {
        el.style.height = 'auto';
    }
}, 150);