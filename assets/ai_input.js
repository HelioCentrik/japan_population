// assets/ai_input.js

document.addEventListener('input', function (e) {
    if (!e.target || e.target.id !== 'ai-input') return;
    const el = e.target;
    el.style.height = 'auto';
    el.style.height = el.scrollHeight + 'px';
});