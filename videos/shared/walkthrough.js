/**
 * PocketBudJet video walkthrough helpers.
 * - Builds tap indicators from data-tap-x / data-tap-y / data-tap-label
 * - Injects "Where to tap" hints into narration cards from data-tap-hint
 * - Optional highlight regions from data-highlight-x/y/w/h (percent)
 */
(function () {
    function buildTapIndicator(slide) {
        const x = slide.getAttribute('data-tap-x');
        const y = slide.getAttribute('data-tap-y');
        if (!x || !y) return null;

        const label = slide.getAttribute('data-tap-label') || '';
        const ind = document.createElement('div');
        ind.className = 'tap-indicator';
        ind.style.left = x + '%';
        ind.style.top = y + '%';

        const ring = document.createElement('div');
        ring.className = 'tap-ring';
        ind.appendChild(ring);

        const outer = document.createElement('div');
        outer.className = 'tap-ring-outer';
        ind.appendChild(outer);

        const finger = document.createElement('span');
        finger.className = 'tap-finger';
        finger.innerHTML = '&#9757;';
        ind.appendChild(finger);

        if (label) {
            const lbl = document.createElement('span');
            lbl.className = 'tap-label';
            lbl.textContent = label;
            ind.appendChild(lbl);
        }

        return ind;
    }

    function buildHighlight(slide) {
        const x = slide.getAttribute('data-highlight-x');
        const y = slide.getAttribute('data-highlight-y');
        const w = slide.getAttribute('data-highlight-w');
        const h = slide.getAttribute('data-highlight-h');
        if (!x || !y || !w || !h) return null;

        const box = document.createElement('div');
        box.className = 'slide-highlight';
        box.style.left = x + '%';
        box.style.top = y + '%';
        box.style.width = w + '%';
        box.style.height = h + '%';
        box.style.transform = 'translate(-50%, -50%)';
        if (slide.getAttribute('data-highlight-anchor') !== 'topleft') {
            box.style.transform = 'translate(-50%, -50%)';
        }
        return box;
    }

    function initSlides() {
        document.querySelectorAll('.slide').forEach(function (slide) {
            slide.querySelectorAll(':scope > .tap-ring-outer, :scope > .tap-finger, :scope > .tap-ring').forEach(function (el) {
                el.remove();
            });

            if (!slide.querySelector('.tap-indicator')) {
                const ind = buildTapIndicator(slide);
                if (ind) {
                    const overlay = slide.querySelector('.slide-overlay');
                    if (overlay) {
                        slide.insertBefore(ind, overlay);
                    } else {
                        slide.appendChild(ind);
                    }
                }
            }

            if (!slide.querySelector('.slide-highlight')) {
                const hi = buildHighlight(slide);
                if (hi) {
                    const overlay = slide.querySelector('.slide-overlay');
                    if (overlay) {
                        slide.insertBefore(hi, overlay);
                    } else {
                        slide.appendChild(hi);
                    }
                }
            }
        });
    }

    function initNarrationHints() {
        document.querySelectorAll('.slide[data-tap-hint]').forEach(function (slide) {
            const index = slide.getAttribute('data-index');
            if (index === null) return;
            const hint = slide.getAttribute('data-tap-hint');
            const card = document.querySelector('.narration-card[data-index="' + index + '"]');
            if (!card || card.querySelector('.narration-tap-hint')) return;

            const block = document.createElement('p');
            block.className = 'narration-tap-hint';
            block.innerHTML = '<strong>Where to tap</strong>' + hint;

            const timer = card.querySelector('.narration-timer');
            if (timer) {
                card.insertBefore(block, timer);
            } else {
                card.appendChild(block);
            }
        });
    }

    function initLegend() {
        const controls = document.querySelector('.playback-controls');
        if (!controls || document.querySelector('.walkthrough-legend')) return;
        if (!document.querySelector('.slide[data-tap-x]')) return;

        const legend = document.createElement('p');
        legend.className = 'walkthrough-legend';
        legend.textContent = 'Gold pulse = tap here on your phone';
        controls.parentNode.insertBefore(legend, controls.nextSibling);
    }

    function init() {
        initSlides();
        initNarrationHints();
        initLegend();
    }

    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', init);
    } else {
        init();
    }
})();
