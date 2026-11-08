/**
 * HeyCatch for josspatech.com (static marketing site).
 * https://heycatch.ai/agents.md — pin the latest stable SDK (no -dev).
 *
 * Each public page loads this from <head>:
 *   <script type="module" src="/scripts/heycatch-init.js?v=6"></script>
 * Do not inject it after load. A deferred inject misses the landing pageview
 * on mobile, which is how TikTok visits showed sessions and zero pageviews.
 *
 * site: 'landing' keeps these visits apart from the phone apps.
 * requestBatching: false — full page loads; mobile Safari drops a batched beacon.
 *
 * HeyCatch Website funnels match on event *names* only (no property filters).
 * Published apps only: pbj, hhh, cvc, unscribe. PAL is not in stores yet — omit.
 * Store taps fire distinct names per app and per store destination:
 *   store_click_pbj
 *   store_click_pbj_google_play
 *   store_click_pbj_app_store
 * Properties (app, store, page, href) stay on the event for the live feed.
 */
import { analytics } from 'https://esm.sh/@heycatch/sdk@0.8.5';

// Product pages embed media in an iframe. That frame is not a visit.
var framed = false;
try { framed = window.top !== window.self; } catch (e) { framed = true; }
if (!framed) analytics.init({
  projectKey: 'hck_pk_kHHaqwkbOlQRAk0BomIfCNQw-NlPKCCu',
  site: 'landing',
  requestBatching: false,
  install: {
    framework: 'web',
    agent: 'cursor',
  },
});

/** Which published app the *store link destination* belongs to. */
function appFromStoreHref(href) {
  var blob = String(href || '').toLowerCase();
  if (/pocketbudjet|id6761077263/.test(blob)) return 'pbj';
  if (/handyhorology|id6778570480|handy-horology/.test(blob)) return 'hhh';
  if (/josspatech\.cts|curator|id6778571307/.test(blob)) return 'cvc';
  if (/josspatech\.snip|unscribe|id6823295613/.test(blob)) return 'unscribe';
  // Developer listing / unknown package — fall back to the page they clicked from.
  return appFromPage();
}

/** Which published product page / home section the visitor is on. */
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

/**
 * Store badge / text store link → named events HeyCatch funnels can select.
 * Two names per tap so you can funnel by app, or by app+store.
 * Skip unknown (no published app matched) so we do not invent junk event names.
 */
document.addEventListener(
  'click',
  function (e) {
    var t = e.target;
    if (!t || !t.closest) return;
    var a = t.closest('a[href]');
    if (!a) return;
    var href = a.href || '';
    var store = null;
    if (/play\.google\.com/i.test(href)) store = 'google_play';
    else if (/apps\.apple\.com|itunes\.apple\.com|testflight\.apple\.com/i.test(href)) store = 'app_store';
    else return;

    var app = appFromStoreHref(href);
    if (app === 'unknown') return;

    var props = {
      app: app,
      store: store,
      page: currentPage(),
      href: href.slice(0, 200),
    };

    // Per-app success (any store) — use as funnel step 3.
    analytics.trackEvent('store_click_' + app, props);
    // Per-app + which store link — Play vs App Store.
    analytics.trackEvent('store_click_' + app + '_' + store, props);
  },
  true
);

/**
 * Home SPA (#products / #pbj / …) does not load a new document, so autocapture
 * only sees "/". Named events so funnels can use them without property filters.
 * Published apps only — no PAL.
 */
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
