/**
 * Optional free SaaS analytics for josspatech.com.
 * Configured via window.JOSSPATECH_ANALYTICS on each page.
 * First-party visits still go to PocketBase _site_visits (index tracker).
 */
(function () {
  var cfg = window.JOSSPATECH_ANALYTICS || {};
  try {
    if (cfg.goatcounter && typeof cfg.goatcounter === 'string') {
      window.goatcounter = { path: location.pathname + location.search + location.hash };
      var g = document.createElement('script');
      g.async = true;
      g.dataset.goatcounter = cfg.goatcounter;
      g.src = '//gc.zgo.at/count.js';
      document.head.appendChild(g);
    }
  } catch (e) {}
  try {
    if (cfg.cloudflareToken && typeof cfg.cloudflareToken === 'string') {
      var c = document.createElement('script');
      c.defer = true;
      c.src = 'https://static.cloudflareinsights.com/beacon.min.js';
      c.setAttribute('data-cf-beacon', JSON.stringify({ token: cfg.cloudflareToken }));
      document.head.appendChild(c);
    }
  } catch (e) {}
})();
