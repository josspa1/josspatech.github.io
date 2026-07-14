/* Injected top nav — loaded on every admin page */
(function () {
  const NAV = [
    { href: "index.html", page: "hub", label: "Control Center" },
    { href: "workers.html", page: "workers", label: "Workers" },
    { href: "referrals.html", page: "referrals", label: "Referrals" },
    { href: "traffic.html", page: "traffic", label: "Traffic" },
    { href: "ocr-quota.html", page: "ocr", label: "OCR" },
    { href: "flywheel.html", page: "flywheel", label: "Flywheel" },
  ];

  const APP_NAV = [
    { href: "app-pbj.html", page: "app-pbj", label: "PBJ" },
    { href: "app-hhh.html", page: "app-hhh", label: "HHH" },
    { href: "app-cvc.html", page: "app-cvc", label: "CVC" },
  ];

  function isAppPage(page) {
    return APP_NAV.some((a) => a.page === page);
  }

  window.injectAdminNav = function injectAdminNav() {
    const dash = document.getElementById("dashboard");
    if (!dash || document.getElementById("adminTopNav")) return;
    const page = window.ADMIN_PAGE || "hub";
    const nav = document.createElement("nav");
    nav.id = "adminTopNav";
    nav.className = "admin-topnav";
    nav.setAttribute("aria-label", "Admin sections");

    const mainLinks = NAV.map(
      (n) => `<a href="${n.href}" class="${n.page === page ? "active" : ""}">${n.label}</a>`,
    ).join("");

    const appLinks = APP_NAV.map(
      (a) => `<a href="${a.href}" class="admin-app-link ${a.page === page ? "active" : ""}">${a.label}</a>`,
    ).join("");

    nav.innerHTML = mainLinks + `
      <span class="admin-nav-divider" aria-hidden="true"></span>
      <span class="admin-nav-apps-label">Apps</span>
      <span class="admin-nav-apps">${appLinks}</span>`;

    if (isAppPage(page)) nav.classList.add("admin-topnav--app-active");

    const header = dash.querySelector("header");
    if (header && header.nextSibling) {
      dash.insertBefore(nav, header.nextSibling);
    } else {
      dash.prepend(nav);
    }

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
