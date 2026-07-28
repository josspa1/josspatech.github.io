/**
 * Shared JosspaTech chrome for standalone manuals / how-to pages.
 * Ensures: header product links, hierarchy breadcrumbs, product footer.
 *
 * <body data-jt-product="hhh|pbj|pal|cvc">
 * <link rel="stylesheet" href="/videos/shared/site-chrome.css">
 * <script src="/videos/shared/site-chrome.js" defer></script>
 */
(function () {
  if (document.documentElement.classList.contains('embed-mode')) return;
  if (new URLSearchParams(location.search).get('embed') === '1') return;
  if (/[?&]record=1/.test(location.search)) return;

  var PRODUCTS = [
    { id: 'home', href: '/', label: 'Home' },
    { id: 'pbj', href: '/#pbj', label: 'PocketBudJet' },
    { id: 'hhh', href: '/#hhh', label: 'Handy Horology Helper' },
    { id: 'pal', href: '/#pal', label: 'Pocket Allowance Ledger' },
    { id: 'cvc', href: '/#cvc', label: "Curator's Vault" }
  ];

  var FOOTER_PRODUCTS = [
    { href: '/', label: 'Home' },
    { href: '/#pbj', label: 'PocketBudJet' },
    { href: '/#hhh', label: 'Handy Horology Helper' },
    { href: '/#pal', label: 'Pocket Allowance Ledger' },
    { href: '/#cvc', label: "Curator's Vault: Classics" }
  ];

  var product = (document.body && document.body.getAttribute('data-jt-product')) || '';
  if (!product) {
    if (/user-guide-hhh/.test(location.pathname)) product = 'hhh';
    else if (/user-guide/.test(location.pathname)) product = 'pbj';
  }
  if (product && document.body) document.body.setAttribute('data-jt-product', product);

  var productMeta = {
    hhh: { href: '/#hhh', label: 'Handy Horology Helper' },
    pbj: { href: '/#pbj', label: 'PocketBudJet' },
    pal: { href: '/#pal', label: 'Pocket Allowance Ledger' },
    cvc: { href: '/#cvc', label: "Curator's Vault" }
  };

  function ensureStylesheet() {
    if (document.querySelector('link[href*="site-chrome.css"]')) return;
    var link = document.createElement('link');
    link.rel = 'stylesheet';
    link.href = '/videos/shared/site-chrome.css?v=chrome-2026-07-28';
    document.head.appendChild(link);
  }

  function ensureHeaderNav() {
    var nav = document.querySelector('nav');
    if (!nav) return;
    var list = nav.querySelector('.nav-links');
    if (!list) {
      list = document.createElement('ul');
      list.className = 'nav-links';
      var container = nav.querySelector('.container') || nav;
      container.appendChild(list);
    }
    // Ensure Home + every product are present (keep page-specific extras like PDF / How To)
    PRODUCTS.forEach(function (p) {
      var exists = Array.prototype.some.call(list.querySelectorAll('a'), function (a) {
        var href = a.getAttribute('href') || '';
        if (p.id === 'home') return href === '/' || href === '/index.html';
        return href.indexOf(p.href) !== -1 || href === p.href;
      });
      if (exists) return;
      var li = document.createElement('li');
      var a = document.createElement('a');
      a.href = p.href;
      a.textContent = p.label;
      li.appendChild(a);
      // Insert products before trailing utility links (PDF / How To)
      list.appendChild(li);
    });
  }

  function ensureBreadcrumbs() {
    var existing = document.querySelector('.breadcrumbs');
    var meta = productMeta[product];
    if (!meta) return;

    var html =
      '<a href="/">Home</a><span class="sep">/</span>' +
      '<a href="' + meta.href + '">' + meta.label + '</a><span class="sep">/</span>' +
      '<span class="current">User Manual</span>';

    if (existing) {
      // Normalize to Home / Product / User Manual if empty or broken
      if (!existing.querySelector('a[href="/"]') || !existing.querySelector('a[href*="' + meta.href + '"]')) {
        existing.innerHTML = html;
      }
      return;
    }

    var crumbs = document.createElement('div');
    crumbs.className = 'breadcrumbs';
    crumbs.setAttribute('aria-label', 'Breadcrumb');
    crumbs.innerHTML = html;
    var nav = document.querySelector('nav');
    if (nav && nav.parentNode) {
      nav.parentNode.insertBefore(crumbs, nav.nextSibling);
    } else if (document.body) {
      document.body.insertBefore(crumbs, document.body.firstChild);
    }
  }

  function ensureFooter() {
    var footer = document.querySelector('.jt-site-footer');
    var productsHtml = FOOTER_PRODUCTS.map(function (p) {
      return '<li><a href="' + p.href + '">' + p.label + '</a></li>';
    }).join('');

    if (!footer) {
      footer = document.createElement('footer');
      footer.className = 'jt-site-footer';
      footer.innerHTML =
        '<ul class="jt-products" aria-label="JosspaTech products">' + productsHtml + '</ul>' +
        '<p class="jt-copy">&copy; 2026 JosspaTech. All Rights Reserved.</p>' +
        '<p class="jt-legal"><a href="mailto:support@josspatech.com">support@josspatech.com</a></p>';
      document.body.appendChild(footer);
      return;
    }

    var ul = footer.querySelector('.jt-products');
    if (!ul) {
      ul = document.createElement('ul');
      ul.className = 'jt-products';
      ul.setAttribute('aria-label', 'JosspaTech products');
      footer.insertBefore(ul, footer.firstChild);
    }
    // Refresh product links so Home + all products always present
    ul.innerHTML = productsHtml;
  }

  function run() {
    ensureStylesheet();
    ensureHeaderNav();
    ensureBreadcrumbs();
    ensureFooter();
  }

  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', run);
  } else {
    run();
  }
})();
