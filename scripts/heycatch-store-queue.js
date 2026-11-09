/**
 * Classic (non-module) script — runs before the deferred HeyCatch module.
 * Queues Play / App Store taps so they still fire after init, and opens the
 * store in a new tab so same-tab navigation cannot cancel the beacon.
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
    window.__hcStoreQueue.push(String(a.href));
  }

  document.addEventListener('pointerdown', onIntent, true);
  document.addEventListener('click', onIntent, true);
})();
