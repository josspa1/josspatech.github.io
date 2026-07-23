/**
 * PocketBudJet video walkthrough helpers ΓÇö tech-support mode.
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
        return document.querySelector('.transcript-para[data-slide="' + index + '"]') ||
            document.querySelector('.transcript-para[data-index="' + index + '"]');
    }

    function syncTranscriptSlide(index) {
        var paras = document.querySelectorAll('.transcript-para');
        if (!paras.length) return;
        paras.forEach(function (p) {
            var slide = parseInt(p.getAttribute('data-slide') || p.getAttribute('data-index'), 10);
            p.classList.toggle('current', slide === index);
        });
        var active = narrationFor(String(index));
        if (!active) return;
        var panel = document.getElementById('narrationPanel');
        if (!panel) return;
        var panelRect = panel.getBoundingClientRect();
        var elRect = active.getBoundingClientRect();
        if (elRect.top < panelRect.top + 40 || elRect.bottom > panelRect.bottom - 40) {
            active.scrollIntoView({ behavior: 'smooth', block: 'nearest' });
        }
    }

    function inferTap(slide) {
        var title = slideTitle(slide);
        var card = narrationFor(slide.getAttribute('data-index'));
        var text = card ? (card.textContent || '') : '';
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

        // Gold pulse ring only — no finger emoji (Joe preference, PBJ + HHH parity).

        // PNG screenshots already show UI labels — skip the floating pill on phone PNGs.
        if (label && !slideUsesPng(slide)) {
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
        var p = card.querySelector('p') || card;
        if (!p) return '';
        var text = p.textContent.trim();
        var parts = text.split(/(?<=[.!?])\s+/);
        for (var i = 0; i < parts.length; i++) {
            if (/\b(tap|open|choose|select|go to|scroll|scan|enter|switch|swipe|fill|install|manage|allow|use|browse|expand)\b/i.test(parts[i])) {
                return parts[i];
            }
        }
        if (/\b(tap|open|switch|scroll|swipe|fill|install|manage)\b/i.test(text) && text.length < 240) return text;
        return '';
    }

    function slideUsesPng(slide) {
        var img = slide.querySelector('img[src]');
        if (!img) return false;
        return /\.png(\?|$)/i.test(img.getAttribute('src') || '');
    }

    var tapTimers = [];

    function clearTapPulse() {
        tapTimers.forEach(function (id) { clearTimeout(id); });
        tapTimers = [];
        document.querySelectorAll('.tap-indicator.tap-visible, .slide-highlight.tap-visible').forEach(function (el) {
            el.classList.remove('tap-visible');
        });
    }

    function getTapTiming(slide) {
        var showAt = parseFloat(slide.getAttribute('data-tap-show-at'));
        var duration = parseFloat(slide.getAttribute('data-tap-duration'));
        if (isNaN(showAt)) showAt = 0.3;
        if (isNaN(duration)) duration = 2.5;
        return { showAtMs: showAt * 1000, durationMs: duration * 1000 };
    }

    function setTapVisible(slide, visible) {
        if (!slide) return;
        var ind = slide.querySelector('.tap-indicator');
        var hi = slide.querySelector('.slide-highlight');
        if (ind) ind.classList.toggle('tap-visible', visible);
        if (hi) hi.classList.toggle('tap-visible', visible);
    }

    function scheduleTapPulse(slideIndex) {
        clearTapPulse();
        var slide = document.querySelector('.slide[data-index="' + slideIndex + '"]');
        if (!slide || slide.hasAttribute('data-tap-none')) return;
        if (!slide.getAttribute('data-tap-x') || !slide.getAttribute('data-tap-y')) return;

        var timing = getTapTiming(slide);
        var showTimer = setTimeout(function () {
            setTapVisible(slide, true);
        }, timing.showAtMs);
        var hideTimer = setTimeout(function () {
            setTapVisible(slide, false);
        }, timing.showAtMs + timing.durationMs);
        tapTimers.push(showTimer, hideTimer);
    }

    function showTapNow(slideIndex) {
        clearTapPulse();
        var slide = document.querySelector('.slide[data-index="' + slideIndex + '"]');
        if (!slide || slide.hasAttribute('data-tap-none')) return;
        if (!slide.getAttribute('data-tap-x')) return;
        setTapVisible(slide, true);
    }

    function hideTapNow(slideIndex) {
        var slide = document.querySelector('.slide[data-index="' + slideIndex + '"]');
        setTapVisible(slide, false);
    }

    function initSlides() {
        document.querySelectorAll('.slide').forEach(function (slide) {
            slide.querySelectorAll(':scope > .tap-ring-outer, :scope > .tap-finger, :scope > .tap-ring').forEach(function (el) {
                el.remove();
            });

            if (slide.hasAttribute('data-tap-none')) return;

            var x = slide.getAttribute('data-tap-x');
            var y = slide.getAttribute('data-tap-y');
            var label = slide.getAttribute('data-tap-label') || '';

            // Gold pulse only when explicit tap coords are set (never infer or default).
            if (!x || !y) return;

            if (!slide.querySelector('.tap-indicator')) {
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
            if (!card || card.classList.contains('transcript-para')) return;
            if (card.querySelector('.narration-tap-hint')) return;

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
        var activeSlide = document.querySelector('.slide.active');
        if (activeSlide) {
            var idx = parseInt(activeSlide.getAttribute('data-index'), 10);
            if (!isNaN(idx)) syncTranscriptSlide(idx);
        }
    }

    window.PBJWalkthrough = window.PBJWalkthrough || {};
    window.PBJWalkthrough.syncTranscriptSlide = syncTranscriptSlide;
    window.PBJWalkthrough.clearTapPulse = clearTapPulse;
    window.PBJWalkthrough.scheduleTapPulse = scheduleTapPulse;
    window.PBJWalkthrough.showTapNow = showTapNow;
    window.PBJWalkthrough.hideTapNow = hideTapNow;
    window.initWalkthroughSlides = init;
    window.syncTranscriptSlide = syncTranscriptSlide;

    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', init);
    } else {
        init();
    }

    if (window.PBJWalkthrough && window.PBJWalkthrough.registerTeardown) {
        window.PBJWalkthrough.registerTeardown(clearTapPulse);
    } else {
        window.__pbjTeardownQueue = window.__pbjTeardownQueue || [];
        window.__pbjTeardownQueue.push(clearTapPulse);
    }
})();

/**
 * Shared audio teardown ΓÇö stops MP3 narration when the tab closes, navigates
 * away, or is hidden. Pages register slide-specific cleanup via registerTeardown.
 */
(function () {
    var teardownFns = [];
    var listenersInstalled = false;

    function stopAllAudio() {
        teardownFns.forEach(function (fn) {
            try { fn(); } catch (e) { /* ignore */ }
        });
        document.querySelectorAll('audio').forEach(function (a) {
            a.onended = null;
            a.onerror = null;
            a.loop = false;
            a.pause();
            a.currentTime = 0;
            a.removeAttribute('src');
            if (a.load) a.load();
        });
        if (window.speechSynthesis) {
            try { window.speechSynthesis.cancel(); } catch (e) { /* ignore */ }
        }
    }

    function installListeners() {
        if (listenersInstalled) return;
        listenersInstalled = true;
        window.addEventListener('pagehide', stopAllAudio);
        window.addEventListener('beforeunload', stopAllAudio);
        document.addEventListener('visibilitychange', function () {
            if (document.hidden) stopAllAudio();
        });
    }

    window.PBJWalkthrough = window.PBJWalkthrough || {};
    window.PBJWalkthrough.registerTeardown = function (fn) {
        if (typeof fn === 'function') teardownFns.push(fn);
    };
    window.PBJWalkthrough.stopAllAudio = stopAllAudio;

    installListeners();

    var queue = window.__pbjTeardownQueue;
    if (queue && queue.length) {
        queue.forEach(function (fn) {
            window.PBJWalkthrough.registerTeardown(fn);
        });
        window.__pbjTeardownQueue = [];
    }
})();
