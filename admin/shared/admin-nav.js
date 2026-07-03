/* Injected top nav — loaded on every admin page */
(function () {
  const NAV = [
    { href: "index.html", page: "hub", label: "Control Center" },
    { href: "workers.html", page: "workers", label: "Workers" },
    { href: "referrals.html", page: "referrals", label: "Referrals" },
    { href: "ocr-quota.html", page: "ocr", label: "OCR" },
    { href: "flywheel.html", page: "flywheel", label: "Flywheel" },
  ];

  window.injectAdminNav = function injectAdminNav() {
    const dash = document.getElementById("dashboard");
    if (!dash || document.getElementById("adminTopNav")) return;
    const page = window.ADMIN_PAGE || "hub";
    const nav = document.createElement("nav");
    nav.id = "adminTopNav";
    nav.className = "admin-topnav";
    nav.setAttribute("aria-label", "Admin sections");
    nav.innerHTML = NAV.map(
      (n) => `<a href="${n.href}" class="${n.page === page ? "active" : ""}">${n.label}</a>`,
    ).join("");
    const header = dash.querySelector("header");
    if (header && header.nextSibling) {
      dash.insertBefore(nav, header.nextSibling);
    } else {
      dash.prepend(nav);
    }
  };
})();
