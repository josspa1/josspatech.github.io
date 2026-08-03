/**
 * Site analytics for josspatech.com (GitHub Pages).
 *
 * Include on any public HTML page:
 *   <script src="/scripts/site-analytics-saas.js" defer></script>
 *
 * Optional override before this script:
 *   window.JOSSPATECH_ANALYTICS = { goatcounter, cloudflareToken, pocketbase: true|false }
 *
 * Records:
 *   - GoatCounter path = pathname + search + hash (UTMs + #hhh / #pbj / #cvc)
 *   - GoatCounter events for store outbound clicks (Play / TestFlight / App Store)
 *   - Cloudflare Web Analytics (path without hash by CF default; first load only)
 *   - PocketBase _site_visits (pageviews + outbound:* rows)
 *
 * GoatCounter: open dashboard → Paths for landings; Events for store clicks
 *   (outbound-play-hhh, outbound-testflight-hhh, outbound-play-pbj, …).
 * Event paths must not start with "/".
 */
(function () {
  if (window.__JOSSPATECH_ANALYTICS_BOOTED) return;
  window.__JOSSPATECH_ANALYTICS_BOOTED = true;

  var DEFAULTS = {
    goatcounter: 'https://josspatech.goatcounter.com/count',
    cloudflareToken: 'c09b026e6da640a981afc2f3c5a470fd',
    pocketbase: true,
    pbUrl: 'https://josspatech.pockethost.io',
    visitCollection: '_site_visits',
  };

  var cfg = Object.assign({}, DEFAULTS, window.JOSSPATECH_ANALYTICS || {});

  function fullPath() {
    return (location.pathname + location.search + location.hash).slice(0, 400);
  }

  function visitSourceMeta() {
    var params = new URLSearchParams(location.search || '');
    var utmSource = (params.get('utm_source') || '').slice(0, 80);
    var utmMedium = (params.get('utm_medium') || '').slice(0, 80);
    var utmCampaign = (params.get('utm_campaign') || '').slice(0, 80);
    var ref = document.referrer || '';
    var refHost = '';
    try {
      refHost = ref ? new URL(ref).hostname : '';
    } catch (e) {}
    var source;
    if (utmSource) {
      source = (/clockworks/i.test(utmSource) ? 'clockworks' : utmSource).slice(0, 40);
    } else if (!refHost) source = 'direct';
    else if (refHost === location.hostname) source = 'internal';
    else if (/google|bing|duckduckgo|yahoo|ecosia|brave\.com|search\.|startpage/i.test(refHost))
      source = 'search';
    else if (
      /facebook|twitter|x\.com|instagram|linkedin|reddit|youtube|tiktok|pinterest|mastodon|threads/i.test(
        refHost
      )
    )
      source = 'social';
    else source = 'external';
    var utmTag = [utmSource, utmMedium, utmCampaign].filter(Boolean).join('|').slice(0, 200);
    return { source: source, refHost: refHost, ref: ref, utmTag: utmTag };
  }

  function sessionId() {
    var sid = sessionStorage.getItem('pbj_visit_sid');
    if (!sid) {
      sid = Math.random().toString(36).slice(2, 10) + Date.now().toString(36);
      sessionStorage.setItem('pbj_visit_sid', sid);
    }
    return sid;
  }

  function postPocketBase(page, extraRef) {
    if (cfg.pocketbase === false) return;
    try {
      var PB = cfg.pbUrl || DEFAULTS.pbUrl;
      var VISIT_COL = cfg.visitCollection || DEFAULTS.visitCollection;
      var meta = visitSourceMeta();
      var refRaw =
        (meta.utmTag ? 'utm:' + meta.utmTag + ' | ' : '') +
        (extraRef ? extraRef + ' | ' : '') +
        meta.ref;
      var body = JSON.stringify({
        page: String(page || fullPath()).slice(0, 400),
        referrer_host: meta.refHost.slice(0, 120),
        referrer_raw: refRaw.slice(0, 500),
        user_agent: (navigator.userAgent || '').slice(0, 300),
        session_id: sessionId(),
        source: meta.source,
      });
      var url = PB + '/api/collections/' + VISIT_COL + '/records';
      // sendBeacon first for store clicks / tab switches — fetch keepalive still fails often on mobile
      if (navigator.sendBeacon) {
        try {
          var ok = navigator.sendBeacon(url, new Blob([body], { type: 'application/json' }));
          if (ok) return;
        } catch (e) {}
      }
      fetch(url, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: body,
        keepalive: true,
      }).catch(function () {});
    } catch (e) {}
  }

  function postPocketBaseVisit() {
    postPocketBase(fullPath());
  }

  function countGoat(path, opts) {
    var p = path || fullPath();
    var o = opts || {};
    function tryCount() {
      try {
        if (window.goatcounter && typeof window.goatcounter.count === 'function') {
          var payload = { path: p };
          if (o.title) payload.title = o.title;
          if (o.event) payload.event = true;
          if (o.no_session) payload.no_session = true;
          window.goatcounter.count(payload);
          return true;
        }
      } catch (e) {}
      return false;
    }
    if (tryCount()) return;
    var n = 0;
    var t = setInterval(function () {
      if (tryCount() || ++n > 40) clearInterval(t);
    }, 50);
  }

  /** Map store URLs → GoatCounter event name (no leading slash). */
  function classifyStoreHref(href) {
    try {
      var u = new URL(href, location.href);
      var host = (u.hostname || '').toLowerCase();
      var path = (u.pathname || '') + (u.search || '');
      if (host === 'play.google.com' || host.endsWith('.play.google.com')) {
        if (/handyhorology/i.test(path) || /handyhorology/i.test(u.href)) {
          return { event: 'outbound-play-hhh', title: 'Play Store · HHH' };
        }
        if (/pocketbudjet/i.test(path) || /pocketbudjet/i.test(u.href)) {
          return { event: 'outbound-play-pbj', title: 'Play Store · PBJ' };
        }
        return { event: 'outbound-play', title: 'Play Store' };
      }
      if (host === 'testflight.apple.com') {
        return { event: 'outbound-testflight-hhh', title: 'TestFlight · HHH' };
      }
      if (host === 'apps.apple.com') {
        if (/handyhorology|6778570480|handy-horology/i.test(u.href)) {
          return { event: 'outbound-appstore-hhh', title: 'App Store · HHH' };
        }
        if (/pocketbudjet|pocket-budjet/i.test(u.href)) {
          return { event: 'outbound-appstore-pbj', title: 'App Store · PBJ' };
        }
        return { event: 'outbound-appstore', title: 'App Store' };
      }
    } catch (e) {}
    return null;
  }

  var _lastStoreTrack = { href: '', t: 0 };

  function trackStoreOutbound(info, href) {
    var now = Date.now();
    // Dedupe pointerdown + click on the same badge
    if (_lastStoreTrack.href === href && now - _lastStoreTrack.t < 1500) return;
    _lastStoreTrack = { href: href, t: now };
    // GoatCounter Events tab (event:true — path is the event name)
    countGoat(info.event, { title: info.title, event: true, no_session: true });
    // PocketBase: filter page startsWith outbound:
    postPocketBase('outbound:' + info.event, 'href:' + String(href || '').slice(0, 200) + ' | from:' + fullPath());
  }

  function onStoreLinkIntent(e) {
    if (e.defaultPrevented) return;
    if (e.type === 'click' && e.button != null && e.button !== 0) return;
    if (e.metaKey || e.ctrlKey || e.shiftKey || e.altKey) return;
    var el = e.target;
    if (!el || !el.closest) return;
    var a = el.closest('a[href]');
    if (!a || !a.href) return;
    var info = classifyStoreHref(a.href);
    if (!info) return;
    trackStoreOutbound(info, a.href);
  }

  // pointerdown fires before navigation; click covers keyboard activation
  document.addEventListener('pointerdown', onStoreLinkIntent, true);
  document.addEventListener('click', onStoreLinkIntent, true);

  // GoatCounter: include hash so /#hhh and /?utm…#hhh are distinct paths
  try {
    if (cfg.goatcounter && typeof cfg.goatcounter === 'string') {
      window.goatcounter = window.goatcounter || {};
      window.goatcounter.path = fullPath();
      var g = document.createElement('script');
      g.async = true;
      g.dataset.goatcounter = cfg.goatcounter;
      g.src = '//gc.zgo.at/count.js';
      document.head.appendChild(g);
    }
  } catch (e) {}

  // Cloudflare Web Analytics (first paint / full navigation only — no hash SPA API)
  try {
    if (cfg.cloudflareToken && typeof cfg.cloudflareToken === 'string') {
      var c = document.createElement('script');
      c.defer = true;
      c.src = 'https://static.cloudflareinsights.com/beacon.min.js';
      c.setAttribute('data-cf-beacon', JSON.stringify({ token: cfg.cloudflareToken }));
      document.head.appendChild(c);
    }
  } catch (e) {}

  postPocketBaseVisit();

  // In-page product switches (#hhh / #pbj / #cvc) — GoatCounter + PocketBase only
  var lastHashPath = fullPath();
  window.addEventListener('hashchange', function () {
    var next = fullPath();
    if (next === lastHashPath) return;
    lastHashPath = next;
    countGoat(next);
    postPocketBaseVisit();
  });
})();
