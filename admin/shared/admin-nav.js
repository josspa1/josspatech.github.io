/* Injected top nav — loaded on every admin page */
(function () {
  const NAV = [
    { href: "index.html", page: "hub", label: "Control Center" },
    { href: "workers.html", page: "workers", label: "Workers" },
    { href: "referrals.html", page: "referrals", label: "Referrals" },
    { href: "dealer-ads.html", page: "dealer-ads", label: "HHH Ads" },
    { href: "cvc-dealer-ads.html", page: "cvc-dealer-ads", label: "CVC Ads" },
    { href: "traffic.html", page: "traffic", label: "Website" },
    { href: "funnels.html", page: "funnels", label: "Funnels" },
    { href: "screens.html", page: "screens", label: "Screens" },
    { href: "ocr-quota.html", page: "ocr", label: "OCR" },
    { href: "flywheel.html", page: "flywheel", label: "Flywheel" },
    { href: "/stocks/", page: "stocks", label: "Stocks" },
  ];

  const APP_NAV = [
    { href: "app-pbj.html", page: "app-pbj", label: "PBJ" },
    { href: "app-hhh.html", page: "app-hhh", label: "HHH" },
    { href: "app-cvc.html", page: "app-cvc", label: "CVC" },
    { href: "app-pal.html", page: "app-pal", label: "PAL" },
  ];

  function isAppPage(page) {
    return APP_NAV.some((a) => a.page === page);
  }

  window.injectAdminNav = function injectAdminNav() {
    const dash = document.getElementById("dashboard");
    if (!dash) return;
    const page = window.ADMIN_PAGE || "hub";
    let nav = document.getElementById("adminTopNav");
    if (!nav) {
      nav = document.createElement("nav");
      nav.id = "adminTopNav";
      nav.className = "admin-topnav";
      nav.setAttribute("aria-label", "Jump to any admin page");
      // Pin at the very top so hop links are always visible after login.
      dash.prepend(nav);
    }

    const mainLinks = NAV.map(
      (n) => `<a href="${n.href}" class="${n.page === page ? "active" : ""}">${n.label}</a>`,
    ).join("");

    const appLinks = APP_NAV.map(
      (a) => `<a href="${a.href}" class="admin-app-link ${a.page === page ? "active" : ""}">${a.label}</a>`,
    ).join("");

    nav.innerHTML =
      `<span class="admin-nav-jump-label">Jump to</span>` +
      mainLinks +
      `
      <span class="admin-nav-divider" aria-hidden="true"></span>
      <span class="admin-nav-apps-label">Apps</span>
      <span class="admin-nav-apps">${appLinks}</span>`;

    nav.classList.toggle("admin-topnav--app-active", isAppPage(page));

    injectAdminFooter(dash);
  };

  function injectAdminFooter(dash) {
    if (document.getElementById("adminFooter")) return;
    const footer = document.createElement("footer");
    footer.id = "adminFooter";
    footer.className = "admin-footer";
    footer.innerHTML = `
      <a href="DASHBOARD_QUOTA.md" target="_blank" rel="noopener noreferrer">Dashboard quota &amp; refresh rules</a>
      <span class="admin-footer-sep" aria-hidden="true">·</span>
      <span class="admin-footer-note">Manual refresh only · static JSON panels · no Worker polling on load</span>`;
    dash.appendChild(footer);
  }
})();
