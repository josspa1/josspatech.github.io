// ========================================================
  // PocketBudJet Flywheel Dashboard
  // © 2026 JosspaTech. All Rights Reserved.
  //
  // Single-file HTML dashboard that reads the PocketBase
  // admin API for everything you care about: submission queue
  // depth, canonical library growth, anomalies, quarantine,
  // market-intelligence freshness.
  //
  // Deploy options:
  //   1. Double-click this file to open locally.
  //   2. FTP to ftp.pockethost.io/josspatech/pb_public/
  //      then visit https://josspatech.pockethost.io/dashboard.html
  //   3. Bookmark the file:// URL in any browser.
  // ========================================================

  const PB_URL = "https://josspatech.pockethost.io";
  const GITHUB_REPO = "josspa1/josspatech.github.io";
  const FETCH_TIMEOUT_MS = 12000; // per-request ceiling
  const GITHUB_CACHE_TTL_MS = 5 * 60 * 1000; // poll GitHub at most every 5 min
  const ADMIN_CACHE_KEYS = {
    wm: "pbj_dash_cache_wm",
    ocr: "pbj_dash_cache_ocr",
    ref: "pbj_dash_cache_ref",
  };

  function adminCacheRead(slot) {
    try {
      const raw = sessionStorage.getItem(ADMIN_CACHE_KEYS[slot]);
      return raw ? JSON.parse(raw) : null;
    } catch {
      return null;
    }
  }

  function adminCacheWrite(slot, data) {
    try {
      if (data == null) sessionStorage.removeItem(ADMIN_CACHE_KEYS[slot]);
      else sessionStorage.setItem(ADMIN_CACHE_KEYS[slot], JSON.stringify(data));
    } catch { /* quota / private mode */ }
  }

  /** Per-app page id (pbj | hhh | cvc) when ADMIN_PAGE is app-* */
  function adminGetApp() {
    const p = window.ADMIN_PAGE || "";
    if (p.startsWith("app-")) return p.slice(4);
    return window.ADMIN_APP || null;
  }

  function persistWmCache() { adminCacheWrite("wm", wmCache); }
  function persistOcrQuotaCache() { adminCacheWrite("ocr", ocrQuotaCache); }

  let   token  = sessionStorage.getItem("pbj_dash_token") || null;
  let   tick   = null;
  let   intervalSec = 0;  // PocketBase grid — manual by default (auto uses PB /api only, not Worker KV)
  let   logTailTick = null;
  let   wmCache = adminCacheRead("wm");       // { results, tier, costHistoryLoaded, fetchedAt }
  let   wmAutoTick = null;
  let   ocrQuotaCache = adminCacheRead("ocr"); // { data, costHistoryLoaded, fetchedAt }
  let   maintenanceFlag = null;  // last known state of _app_config.maintenance_mode
  let   prevCounts  = {};
  let   githubCache = null;      // { sizeKB, pushedAt, fetchedAt }

  // Abortable fetch with timeout — prevents one stuck request from
  // freezing the whole refresh.
  function timedFetch(url, opts) {
    const ctl = new AbortController();
    const t = setTimeout(() => ctl.abort(), FETCH_TIMEOUT_MS);
    return fetch(url, { ...(opts || {}), signal: ctl.signal })
      .finally(() => clearTimeout(t));
  }

  // ─── Auth ──────────────────────────────────────────────
  async function doLogin() {
    const email    = document.getElementById("email").value.trim();
    const password = document.getElementById("password").value;
    const err      = document.getElementById("loginErr");
    err.style.display = "none";
    try {
      // Try 0.23+ superusers endpoint first.
      let res = await fetch(`${PB_URL}/api/collections/_superusers/auth-with-password`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ identity: email, password }),
      });
      if (!res.ok) {
        // Fallback for older PocketBase.
        res = await fetch(`${PB_URL}/api/admins/auth-with-password`, {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({ identity: email, password }),
        });
      }
      if (!res.ok) { throw new Error(`Auth failed (${res.status})`); }
      const data = await res.json();
      token = data.token;
      sessionStorage.setItem("pbj_dash_token", token);
      showDashboard();
    } catch (e) {
      err.textContent = e.message || "Login failed.";
      err.style.display = "block";
    }
  }

  function doLogout() {
    sessionStorage.removeItem("pbj_dash_token");
    token = null;
    if (tick) clearInterval(tick);
    document.getElementById("dashboard").style.display = "none";
    document.getElementById("login").style.display = "block";
  }

  function setRefresh() {
    const autoEl = document.getElementById("pbAutoRefresh");
    const selEl = document.getElementById("refreshInterval");
    const autoOn = autoEl && autoEl.checked;
    if (selEl) selEl.disabled = !autoOn;
    intervalSec = autoOn ? parseInt(selEl?.value || "600", 10) : 0;
    if (tick) clearInterval(tick);
    tick = null;
    if (intervalSec > 0) {
      tick = setInterval(refresh, intervalSec * 1000);
      document.getElementById("pulse").classList.remove("stale");
    } else {
      document.getElementById("pulse").classList.add("stale");
    }
  }

  // ─── Fetch helpers ─────────────────────────────────────
  async function pbCount(collection, filter) {
    try {
      const f = filter ? `&filter=${encodeURIComponent(filter)}` : "";
      const res = await timedFetch(
        `${PB_URL}/api/collections/${collection}/records?perPage=1&fields=id${f}`,
        { headers: { Authorization: `Bearer ${token}` } },
      );
      if (res.status === 401) { doLogout(); throw new Error("Session expired"); }
      if (!res.ok) return null;
      const data = await res.json();
      return data.totalItems ?? null;
    } catch (e) {
      if (e && e.message === "Session expired") throw e;
      return null; // timeout / network — render as "—" but keep going
    }
  }

  async function pbList(collection, filter, sort, limit) {
    try {
      const params = new URLSearchParams({
        perPage: String(limit || 10),
        ...(sort   ? { sort }   : {}),
        ...(filter ? { filter } : {}),
      });
      const res = await timedFetch(
        `${PB_URL}/api/collections/${collection}/records?${params}`,
        { headers: { Authorization: `Bearer ${token}` } },
      );
      if (!res.ok) return [];
      const data = await res.json();
      return data.items || [];
    } catch {
      return [];
    }
  }

  // ─── Section headers in the live PocketBase grid ───────
  function sectionHeader(title, explainer) {
    const sub = explainer
      ? `<p class="section-header-sub section-explainer">${explainer}</p>`
      : "";
    return `<div class="section-header">${title}</div>${sub}`;
  }

  // ─── Card rendering ────────────────────────────────────
  // card(label, description, value, sub, state)
  //   label       — short title (e.g. "Merchant queue")
  //   description — 1-sentence explanation of what the number represents
  //   value       — the big number / string
  //   sub         — footnote (thresholds, context)
  //   state       — 'ok' | 'warn' | 'crit' (drives left border color)
  function card(label, description, value, sub, state) {
    const small = typeof value === "string" && value.length > 10;
    return `
      <div class="card ${state || ''}">
        <div class="label">${label}</div>
        ${description ? `<div class="description">${description}</div>` : ''}
        <div class="value ${small ? 'small' : ''}">${value ?? "—"}</div>
        ${sub ? `<div class="sub">${sub}</div>` : ''}
      </div>`;
  }

  function queueCard(label, description, collection, unprocessed, total, thresholdsNote) {
    const prev   = prevCounts[collection];
    const deltaN = prev != null ? (unprocessed - prev) : null;
    const state  = unprocessed > 500 ? "crit"
                 : unprocessed > 100 ? "warn"
                 : "ok";
    const dir = deltaN == null ? ""
              : deltaN > 0 ? `<span class="delta up">+${deltaN} since last poll</span>`
              : deltaN < 0 ? `<span class="delta down">${deltaN} drained since last poll</span>`
              : `no change since last poll`;
    prevCounts[collection] = unprocessed;
    const subParts = [
      `${total ?? "?"} submitted all-time`,
      dir,
      thresholdsNote,
    ].filter(Boolean);
    return card(
      label,
      description,
      unprocessed ?? "—",
      subParts.join(" · "),
      state,
    );
  }

  function relTime(iso) {
    if (!iso) return "—";
    const t = Date.parse(iso);
    if (Number.isNaN(t)) return iso;
    const diff = (Date.now() - t) / 1000;
    if (diff < 60)        return Math.floor(diff) + "s ago";
    if (diff < 3600)      return Math.floor(diff / 60) + "m ago";
    if (diff < 86400)     return Math.floor(diff / 3600) + "h ago";
    return Math.floor(diff / 86400) + "d ago";
  }

  // ─── Refresh loop ──────────────────────────────────────
  async function refresh() {
    const grid  = document.getElementById("grid");
    const parts = [];

    // Show immediate "loading" so the user isn't staring at an empty page
    // while ~30 fetches stream in. Replaced as real data lands.
    grid.innerHTML = `
      <div class="section-header">Loading live data from PocketBase…</div>
      <div class="card"><div class="label">Connecting</div>
        <div class="value small">Fetching ${'\u00B7'.repeat(3)}</div>
        <div class="sub">First page takes ~10 seconds cold.</div>
      </div>`;
    const paint = () => { grid.innerHTML = parts.join(""); };

    try {
      // === SECTION: FLYWHEEL HEALTH ===
      parts.push(sectionHeader(
        "Flywheel Health",
        "PBJ crowd-data ingestion. Each card's big number is <strong>unprocessed queue depth</strong> or <strong>last cron run</strong>. Queues should drain hourly when PocketBase <code>pb_hooks</code> run. Rising queues with a stale &ldquo;Last aggregation&rdquo; = cron stalled — see Cron Health below (PBJ only)."
      ));

      const [
        merchUnprocessed, merchTotal,
        paycheckUnprocessed, paycheckTotal,
        billUnprocessed, billTotal,
      ] = await Promise.all([
        pbCount("pbj_merchant_submissions",  "is_stale = false"),
        pbCount("pbj_merchant_submissions",  ""),
        pbCount("pbj_paycheck_submissions",  "is_stale = false"),
        pbCount("pbj_paycheck_submissions",  ""),
        pbCount("pbj_bill_submissions",      "is_stale = false"),
        pbCount("pbj_bill_submissions",      ""),
      ]);

      parts.push(queueCard(
        "Merchant queue",
        "Scanned receipts waiting for the server's hourly aggregation.",
        "pbj_merchant_submissions", merchUnprocessed, merchTotal,
        "Should stay under 100. Over 500 = aggregation isn't running."
      ));
      parts.push(queueCard(
        "Pay-stub queue",
        "Scanned pay stubs waiting for server-side employer canonicalization.",
        "pbj_paycheck_submissions", paycheckUnprocessed, paycheckTotal,
        "Lower volume than receipts. Over 50 = investigate hooks."
      ));
      parts.push(queueCard(
        "Bill queue",
        "Scanned bills waiting for server-side payee canonicalization.",
        "pbj_bill_submissions", billUnprocessed, billTotal,
        "Lower volume. Over 50 = investigate."
      ));

      // Last aggregation run — most recent processed_at across all submissions
      const [mRecent, pRecent, bRecent] = await Promise.all([
        pbList("pbj_merchant_submissions",  "processed_at != ''", "-processed_at", 1),
        pbList("pbj_paycheck_submissions",  "processed_at != ''", "-processed_at", 1),
        pbList("pbj_bill_submissions",      "processed_at != ''", "-processed_at", 1),
      ]);
      const lastProcessed = [mRecent[0], pRecent[0], bRecent[0]]
        .filter(Boolean)
        .map(r => r.processed_at)
        .sort().pop();
      const lastProcAgeH = lastProcessed ? (Date.now() - Date.parse(lastProcessed)) / 3600000 : null;
      const lastProcState = lastProcessed == null ? "info"
                          : lastProcAgeH > 2 ? "warn"
                          : "ok";
      parts.push(card(
        "Last aggregation",
        "When the server-side cron last processed the queues.",
        lastProcessed ? relTime(lastProcessed) : "not yet",
        lastProcessed
          ? `Runs hourly. Under 2h = healthy.`
          : `Expected while pb_hooks isn't deployed — not a worker outage.`,
        lastProcState
      ));
      paint();

      // === SECTION: CANONICAL LIBRARY ===
      parts.push(sectionHeader(
        "Canonical Library · shared across PBJ/HHH/CVC",
        "Consensus entities every app reads. Merchants/employers/payees grow as scans aggregate; alias votes show pending community proposals vs approved links. Steady approved growth = healthy flywheel."
      ));
      const [merchants, employers, payees, aliasesP, aliasesA, aliasesR] = await Promise.all([
        pbCount("shared_entity_library", "entity_type = 'merchant'"),
        pbCount("shared_entity_library", "entity_type = 'employer'"),
        pbCount("shared_entity_library", "entity_type = 'payee'"),
        pbCount("shared_entity_aliases", "status = 'pending'"),
        pbCount("shared_entity_aliases", "status = 'approved'"),
        pbCount("shared_entity_aliases", "status = 'rejected'"),
      ]);
      parts.push(card(
        "Canonical merchants",
        "Unique merchants that consensus has identified across all users. The product of the flywheel.",
        merchants ?? "—",
        "Grows over time as more users scan receipts."
      ));
      parts.push(card(
        "Canonical employers",
        "Unique employers recognized from pay-stub scans.",
        employers ?? "—",
        "Slower growth — users scan fewer pay stubs than receipts."
      ));
      parts.push(card(
        "Canonical payees",
        "Unique bill payees (utilities, insurance, subscriptions) recognized.",
        payees ?? "—",
        "Mid-volume growth."
      ));
      parts.push(card(
        "Alias votes",
        "Raw-name-to-canonical proposals: awaiting votes / confirmed / rejected.",
        `${aliasesP ?? 0} / ${aliasesA ?? 0} / ${aliasesR ?? 0}`,
        "Approved grows steadily. Pending should churn hourly (votes → approved).",
        ((aliasesP ?? 0) > 200) ? "warn" : "ok"
      ));
      paint();

      // === SECTION: DATA POOLS ===
      parts.push(sectionHeader(
        "Aggregate Data Pools · powered by user scans",
        "Derived tables the apps query for insights (categories, benchmarks, OCR corrections). Counts climb with usage — flat lines over weeks may mean low traffic or stalled aggregation upstream."
      ));
      const [merchDat, priceTrnd, spendBench, storeIntel, recur, household, docs, subs] = await Promise.all([
        pbCount("pbj_merchant_data", ""),
        pbCount("pbj_price_trends", ""),
        pbCount("pbj_spending_benchmarks", ""),
        pbCount("pbj_store_intel", ""),
        pbCount("pbj_recurring_patterns", ""),
        pbCount("pbj_household_benchmarks", ""),
        pbCount("pbj_document_patterns", ""),
        pbCount("pbj_subscription_library", ""),
      ]);
      parts.push(card(
        "Merchant data",
        "Crowd-sourced category votes + store-level metrics per merchant.",
        merchDat,
        "Drives category auto-suggest on every new scan."
      ));
      parts.push(card(
        "Price trends",
        "Category×region price averages by period.",
        priceTrnd,
        "Feeds 'you're paying more than average' insights."
      ));
      parts.push(card(
        "Spending benchmarks",
        "How much similar households spend per category each month.",
        spendBench,
        "Powers peer-comparison on the budget screen."
      ));
      parts.push(card(
        "Store intel",
        "Per-location data for specific stores (e.g. Walmart #1042).",
        storeIntel,
        "Unlocks store-level price variance insights."
      ));
      parts.push(card(
        "Recurring patterns",
        "Known recurring-charge cadences across users.",
        recur,
        "Improves subscription detection for new users."
      ));
      parts.push(card(
        "Household benchmarks",
        "Split-ratio data for multi-person households.",
        household,
        "Feeds split-expense suggestions."
      ));
      parts.push(card(
        "OCR correction patterns",
        "What OCR misread vs. what users corrected to. The 98%→99% training loop.",
        docs,
        "Every scan correction adds one row here. Growth = health."
      ));
      parts.push(card(
        "Subscription library",
        "Known subscription services + their typical amounts/frequencies.",
        subs,
        "Seeded by the team; you may not see growth here."
      ));
      paint();

      // === SECTION: PER-APP ACTIVITY (LAST 24H) ===
      parts.push(sectionHeader(
        "Per-App Activity · last 24 hours",
        "Write volume per app since midnight UTC (PocketBase <code>created</code> filter). Best proxy for &ldquo;are people using the apps today?&rdquo; — not the same as install count or paying subs."
      ));

      // Compute the ISO cutoff for "last 24h"
      const dayAgo = new Date(Date.now() - 24 * 3600 * 1000)
        .toISOString()
        .replace('T', ' ')      // PocketBase filter format
        .slice(0, 19);          // YYYY-MM-DD HH:MM:SS
      const dayAgoFilter = `created >= "${dayAgo}"`;

      const [
        pbjToday, hhhTodayMi, cvcTodayMi, aliasesToday, visitsToday,
      ] = await Promise.all([
        pbCount("pbj_merchant_submissions",  dayAgoFilter),
        pbCount("hhh_market_intelligence",   dayAgoFilter),
        pbCount("cts_market_intelligence",   dayAgoFilter),
        pbCount("shared_entity_aliases",     dayAgoFilter),
        pbCount("_site_visits",              dayAgoFilter),
      ]);

      parts.push(card(
        "PBJ writes · 24h",
        "New merchant submissions from PocketBudJet scans today. Closest proxy for daily PBJ user activity.",
        pbjToday ?? 0,
        "Grows with active scanners. 0 = nobody scanned today."
      ));
      parts.push(card(
        "HHH writes · 24h",
        "New watch-market snapshots from Handy Horology Helper today.",
        hhhTodayMi ?? 0,
        "HHH writes when users search or add watches."
      ));
      parts.push(card(
        "CVC writes · 24h",
        "New collectible-market snapshots from Curator's Vault today.",
        cvcTodayMi ?? 0,
        "CVC writes when users search or add items."
      ));
      parts.push(card(
        "Shared alias votes · 24h",
        "New raw-name-to-canonical proposals from all three apps combined.",
        aliasesToday ?? 0,
        "Feeds the canonical entity registry. Grows with total scan volume."
      ));
      paint();

      // === SECTION: CROSS-APP ===
      parts.push(sectionHeader(
        "Cross-App Integration · HHH + CVC",
        "How the three apps share value: collection snapshots, market-intel crawls, and user-linked purchases. Purchase links = a PBJ expense explicitly tied to an HHH watch or CVC item."
      ));
      const [hhhVal, cvcVal, hhhMkt, cvcMkt, links] = await Promise.all([
        pbCount("hhh_collection_values",    ""),
        pbCount("cvc_collection_values",    ""),
        pbCount("hhh_market_intelligence",  ""),
        pbCount("cts_market_intelligence",  ""),
        pbCount("pbj_purchase_links",       ""),
      ]);
      parts.push(card(
        "HHH collection snapshots",
        "Periodic total-value writes from the Handy Horology Helper app.",
        hhhVal,
        "One per HHH user per periodic sync."
      ));
      parts.push(card(
        "CVC collection snapshots",
        "Periodic total-value writes from Curator's Vault.",
        cvcVal,
        "One per CVC user per periodic sync."
      ));
      parts.push(card(
        "HHH market intel",
        "Watch-model price intelligence (asking + sold averages) from HHH's eBay crawler.",
        hhhMkt,
        "PBJ reads this for linked-purchase market values."
      ));
      parts.push(card(
        "CVC market intel",
        "Collectible price intelligence from CVC's crawler (stored as cts_market_intelligence).",
        cvcMkt,
        "Same role as HHH's but for coins/cards/stamps."
      ));
      parts.push(card(
        "Cross-app purchase links",
        "PBJ transactions that the user linked to an HHH watch or CVC item.",
        links,
        "Each = one user consciously connected a purchase to a collectible."
      ));
      paint();

      // === SECTION: CRASH REPORTS (app stability) ===
      parts.push(sectionHeader(
        "App Stability · crash reports",
        "Client-side errors reported to PocketBase <code>_crash_reports</code>. Zero is normal. Spikes after a release → check the list below for platform, screen, and error name."
      ));
      const [crashAll, crash24h, crash7d] = await Promise.all([
        pbCount("_crash_reports", ""),
        pbCount("_crash_reports", dayAgoFilter),
        pbCount("_crash_reports", `created >= "${new Date(Date.now() - 7 * 86400000).toISOString().replace('T', ' ').slice(0, 19)}"`),
      ]);
      parts.push(card(
        "Crashes · 24h",
        "React render errors, unhandled promise rejections, and explicit reportError() calls from the last 24 hours.",
        crash24h ?? 0,
        "Zero is normal. Non-zero = check the recent crashes list below.",
        (crash24h > 0) ? "warn" : "ok"
      ));
      parts.push(card(
        "Crashes · 7 days",
        "Same signal, wider window. Good for spotting regressions after a release.",
        crash7d ?? 0,
        crash7d > crash24h * 7
          ? `Trending up — investigate most common error_name`
          : "Compare against 24h × 7 to judge trend."
      ));
      parts.push(card(
        "Crashes · lifetime",
        "Every crash ever reported. Mostly useful as a total health signal over time.",
        crashAll ?? 0,
        "Archive older resolved crashes from the maintenance panel when this grows past ~10k."
      ));
      paint();

      // Recent crashes list (only render when there are some)
      if (crash7d > 0) {
        const recentCrashes = await pbList("_crash_reports", "", "-created", 10);
        if (recentCrashes.length > 0) {
          parts.push(`
            <div class="list-card">
              <div class="head">
                <span>Recent crashes</span>
                <span>${recentCrashes.length} shown · newest first</span>
              </div>
              <ul>${recentCrashes.map(c => {
                const sev = String(c.action || '').includes('fatal') ? 'high'
                          : String(c.action || '').includes('crash') ? 'medium'
                          : 'low';
                const what = `${c.platform || '?'} ${c.app_version || ''} · ${c.screen || 'unknown screen'}${c.action ? ' · ' + c.action : ''}`;
                const msg = (c.error_name ? c.error_name + ': ' : '') + (c.error_message || '').slice(0, 200);
                return `<li>
                  <span class="sev ${sev}">${sev}</span>
                  <span class="when">${relTime(c.created)}</span>
                  <span class="what">
                    <strong>${what}</strong>
                    <code>${msg.replace(/</g, '&lt;')}</code>
                  </span>
                </li>`;
              }).join('')}</ul>
            </div>`);
        }
      }
      paint();

      // === SECTION: QUALITY & SECURITY ===
      parts.push(sectionHeader(
        "Quality &amp; Security",
        "Anomaly hook flags suspicious crowd patterns; quarantine holds submissions that matched PII regex before they enter consensus. Open anomalies need review; quarantine should stay near zero."
      ));
      const [anomalyUnresolved, anomalyTotal, quarantineCount] = await Promise.all([
        pbCount("_anomaly_log",            "resolved = false"),
        pbCount("_anomaly_log",            ""),
        pbCount("_quarantine_submissions", ""),
      ]);
      parts.push(card(
        "Open anomalies",
        "Category flips, alias storms, or image-dupe floods flagged by the anomaly hook.",
        anomalyUnresolved ?? 0,
        `${anomalyTotal ?? 0} total ever · see list below for details`,
        (anomalyUnresolved > 0) ? "warn" : "ok"
      ));
      parts.push(card(
        "PII quarantine",
        "Submissions that matched PII regex (SSN, card#, etc.) before entering consensus.",
        quarantineCount ?? 0,
        "Blocked from the flywheel. Grows slowly = false positives are rare.",
        (quarantineCount > 10) ? "warn" : "ok"
      ));

      // Full anomaly list
      const anomalies = await pbList("_anomaly_log", "resolved = false", "-detected_at", 10);
      let anomalyRows = "";
      if (anomalies.length === 0) {
        anomalyRows = `<div class="empty ok">No open anomalies — system healthy.</div>`;
      } else {
        anomalyRows = `<ul>${anomalies.map(a => {
          const ctx = a.context_json ? (() => { try { return JSON.stringify(JSON.parse(a.context_json)); } catch { return String(a.context_json); } })() : "";
          return `<li>
            <span class="sev ${a.severity || 'low'}">${a.severity || 'low'}</span>
            <span class="when">${relTime(a.detected_at)}</span>
            <span class="what">
              <strong>${a.anomaly_type || "unknown"}</strong>
              <code>${(ctx || "").slice(0, 240)}</code>
            </span>
          </li>`;
        }).join("")}</ul>`;
      }
      parts.push(`
        <div class="list-card">
          <div class="head">
            <span>Recent anomalies</span>
            <span>${anomalies.length} shown</span>
          </div>
          ${anomalyRows}
        </div>`);

      // Quarantine list
      const quarantined = await pbList("_quarantine_submissions", "", "-flagged_at", 5);
      let quarRows = "";
      if (quarantined.length === 0) {
        quarRows = `<div class="empty ok">No PII matches in recent submissions.</div>`;
      } else {
        quarRows = `<ul>${quarantined.map(q => {
          let kinds = [];
          try { kinds = JSON.parse(q.pii_patterns || "[]"); } catch {}
          return `<li>
            <span class="sev medium">PII</span>
            <span class="when">${relTime(q.flagged_at)}</span>
            <span class="what">
              <strong>${q.origin_collection || "unknown"}</strong>
              <code>patterns: ${kinds.join(", ") || "—"}</code>
            </span>
          </li>`;
        }).join("")}</ul>`;
      }
      parts.push(`
        <div class="list-card">
          <div class="head">
            <span>Recent quarantine</span>
            <span>${quarantined.length} shown (last 5)</span>
          </div>
          ${quarRows}
        </div>`);
      paint();

      // === SECTION: QUOTAS & THRESHOLDS ===
      parts.push(sectionHeader(
        "Quotas &amp; Thresholds",
        "Storage and vendor capacity signals. Record-count estimate is a rough proxy; backup size is better when available. &ldquo;check manually&rdquo; = no API — open the vendor dashboard. Live OCR/Gemini bars are in Worker Monitoring and OCR Quota panels."
      ));

      // Sum record counts across all known PBJ/shared collections so we can
      // estimate storage consumption vs. PocketHost's 1 GB free-tier cap.
      // PocketBase doesn't expose a disk-usage endpoint on this version, so
      // this is a rough proxy (≈1 KB per record on average across our shapes).
      const tracked = [
        ["pbj_merchant_submissions", merchTotal],
        ["pbj_paycheck_submissions", paycheckTotal],
        ["pbj_bill_submissions",     billTotal],
        ["pbj_merchant_data",        merchDat],
        ["pbj_price_trends",         priceTrnd],
        ["pbj_spending_benchmarks",  spendBench],
        ["pbj_store_intel",          storeIntel],
        ["pbj_recurring_patterns",   recur],
        ["pbj_household_benchmarks", household],
        ["pbj_document_patterns",    docs],
        ["pbj_subscription_library", subs],
        ["shared_entity_library",    (merchants ?? 0) + (employers ?? 0) + (payees ?? 0)],
        ["shared_entity_aliases",    (aliasesP ?? 0) + (aliasesA ?? 0) + (aliasesR ?? 0)],
        ["hhh_collection_values",    hhhVal],
        ["cvc_collection_values",    cvcVal],
        ["hhh_market_intelligence",  hhhMkt],
        ["cts_market_intelligence",  cvcMkt],
        ["pbj_purchase_links",       links],
        ["_anomaly_log",             anomalyTotal],
        ["_quarantine_submissions",  quarantineCount],
      ];
      const totalRecords = tracked.reduce((s, [, n]) => s + (Number(n) || 0), 0);

      // ≈1 KB per record is a blunt estimate — some (market_intelligence JSON)
      // are larger, some (purchase_links) are tiny. Overall it's within 2× for
      // most PBJ data shapes. Close enough for a capacity gauge.
      const estBytes = totalRecords * 1024;
      const FREE_TIER_BYTES = 1024 * 1024 * 1024; // PocketHost free tier — 1 GB
      const pctFree = Math.min(100, (estBytes / FREE_TIER_BYTES) * 100);
      const storageState = pctFree > 85 ? "crit"
                         : pctFree > 60 ? "warn"
                         : "ok";
      const mb = (estBytes / (1024 * 1024)).toFixed(1);

      parts.push(card(
        "Total records tracked",
        "Sum of every tracked collection — the flywheel's raw corpus size.",
        totalRecords.toLocaleString(),
        "Grows with user scans; aggregation keeps the submission queues bounded."
      ));

      // Real DB size via /api/backups — if a backup exists, its ZIP size is a
      // close proxy for the compressed DB. PocketBase doesn't expose disk
      // usage directly on 0.36.9; this is the cleanest available signal.
      let backupBytes = null;
      let backupModified = null;
      try {
        const r = await timedFetch(`${PB_URL}/api/backups`, {
          headers: { Authorization: `Bearer ${token}` },
        });
        if (r.ok) {
          const list = await r.json();
          // API returns an array (sometimes wrapped). Normalize.
          const items = Array.isArray(list) ? list : (list?.items || []);
          if (items.length > 0) {
            // Use the most recent by modified
            const sorted = items.slice().sort((a, b) =>
              String(b.modified || "").localeCompare(String(a.modified || "")));
            backupBytes = sorted[0].size;
            backupModified = sorted[0].modified;
          }
        }
      } catch { /* leave null — card shows fallback */ }

      if (backupBytes != null) {
        const dbMb = (backupBytes / (1024 * 1024)).toFixed(1);
        parts.push(card(
          "Database size (backup)",
          "Compressed size of the most recent PocketBase backup — closest signal to true DB size on this PocketBase version.",
          `${dbMb} MB`,
          `From backup made ${backupModified ? relTime(backupModified) : "unknown"} · create fresh backups in Settings → Backups for a current read`,
          "ok"
        ));
      } else {
        parts.push(card(
          "Database size (backup)",
          "Compressed DB size — only visible when at least one backup exists.",
          "no backup yet",
          "Go to Settings → Backups → Initialize new backup. This dashboard will show the size once it finishes.",
          "warn"
        ));
      }

      // PocketHost is fair-use, not a hard-quota tier, so the "% of 1 GB"
      // framing I had before was misleading. Keep the record-based estimate
      // but correctly frame what the ceiling actually is.
      parts.push(card(
        "Record-count estimate (rough)",
        "Proxy DB size at ~1 KB/record. Real number is the card above when backups exist.",
        `${mb} MB`,
        `PocketHost has no hard storage cap — they monitor under a fair-use policy. Most small apps stay under 500 MB for years.`,
        totalRecords > 500000 ? "warn" : "ok"
      ));
      // Website size via GitHub public API — cached 5 min to stay well under
      // the 60/hour anonymous rate limit even if the dashboard is left open.
      if (!githubCache || (Date.now() - githubCache.fetchedAt) > GITHUB_CACHE_TTL_MS) {
        try {
          const ghRes = await timedFetch(`https://api.github.com/repos/${GITHUB_REPO}`);
          if (ghRes.ok) {
            const gh = await ghRes.json();
            githubCache = {
              sizeKB: gh.size,
              pushedAt: gh.pushed_at,
              fetchedAt: Date.now(),
            };
          }
        } catch { /* leave cache as-is */ }
      }
      if (githubCache) {
        const WEB_LIMIT_BYTES = 1024 * 1024 * 1024; // 1 GB GitHub Pages soft limit
        const webBytes = githubCache.sizeKB * 1024;
        const webPct = Math.min(100, (webBytes / WEB_LIMIT_BYTES) * 100);
        const webMb = (webBytes / (1024 * 1024)).toFixed(1);
        const webState = webPct > 85 ? "crit" : webPct > 60 ? "warn" : "ok";
        parts.push(card(
          "Website repo size",
          "GitHub Pages serves josspatech.com from this repo — measured by GitHub.",
          `${webMb} MB`,
          `~${webPct.toFixed(1)}% of GitHub Pages 1 GB soft cap · last push ${relTime(githubCache.pushedAt)}`,
          webState
        ));
      } else {
        parts.push(card(
          "Website repo size",
          "GitHub Pages serves josspatech.com from this repo.",
          "unknown",
          "Couldn't reach github.com (rate limit or offline)."
        ));
      }

      parts.push(card(
        "Website bandwidth",
        "Outbound bytes GitHub Pages serves to visitors. Free tier: 100 GB/month.",
        "check manually",
        `Only visible in Repo → Insights → Traffic for ${GITHUB_REPO}. GitHub does not expose this via API.`,
        "ok"
      ));

      parts.push(card(
        "OCR.Space quota",
        "Free tier: 25,000 requests/month shared across all PBJ users.",
        "check manually",
        `Monitor at ocr.space/ocrapi — PRO ($30/mo) = 300k/month + no per-IP rate limit`,
        "ok"
      ));
      // === SECTION: SITE TRAFFIC ===
      // Pulls from _site_visits, written by the tracking snippet on
      // josspatech.com. If the snippet isn't installed yet these all
      // show 0 — that's the card story: "add tracker to see real data."
      parts.push(`<div class="section-header">Site Traffic · josspatech.com</div>`);
      const [visitsAll, visitsList] = await Promise.all([
        pbCount("_site_visits", ""),
        pbList("_site_visits", dayAgoFilter, "-created", 500),
      ]);
      const uniqueSessionsToday = new Set(visitsList.map(v => v.session_id).filter(Boolean)).size;
      const sourceCounts = visitsList.reduce((acc, v) => {
        const s = v.source || 'unknown';
        acc[s] = (acc[s] || 0) + 1;
        return acc;
      }, {});
      const sortedSources = Object.entries(sourceCounts).sort((a, b) => b[1] - a[1]);
      const topSource = sortedSources[0] || ["—", 0];
      const pageCounts = visitsList.reduce((acc, v) => {
        const p = v.page || '/';
        acc[p] = (acc[p] || 0) + 1;
        return acc;
      }, {});
      const sortedPages = Object.entries(pageCounts).sort((a, b) => b[1] - a[1]);
      const topPage = sortedPages[0] || ["—", 0];

      parts.push(card(
        "Visits · 24h",
        "Page loads on josspatech.com in the last 24 hours (includes all landing pages + this dashboard).",
        visitsToday ?? 0,
        `${visitsAll ?? 0} all-time · ${uniqueSessionsToday} unique sessions today`,
        (visitsToday === 0) ? "warn" : "ok"
      ));
      parts.push(card(
        "Top traffic source · 24h",
        "Where today's visitors came from: direct URL, search engine, social link, or another site.",
        (topSource[0] === "—") ? "—" : `${topSource[0]} (${topSource[1]})`,
        sortedSources.length > 1
          ? sortedSources.slice(1, 4).map(([s, c]) => `${s}:${c}`).join(" · ")
          : "Install the site-visit tracker snippet on josspatech.com to populate this card."
      ));
      parts.push(card(
        "Most-visited page · 24h",
        "Which page on the site got the most loads today.",
        (topPage[0] === "—") ? "—" : topPage[0],
        topPage[1] > 0
          ? `${topPage[1]} loads · ${sortedPages.length} unique pages visited`
          : "Tracking snippet not active yet — see site_visit_tracker.html in ClaudeFiles."
      ));
      paint();

      parts.push(card(
        "Play Store test gate",
        "14-day / 12-tester closed testing required before first production release.",
        "manual",
        "Tracked in Google Play Console — this dashboard can't read it.",
        "ok"
      ));
      paint();

      // Banner + maintenance status refresh alongside the main grid.
      // updateWowBanner has its own try/catch — it doesn't block if it fails.
      updateWowBanner().catch(() => {});
      updateOpsAlertBanner().catch(() => {});
      renderFounderCostTable();
      renderBreakevenPanel();

      document.getElementById("lastRefresh").textContent =
        `updated ${new Date().toLocaleTimeString()}`;
      document.getElementById("pulse").classList.remove("stale");
    } catch (e) {
      document.getElementById("lastRefresh").textContent = `error: ${e.message}`;
      document.getElementById("pulse").classList.add("stale");
    }
  }

  // ─── Boot ──────────────────────────────────────────────
  function showDashboard() {
    document.getElementById("login").style.display = "none";
    document.getElementById("dashboard").style.display = "block";
    const page = window.ADMIN_PAGE || "flywheel";
    if (page === "flywheel" && document.getElementById("grid")) {
      refresh();
      setRefresh();
    } else if (page === "hub") {
      const pulse = document.getElementById("pulse");
      if (pulse) pulse.classList.add("stale");
    }
    mCheckMaintenanceFlag().catch(() => {});
    initAdminPage();
  }

  function wireLoginEnterKey() {
    const pw = document.getElementById("password");
    const em = document.getElementById("email");
    if (!pw || pw.dataset.wired) return;
    pw.dataset.wired = "1";
    pw.addEventListener("keydown", (e) => {
      if (e.key === "Enter") doLogin();
    });
    if (em) {
      em.addEventListener("keydown", (e) => {
        if (e.key === "Enter") pw.focus();
      });
    }
  }

  async function renderHubBriefStatus(issues, infoIssues) {
    const el = document.getElementById("hubStatusLines");
    if (!el) return;
    const lines = [];
    if (issues.length) lines.push(`<strong style="color:var(--danger)">${issues.length} alert(s)</strong>: ${issues[0]}`);
    else lines.push('<span style="color:var(--success)">No red ops alerts from cached data / health ping.</span>');
    if (infoIssues.length) lines.push(`<span style="color:var(--text-dim)">${infoIssues.length} info note(s) — see banners on sub-pages.</span>`);
    lines.push('Worker KV: manual refresh only · <a href="workers.html">Workers</a> · <a href="ocr-quota.html">OCR</a>');
    el.innerHTML = lines.join("<br>");
  }
