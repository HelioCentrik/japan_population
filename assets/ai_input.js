// assets/ai_input.js

document.addEventListener('input', function (e) {
    if (!e.target || e.target.id !== 'ai-input') return;
    const el = e.target;
    el.style.height = 'auto';
    el.style.height = el.scrollHeight + 'px';
});

// Reset height when Dash clears the value via callback
document.addEventListener('DOMContentLoaded', function () {
    const observer = new MutationObserver(function () {
        const el = document.getElementById('ai-input');
        if (el && el.value === '') {
            el.style.height = 'auto';
        }
    });
    observer.observe(doc