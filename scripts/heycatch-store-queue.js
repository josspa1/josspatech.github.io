/**
 * Classic (non-module) script — runs before the deferred HeyCatch module.
 * Queues Play / App Store taps so they still fire after init, opens the
 * store in a new tab, and calls window.__hcTrackStoreClick once the module
 * exposes it (so we do not wait for a second click).
 */
(function () {
  if (window.__hcStoreQueueBooted) return;
  window.__hcStoreQueueBooted = true;
  window.__hcStoreQueue = window.__hcStoreQueue || [];

  function isStoreHref(href) {
    return /play\.google\.com|apps\.apple\.com|itunes\.apple\.com|testflight\.apple\.com/i.test(
      href || ''
    );
  }

  function fireOrQueue(href) {
    var h = String(href || '');
    if (!h) return;
    if (typeof window.__hcTrackStoreClick === 'function') {
      try {
        window.__hcTrackStoreClick(h);
        return;
      } catch (err) {}
    }
    window.__hcStoreQueue.push(h);
  }

  function onIntent(e) {
    if (e.type === 'click' && e.button != null && e.button !== 0) return;
    var t = e.target;
    if (!t || !t.closest) return;
    var a = t.closest('a[href]');
    if (!a || !a.href || !isStoreHref(a.href)) return;
    try {
      a.setAttribute('target', '_blank');
      a.setAttribute('rel', 'noopener');
    } catch (err) {}
    fireOrQueue(a.href);
  }

  document.addEventListener('pointerdown', onIntent, true);
  document.addEventListener('mousedown', onIntent, true);
  document.addEventListener('touchstart', onIntent, true);
  document.addEventListener('click', onIntent, true);
})();
