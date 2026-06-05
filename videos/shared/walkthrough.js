/**
 * PocketBudJet video walkthrough helpers — tech-support mode.
 */
(function () {
    var TAP_RULES = [
        [/settings|gear|toolbox/i, 88, 7, 'Settings'],
        [/gold \+|\+ button|tap the \+/i, 50, 90, 'Gold +'],
        [/plan tab|setup wizard/i, 38, 94, 'Plan tab'],
        [/home tab/i, 12, 94, 'Home'],
        [/transactions tab/i, 50, 94, 'Transactions'],
        [/progress tab|debt/i, 75, 94, 'Progress'],
        [/import receipt|import center/i, 50, 88, 'Import'],
        [/share icon|share sheet/i, 88, 33, 'Share'],
        [/confirm/i, 50, 91, 'Confirm'],
        [/export/i, 50, 55, 'Export'],
        [/scan receipt|camera/i, 50, 88, 'Scan'],
        [/search/i, 82, 9, 'Search'],
        [/qr|pair/i, 50, 48, 'QR code'],
        [/financial coach|ai coach/i, 50, 50, 'Coach'],
        [/household/i, 50, 55, 'Household'],
        [/storage|backup|cloud tab/i, 50, 38, 'Cloud'],
        [/category/i, 50, 42, 'Category'],
        [/account/i, 50, 52, 'Account'],
        [/amount/i, 50, 22, 'Amount'],
        [/split/i, 72, 58, 'Split'],
        [/bill calendar|calendar view/i, 50, 45, 'Calendar'],
        [/save/i, 85, 12, 'Save'],
        [/filter/i, 50, 35, 'Filter']
    ];

    var SKIP_TAP = /\b(done|intro|overview|finished|summary|private by|why )\b/i;

    function slideTitle(slide) {
        var el = slide.querySelector('.slide-title');
        return el ? el.textContent.trim() : '';
    }

    function narrationFor(index) {
        return document.querySelector('.narration-card[data-index="' + index + '"]');
    }

    function inferTap(slide) {
        var title = slideTitle(slide);
        var card = narrationFor(slide.getAttribute('data-index'));
        var text = card ? (card.querySelector('p') || {}).textContent || '' : '';
        var blob = (title + ' ' + text).toLowerCase();
        if (SKIP_TAP.test(title) && blob.indexOf('tap') === -1) return null;
        for (var i = 0; i < TAP_RULES.length; i++) {
            var rule = TAP_RULES[i];
            if (rule[0].test(blob)) {
                return { x: rule[1], y: rule[2], label: rule[3] };
            }
        }
        if (/\b(tap|open|select|choose)\b/i.test(text)) {
            return { x: 50, y: 45, label: 'Here' };
        }
        return null;
    }

    function buildTapIndicator(slide, x, y, label) {
        var ind = document.createElement('div');
        ind.className = 'tap-indicator';
        ind.style.left = x + '%';
        ind.style.top = y + '%';

        var ring = document.createElement('div');
        ring.className = 'tap-ring';
        ind.appendChild(ring);

        var outer = document.createElement('div');
        outer.className = 'tap-ring-outer';
        ind.appendChild(outer);

        var finger = document.createElement('span');
        finger.className = 'tap-finger';
        finger.innerHTML = '&#9757;';
        ind.appendChild(finger);

        if (label) {
            var lbl = document.createElement('span');
            lbl.className = 'tap-label';
            lbl.textContent = label;
            ind.appendChild(lbl);
        }
        return ind;
    }

    function buildHighlight(slide) {
        var x = slide.getAttribute('data-highlight-x');
        var y = slide.getAttribute('data-highlight-y');
        var w = slide.getAttribute('data-highlight-w');
        var h = slide.getAttribute('data-highlight-h');
        if (!x || !y || !w || !h) return null;

        var box = document.createElement('div');
        box.className = 'slide-highlight';
        box.style.left = x + '%';
        box.style.top = y + '%';
        box.style.width = w + '%';
        box.style.height = h + '%';
        box.style.transform = 'translate(-50%, -50%)';
        return box;
    }

    function hintFromNarration(slide) {
        var hint = slide.getAttribute('data-tap-hint');
        if (hint) return hint;
        var card = narrationFor(slide.getAttribute('data-index'));
        if (!card) return '';
        var p = card.querySelector('p');
        if (!p) return '';
        var text = p.textContent.trim();
        var parts = text.split(/(?<=[.!?])\s+/);
        for (var i = 0; i < parts.length; i++) {
            if (/\b(tap|open|choose|select|go to|scroll|scan|enter)\b/i.test(parts[i])) {
                return parts[i];
            }
        }
        if (/\b(tap|open)\b/i.test(text) && text.length < 240) return text;
        return '';
    }

    function initSlides() {
        document.querySelectorAll('.slide').forEach(function (slide) {
            slide.querySelectorAll(':scope > .tap-ring-outer, :scope > .tap-finger, :scope > .tap-ring').forEach(function (el) {
                el.remove();
            });

            var x = slide.getAttribute('data-tap-x');
            var y = slide.getAttribute('data-tap-y');
            var label = slide.getAttribute('data-tap-label') || '';

            if (!x || !y) {
                var inferred = inferTap(slide);
                if (inferred) {
                    x = String(inferred.x);
                    y = String(inferred.y);
                    if (!label) label = inferred.label;
                    slide.setAttribute('data-tap-x', x);
                    slide.setAttribute('data-tap-y', y);
                    if (label) slide.setAttribute('data-tap-label', label);
                }
            }

            if (!slide.querySelector('.tap-indicator') && x && y) {
                var ind = buildTapIndicator(slide, x, y, label);
                var overlay = slide.querySelector('.slide-overlay');
                if (overlay) slide.insertBefore(ind, overlay);
                else slide.appendChild(ind);
            }

            if (!slide.querySelector('.slide-highlight')) {
                var hi = buildHighlight(slide);
                if (hi) {
                    var ov = slide.querySelector('.slide-overlay');
                    if (ov) slide.insertBefore(hi, ov);
                    else slide.appendChild(hi);
                }
            }
        });
    }

    function initNarrationHints() {
        document.querySelectorAll('.slide').forEach(function (slide) {
            var index = slide.getAttribute('data-index');
            if (index === null) return;
            var hint = hintFromNarration(slide);
            if (!hint) return;
            var card = narrationFor(index);
            if (!card || card.querySelector('.narration-tap-hint')) return;

            var block = document.createElement('p');
            block.className = 'narration-tap-hint';
            block.innerHTML = '<strong>Where to tap</strong> ' + hint;

            var timer = card.querySelector('.narration-timer');
            if (timer) card.insertBefore(block, timer);
            else card.appendChild(block);
        });
    }

    function initLegend() {
        var controls = document.querySelector('.playback-controls');
        if (!controls || document.querySelector('.walkthrough-legend')) return;
        if (!document.querySelector('.slide[data-tap-x]')) return;

        var legend = document.createElement('p');
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
