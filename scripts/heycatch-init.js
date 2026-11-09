/**
 * HeyCatch for josspatech.com (static marketing site).
 * https://heycatch.ai/agents.md — pin the latest stable SDK (no -dev).
 *
 * Each public page loads from <head>:
 *   <script src="/scripts/heycatch-store-queue.js"></script>
 *   <link rel="modulepreload" href="/scripts/vendor/heycatch-sdk-0.8.5.js">
 *   <script type="module" src="/scripts/heycatch-init.js?v=11"></script>
 *
 * Funnel success names (literal — never bare "store_click"):
 *   store_click_pbj / store_click_pbj_google_play / store_click_pbj_app_store
 *   (same for hhh, cvc, unscribe)
 *
 * v=11: hold the navigation ourselves (preventDefault + window.open) so the
 * trackEvent beacon is not cancelled by Play/App Store navigation, and send a
 * one-shot landing_store_funnel_ready ping so ingest can confirm custom events.
 */
import { analytics } from '/scripts/vendor/heycatch-sdk-0.8.5.js';

var framed = false;
try { framed = window.top !== window.self; } catch (e) { framed = true; }

if (!framed) {
  analytics.init({
    projectKey: 'hck_pk_kHHaqwkbOlQRAk0BomIfCNQw-NlPKCCu',
    site: 'landing',
    requestBatching: false,
    install: {
      framework: 'web',
      agent: 'cursor',
    },
  });
}

var STORE_EVENTS = {
  pbj: {
    any: 'store_click_pbj',
    google_play: 'store_click_pbj_google_play',
    app_store: 'store_click_pbj_app_store',
  },
  hhh: {
    any: 'store_click_hhh',
    google_play: 'store_click_hhh_google_play',
    app_store: 'store_click_hhh_app_store',
  },
  cvc: {
    any: 'store_click_cvc',
    google_play: 'store_click_cvc_google_play',
    app_store: 'store_click_cvc_app_store',
  },
  unscribe: {
    any: 'store_click_unscribe',
    google_play: 'store_click_unscribe_google_play',
    app_store: 'store_click_unscribe_app_store',
  },
};

function appFromStoreHref(href) {
  var blob = String(href || '').toLowerCase();
  if (/pocketbudjet|id6761077263/.test(blob)) return 'pbj';
  if (/handyhorology|id6778570480|handy-horology/.test(blob)) return 'hhh';
  if (/josspatech\.cts|curator|id6778571307/.test(blob)) return 'cvc';
  if (/josspatech\.snip|unscribe|id6823295613/.test(blob)) return 'unscribe';
  return appFromPage();
}

function appFromPage() {
  var path = (location.pathname || '').toLowerCase();
  var hash = (location.hash || '').toLowerCase();
  var blob = path + ' ' + hash;
  if (/\/pbj(\/|$)|#pbj\b/.test(blob)) return 'pbj';
  if (/\/hhh(\/|$)|#hhh\b/.test(blob)) return 'hhh';
  if (/\/cvc(\/|$)|#cvc\b|\/cts(\/|$)/.test(blob)) return 'cvc';
  if (/\/unscribe(\/|$)|#unscribe\b|\/snip(\/|$)/.test(blob)) return 'unscribe';
  return 'unknown';
}

function currentPage() {
  return (location.pathname + location.search + location.hash).slice(0, 200);
}

var _lastStore = { href: '', t: 0 };

function trackStoreClick(href) {
  if (framed) return false;
  var store = null;
  if (/play\.google\.com/i.test(href)) store = 'google_play';
  else if (/apps\.apple\.com|itunes\.apple\.com|testflight\.apple\.com/i.test(href)) store = 'app_store';
  else return false;

  var now = Date.now();
  if (_lastStore.href === href && now - _lastStore.t < 1500) return true;
  _lastStore = { href: href, t: now };

  var app = appFromStoreHref(href);
  var names = STORE_EVENTS[app];
  if (!names) return false;

  var props = {
    app: app,
    store: store,
    page: currentPage(),
    href: String(href).slice(0, 200),
  };

  analytics.trackEvent(names.any, props);
  analytics.trackEvent(names[store], props);
  return true;
}

window.__hcTrackStoreClick = trackStoreClick;

function isStoreHref(href) {
  return /play\.google\.com|apps\.apple\.com|itunes\.apple\.com|testflight\.apple\.com/i.test(
    href || ''
  );
}

function onStoreLinkIntent(e) {
  if (e.type === 'click' && e.button != null && e.button !== 0) return;
  if (e.metaKey || e.ctrlKey || e.shiftKey || e.altKey) return;
  var t = e.target;
  if (!t || !t.closest) return;
  var a = t.closest('a[href]');
  if (!a || !a.href || !isStoreHref(a.href)) return;

  // Own the navigation so Play/App Store cannot cancel the ingest request.
  try {
    e.preventDefault();
    e.stopPropagation();
  } catch (err) {}

  trackStoreClick(a.href);

  var href = a.href;
  // Open after a tick so trackEvent can schedule its request first.
  setTimeout(function () {
    try {
      var w = window.open(href, '_blank', 'noopener');
      if (!w) location.href = href; // popup blocked — last resort
    } catch (err) {
      location.href = href;
    }
  }, 50);
}

document.addEventListener('pointerdown', onStoreLinkIntent, true);
document.addEventListener('mousedown', onStoreLinkIntent, true);
document.addEventListener('touchstart', onStoreLinkIntent, true);
document.addEventListener('click', onStoreLinkIntent, true);

try {
  var q = window.__hcStoreQueue || [];
  window.__hcStoreQueue = [];
  for (var i = 0; i < q.length; i++) trackStoreClick(q[i]);
} catch (err) {}

// One-shot ping: proves custom trackEvent from landing reaches ingest without a click.
if (!framed) {
  try {
    var pingKey = 'hc_landing_store_funnel_ready_v11';
    if (!sessionStorage.getItem(pingKey)) {
      sessionStorage.setItem(pingKey, '1');
      analytics.trackEvent('landing_store_funnel_ready', {
        page: currentPage(),
        v: 11,
      });
    }
  } catch (err) {}
}

var lastProductSection = '';
function trackProductSection() {
  if (framed) return;
  var raw = (location.hash || '').replace(/^#/, '').toLowerCase();
  if (!raw || raw === lastProductSection) return;
  var app = null;
  if (raw === 'products') {
    lastProductSection = raw;
    analytics.trackEvent('products_section', { page: currentPage() });
    return;
  }
  if (raw === 'pbj') app = 'pbj';
  else if (raw === 'hhh') app = 'hhh';
  else if (raw === 'cvc') app = 'cvc';
  else if (raw === 'unscribe') app = 'unscribe';
  else return;
  lastProductSection = raw;
  analytics.trackEvent('product_section_' + app, { app: app, page: currentPage() });
}
window.addEventListener('hashchange', trackProductSection);
if (document.readyState === 'loading') {
  document.addEventListener('DOMContentLoaded', trackProductSection);
} else {
  trackProductSection();
}
