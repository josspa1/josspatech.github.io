/**
 * Shared footer + product links for standalone JosspaTech pages.
 * Include after page body content: <script src="/videos/shared/site-chrome.js" defer></script>
 * Optional: set data-jt-product on <body> to "pbj" | "hhh" | "pal" | "cvc" for breadcrumb hints.
 */
(function () {
  if (document.documentElement.classList.contains('embed-mode')) return;
  if (new URLSearchParams(location.search).get('embed') === '1') return;
  if (document.body && document.body.classList.contains('record-mode')) return;
  if (document.querySelector('.jt-site-footer')) return;

  var link = document.createElement('link');
  link.rel = 'stylesheet';
  link.href = '/videos/shared/site-chrome.css';
  document.head.appendChild(link);

  var footer = document.createElement('footer');
  footer.className = 'jt-site-footer';
  footer.innerHTML =
    '<ul class="jt-products" aria-label="JosspaTech products">' +
    '<li><a href="/">Home</a></li>' +
    '<li><a href="/#pbj">PocketBudJet</a></li>' +
    '<li><a href="/#hhh">Handy Horology Helper</a></li>' +
    '<li><a href="/#pal">Pocket Allowance Ledger</a></li>' +
    '<li><a href="/#cvc">Curator\'s Vault: Classics</a></li>' +
    '</ul>' +
    '<p class="jt-copy">&copy; 2026 JosspaTech. All Rights Reserved.</p>' +
    '<p class="jt-legal"><a href="mailto:support@josspatech.com">support@josspatech.com</a></p>';
  document.body.appendChild(footer);
})();
