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
 *   - Cloudflare Web Analytics (path without hash by CF default; first load only)
 *   - PocketBase _site_visits (same path string; also fires on hashchange)
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

  function postPocketBaseVisit() {
    if (cfg.pocketbase === false) return;
    try {
      var PB = cfg.pbUrl || DEFAULTS.pbUrl;
      var VISIT_COL = cfg.visitCollection || DEFAULTS.visitCollection;
      var sid = sessionStorage.getItem('pbj_visit_sid');
      if (!sid) {
        sid = Math.random().toString(36).slice(2, 10) + Date.now().toString(36);
        sessionStorage.setItem('pbj_visit_sid', sid);
      }
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
      var page = fullPath();
      var utmTag = [utmSource, utmMedium, utmCampaign].filter(Boolean).join('|').slice(0, 200);
      fetch(PB + '/api/collections/' + VISIT_COL + '/records', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          page: page,
          referrer_host: refHost.slice(0, 120),
          referrer_raw: (utmTag ? 'utm:' + utmTag + ' | ' : '') + ref.slice(0, 400),
          user_agent: (navigator.userAgent || '').slice(0, 300),
          session_id: sid,
          source: source,
        }),
        keepalive: true,
      }).catch(function () {});
    } catch (e) {}
  }

  function countGoat(path) {
    var p = path || fullPath();
    function tryCount() {
      try {
        if (window.goatcounter && typeof window.goatcounter.count === 'function') {
          window.goatcounter.count({ path: p });
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
