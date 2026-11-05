/**
 * HeyCatch for josspatech.com (static marketing site).
 * https://heycatch.ai/agents.md — pin the latest stable SDK (no -dev).
 *
 * Each public page loads this from <head>:
 *   <script type="module" src="/scripts/heycatch-init.js?v=3"></script>
 * Do not inject it after load. A deferred inject misses the landing pageview
 * on mobile, which is how TikTok visits showed sessions and zero pageviews.
 *
 * site: 'landing' keeps these visits apart from the phone apps.
 * requestBatching: false — full page loads; mobile Safari drops a batched beacon.
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

function appFromContext(href) {
  var path = (location.pathname || '').toLowerCase();
  var blob = (href + ' ' + path).toLowerCase();
  if (/pocketbudjet|\/pbj(\/|$)/.test(blob)) return 'pbj';
  if (/handyhorology|\/hhh(\/|$)/.test(blob)) return 'hhh';
  if (/curator|\/cvc(\/|$)|josspatech\.cts|\/cts(\/|$)/.test(blob)) return 'cvc';
  if (/unscribe|\/snip(\/|$)|josspatech\.snip/.test(blob)) return 'unscribe';
  if (/allowance|\/pal(\/|$)/.test(blob)) return 'pal';
  return 'unknown';
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
      href: href.slice(0, 200),
    });
  },
  true
);
