// assets/slider_density.js
// Tags slider marks with data-year and sets body density class on resize.
// CSS in style.css reacts to .slider-thin / .slider-thinner to hide labels.
(function () {
    function tagMarks() {
        document.querySelectorAll('.dash-slider-mark').forEach(function (mark) {
            if (mark.dataset.year) return;
            var text = mark.textContent.trim();
            if (text) mark.dataset.year = text;
        });
    }

    function setDensity() {
        var w = window.innerWidth;
        document.body.classList.remove('slider-thin', 'slider-thinner');
        if (w < 768)  document.body.classList.add('slider-thinner');
        else if (w < 1100) document.body.classList.add('slider-thin');
    }

    function init() {
        tagMarks();
        setDensity();
    }

    window.addEventListener('resize', setDensity);

    // Marks render after Dash hydration — observe until they appear
    var observer = new MutationObserver(function () {
        if (document.querySelector('.dash-slider-mark')) {
            init();
            observer.disconnect();
        }
    });
    observer.observe(document.body, { childList: true, subtree: true });

    // Also try immediately in case we're already hydrated
    if (document.querySelector('.dash-slider-mark')) init();
}());