/**
 * HeyCatch for josspatech.com (static marketing site).
 * https://heycatch.ai/agents.md — pin the latest stable SDK (no -dev).
 *
 * Each public page loads this from <head>:
 *   <script type="module" src="/scripts/heycatch-init.js?v=4"></script>
 * Do not inject it after load. A deferred inject misses the landing pageview
 * on mobile, which is how TikTok visits showed sessions and zero pageviews.
 *
 * site: 'landing' keeps these visits apart from the phone apps.
 * requestBatching: false — full page loads; mobile Safari drops a batched beacon.
 *
 * store_click always includes app (pbj|hhh|cvc|unscribe|pal) so per-app
 * Website funnels can filter the success step by property.
 */
import { analytics } from 'https://esm.sh/@heycatch/sdk@0.8.5';

// Product pages embed the walkthrough in an iframe. That frame is not a visit.
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

/** Resolve which app a store badge / URL belongs to. */
function appFromContext(href) {
  var path = (location.pathname || '').toLowerCase();
  var hash = (location.hash || '').toLowerCase();
  var blob = (href + ' ' + path + ' ' + hash).toLowerCase();

  // Play package ids and App Store numeric ids (href-only Apple links have no name).
  if (/pocketbudjet|id6761077263|\/pbj(\/|$)|#pbj\b/.test(blob)) return 'pbj';
  if (/handyhorology|id6778570480|\/hhh(\/|$)|#hhh\b/.test(blob)) return 'hhh';
  if (/josspatech\.cts|curator|id6778571307|\/cvc(\/|$)|#cvc\b|\/cts(\/|$)/.test(blob)) return 'cvc';
  if (/josspatech\.snip|unscribe|id6823295613|\/unscribe(\/|$)|#unscribe\b|\/snip(\/|$)/.test(blob)) return 'unscribe';
  if (/allowance|\/pal(\/|$)|#pal\b/.test(blob)) return 'pal';
  return 'unknown';
}

function currentPage() {
  return (location.pathname + location.search + location.hash).slice(0, 200);
}

/** Conversion the dashboard can mark as the funnel success event. */
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
    analytics.trackEvent('store_click', {
      store: store,
      app: appFromContext(href),
      page: currentPage(),
      href: href.slice(0, 200),
    });
  },
  true
);

/**
 * Home SPA (#products / #pbj / …) does not load a new document, so autocapture
 * only sees "/". Emit a named step HeyCatch funnels can use per app section.
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
  else if (raw === 'pal') app = 'pal';
  else return;
  lastProductSection = raw;
  analytics.trackEvent('product_section', { app: app, page: currentPage() });
}
window.addEventListener('hashchange', trackProductSection);
if (document.readyState === 'loading') {
  document.addEventListener('DOMContentLoaded', trackProductSection);
} else {
  trackProductSection();
}
