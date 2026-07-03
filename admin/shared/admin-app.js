// ========================================================
  // Maintenance + reports
  // ========================================================

  function log(msg, kind) {
    const el = document.getElementById("log");
    const ts = new Date().toLocaleTimeString();
    const entry = document.createElement("div");
    entry.className = "log-entry " + (kind || "info");
    entry.innerHTML = `<span class="t">${ts}</span> &nbsp;${msg}`;
    el.prepend(entry); // newest on top
  }

  async function withBusy(selector, label, fn) {
    const btn = typeof selector === 'string' ? document.querySelector(selector) : selector;
    if (btn) {
      btn.disabled = true;
      const oldText = btn.textContent;
      btn.textContent = label;
      try { await fn(); }
      finally { btn.disabled = false; btn.textContent = oldText; }
    } else {
      await fn();
    }
  }

  async function pbAuth(path, init) {
    return await timedFetch(PB_URL + path, {
      ...(init || {}),
      headers: { ...(init && init.headers || {}), Authorization: `Bearer ${token}` },
    });
  }

  /** Paginate through an entire collection. Returns array of records. */
  async function listAllRecords(collection, filter, fields) {
    const pageSize = 200;
    let page = 1;
    const out = [];
    while (true) {
      const params = new URLSearchParams({ perPage: String(pageSize), page: String(page) });
      if (filter) params.set("filter", filter);
      if (fields) params.set("fields", fields);
      const res = await pbAuth(`/api/collections/${encodeURIComponent(collection)}/records?${params}`);
      if (!res.ok) throw new Error(`List ${collection} failed (${res.status})`);
      const data = await res.json();
      out.push(...(data.items || []));
      if (out.length >= (data.totalItems || 0) || (data.items || []).length === 0) break;
      page++;
      if (page > 100) break; // hard safety
    }
    return out;
  }

  function downloadFile(filename, content, mime) {
    const blob = new Blob([content], { type: mime || "text/plain;charset=utf-8" });
    const url = URL.createObjectURL(blob);
    const a = document.createElement("a");
    a.href = url;
    a.download = filename;
    document.body.appendChild(a);
    a.click();
    a.remove();
    setTimeout(() => URL.revokeObjectURL(url), 2000);
  }

  function recordsToCSV(records) {
    if (!records.length) return "";
    // Collect union of keys; system fields first in a sensible order.
    const systemOrder = ["id", "created", "updated"];
    const seen = new Set(systemOrder);
    const headers = [...systemOrder];
    for (const r of records) {
      for (const k of Object.keys(r)) {
        if (!seen.has(k) && !k.startsWith("collection")) {
          seen.add(k);
          headers.push(k);
        }
      }
    }
    const esc = (v) => {
      if (v == null) return "";
      let s = typeof v === "object" ? JSON.stringify(v) : String(v);
      if (/[",\n\r]/.test(s)) s = `"${s.replace(/"/g, '""')}"`;
      return s;
    };
    const lines = [headers.join(",")];
    for (const r of records) {
      lines.push(headers.map(h => esc(r[h])).join(","));
    }
    return lines.join("\n");
  }

  // ─── Backups ────────────────────────────────────────────
  async function mCreateBackup() {
    if (!confirm("Create a new PocketBase backup now? This can take 10-60 seconds.")) return;
    await withBusy(event?.target, "Backing up…", async () => {
      try {
        log("Starting backup via /api/backups…", "info");
        const r = await pbAuth("/api/backups", { method: "POST", headers: { "Content-Type": "application/json" }, body: "{}" });
        if (r.ok) {
          log("Backup created ✓  — refresh the page for the new DB-size card.", "ok");
        } else {
          const txt = (await r.text()).slice(0, 200);
          log(`Backup failed (${r.status}): ${txt}`, "err");
        }
      } catch (e) { log(`Backup threw: ${e.message}`, "err"); }
    });
  }

  async function mPruneBackups() {
    if (!confirm("Delete all backups except the 3 most recent? This cannot be undone.")) return;
    await withBusy(event?.target, "Pruning…", async () => {
      try {
        const r = await pbAuth("/api/backups");
        if (!r.ok) throw new Error(`list backups failed (${r.status})`);
        const list = await r.json();
        const items = Array.isArray(list) ? list : (list.items || []);
        items.sort((a, b) => String(b.modified || "").localeCompare(String(a.modified || "")));
        const toDelete = items.slice(3);
        if (!toDelete.length) { log("Nothing to prune — fewer than 4 backups.", "info"); return; }
        log(`Deleting ${toDelete.length} older backups…`, "info");
        let ok = 0, fail = 0;
        for (const b of toDelete) {
          const d = await pbAuth(`/api/backups/${encodeURIComponent(b.key)}`, { method: "DELETE" });
          if (d.ok) ok++; else fail++;
        }
        log(`Prune complete — ${ok} deleted, ${fail} failed.`, fail ? "err" : "ok");
      } catch (e) { log(`Prune threw: ${e.message}`, "err"); }
    });
  }

  // ─── Data hygiene ───────────────────────────────────────
  async function mClearResolvedAnomalies() {
    if (!confirm("Delete resolved anomalies older than 7 days?")) return;
    await withBusy(event?.target, "Clearing…", async () => {
      try {
        const cutoff = new Date(Date.now() - 7 * 86400000).toISOString().replace("T", " ").slice(0, 19);
        const rows = await listAllRecords("_anomaly_log", `resolved = true && detected_at < "${cutoff}"`, "id");
        log(`Deleting ${rows.length} resolved anomaly rows…`, "info");
        let ok = 0, fail = 0;
        for (const row of rows) {
          const d = await pbAuth(`/api/collections/_anomaly_log/records/${row.id}`, { method: "DELETE" });
          if (d.ok) ok++; else fail++;
        }
        log(`Cleared — ${ok} deleted, ${fail} failed.`, fail ? "err" : "ok");
      } catch (e) { log(`Clear threw: ${e.message}`, "err"); }
    });
  }

  async function mClearOldQuarantine() {
    if (!confirm("Delete quarantine records older than 30 days?")) return;
    await withBusy(event?.target, "Clearing…", async () => {
      try {
        const cutoff = new Date(Date.now() - 30 * 86400000).toISOString().replace("T", " ").slice(0, 19);
        const rows = await listAllRecords("_quarantine_submissions", `flagged_at < "${cutoff}"`, "id");
        log(`Deleting ${rows.length} old quarantine rows…`, "info");
        let ok = 0, fail = 0;
        for (const row of rows) {
          const d = await pbAuth(`/api/collections/_quarantine_submissions/records/${row.id}`, { method: "DELETE" });
          if (d.ok) ok++; else fail++;
        }
        log(`Cleared — ${ok} deleted, ${fail} failed.`, fail ? "err" : "ok");
      } catch (e) { log(`Clear threw: ${e.message}`, "err"); }
    });
  }

  // ─── Export CSV ─────────────────────────────────────────
  async function mExportCSV() {
    const col = document.getElementById("exportCol").value;
    await withBusy(event?.target, "Exporting…", async () => {
      try {
        log(`Streaming records from ${col}…`, "info");
        const rows = await listAllRecords(col);
        const csv = recordsToCSV(rows);
        const stamp = new Date().toISOString().slice(0, 10);
        downloadFile(`${col}_${stamp}.csv`, csv, "text/csv;charset=utf-8");
        log(`Exported ${rows.length} rows from ${col} → ${col}_${stamp}.csv ✓`, "ok");
      } catch (e) { log(`Export failed: ${e.message}`, "err"); }
    });
  }

  // ─── Reports ────────────────────────────────────────────
  async function mWeeklySummary() {
    await withBusy(event?.target, "Building…", async () => {
      try {
        log("Aggregating 7-day flywheel stats…", "info");
        const weekAgo = new Date(Date.now() - 7 * 86400000).toISOString().replace("T", " ").slice(0, 19);
        const f = `created >= "${weekAgo}"`;
        const [
          merch7, merchTot, paycheck7, bill7, alias7, aggAll, visitsWk,
          merchants, employers, payees, anomaliesOpen, quarantineTot,
        ] = await Promise.all([
          pbCount("pbj_merchant_submissions", f),
          pbCount("pbj_merchant_submissions", ""),
          pbCount("pbj_paycheck_submissions", f),
          pbCount("pbj_bill_submissions", f),
          pbCount("shared_entity_aliases", f),
          pbCount("pbj_merchant_submissions", 'is_stale = true'),
          pbCount("_site_visits", f),
          pbCount("shared_entity_library", `entity_type = "merchant"`),
          pbCount("shared_entity_library", `entity_type = "employer"`),
          pbCount("shared_entity_library", `entity_type = "payee"`),
          pbCount("_anomaly_log", "resolved = false"),
          pbCount("_quarantine_submissions", ""),
        ]);
        const today = new Date().toISOString().slice(0, 10);
        const md = `# PocketBudJet Flywheel — Weekly Summary
**Week ending ${today}**

## Ingest this week
| Stream | 7-day writes | Lifetime |
|---|---:|---:|
| Merchant submissions | ${merch7 ?? '—'} | ${merchTot ?? '—'} |
| Pay-stub submissions | ${paycheck7 ?? '—'} | — |
| Bill submissions | ${bill7 ?? '—'} | — |
| Alias votes | ${alias7 ?? '—'} | — |
| Site visits (josspatech.com) | ${visitsWk ?? '—'} | — |

## Canonical library state
| Type | Count |
|---|---:|
| Canonical merchants | ${merchants ?? '—'} |
| Canonical employers | ${employers ?? '—'} |
| Canonical payees | ${payees ?? '—'} |

## Quality
| Signal | Count |
|---|---:|
| Aggregated submissions (lifetime) | ${aggAll ?? '—'} |
| Open anomalies | ${anomaliesOpen ?? 0} |
| PII quarantine (lifetime) | ${quarantineTot ?? 0} |

Generated ${new Date().toISOString()} by the Flywheel Dashboard.
`;
        downloadFile(`pbj_weekly_${today}.md`, md, "text/markdown;charset=utf-8");
        log("Weekly summary downloaded ✓", "ok");
      } catch (e) { log(`Summary failed: ${e.message}`, "err"); }
    });
  }

  async function mTopMerchants() {
    await withBusy(event?.target, "Building…", async () => {
      try {
        log("Ranking canonical merchants by submission_count…", "info");
        const res = await pbAuth(`/api/collections/shared_entity_library/records?perPage=50&sort=-submission_count&filter=${encodeURIComponent("entity_type = \"merchant\"")}`);
        if (!res.ok) throw new Error(`list failed (${res.status})`);
        const data = await res.json();
        const items = data.items || [];
        const today = new Date().toISOString().slice(0, 10);
        const rows = items.map((r, i) =>
          `| ${i + 1} | ${(r.canonical_name || '—').slice(0, 50)} | ${r.submission_count ?? 0} | ${Number(r.confidence ?? 0).toFixed(2)} | ${r.region || '—'} |`);
        const md = `# Top 50 Canonical Merchants
**Ranked by cumulative submission count, ${today}**

| Rank | Merchant | Votes | Confidence | Region |
|---:|---|---:|---:|---|
${rows.join("\n")}

Generated ${new Date().toISOString()}.
`;
        downloadFile(`pbj_top_merchants_${today}.md`, md, "text/markdown;charset=utf-8");
        log(`Top ${items.length} merchants downloaded ✓`, "ok");
      } catch (e) { log(`Report failed: ${e.message}`, "err"); }
    });
  }

  // ─── Testing & verification ─────────────────────────
  async function mSendTestSubmission() {
    await withBusy(event?.target, "Sending…", async () => {
      try {
        const marker = `CLAUDE_TEST_${Date.now()}`;
        const body = {
          merchant_entity_ref: null,
          merchant_key: marker,                  // fingerprint-unique key
          raw_name: "DASHBOARD TEST MERCHANT",
          category: "Uncategorized",
          subcategory: "",
          amount_bucket: "10-25",
          store_number: "",
          zip_code: "00000",
          region: "US",
          phone_canonical: "",
          website_domain: "",
          count: 1,
          app_version: "dashboard-test",
          match_method: "none",
          confidence: 0.5,
          is_stale: false,
          ocr_confidence: 0.8,
          source_fingerprint: marker,
          image_hash: "",
        };
        // Anonymous POST (no auth header) — tests the real client write path.
        const r = await timedFetch(`${PB_URL}/api/collections/pbj_merchant_submissions/records`, {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify(body),
        });
        if (r.ok) {
          const created = await r.json();
          const s = document.getElementById("testSubStatus");
          s.innerHTML = `created <code>${created.id}</code> · aggregation should flip it to processed within the hour`;
          log(`Test submission ${created.id} (key ${marker}) created ✓`, "ok");
        } else {
          const t = (await r.text()).slice(0, 200);
          log(`Test submission failed (${r.status}): ${t}`, "err");
        }
      } catch (e) { log(`Test submission threw: ${e.message}`, "err"); }
    });
  }

  async function mDeleteById() {
    const col = document.getElementById("deleteCol").value;
    const id  = document.getElementById("deleteId").value.trim();
    if (!id) { log("Enter a record ID first.", "err"); return; }
    if (!confirm(`Delete ${col}/${id}? This cannot be undone.`)) return;
    await withBusy(event?.target, "Deleting…", async () => {
      try {
        const r = await pbAuth(`/api/collections/${encodeURIComponent(col)}/records/${encodeURIComponent(id)}`, {
          method: "DELETE",
        });
        if (r.ok) {
          log(`Deleted ${col}/${id} ✓`, "ok");
          document.getElementById("deleteId").value = "";
        } else if (r.status === 404) {
          log(`Record ${col}/${id} not found.`, "err");
        } else {
          const t = (await r.text()).slice(0, 200);
          log(`Delete failed (${r.status}): ${t}`, "err");
        }
      } catch (e) { log(`Delete threw: ${e.message}`, "err"); }
    });
  }

  // ─── Flywheel curation ───────────────────────────────
  async function mPromoteAliases() {
    const n = parseInt(document.getElementById("promoteThreshold").value, 10);
    if (!Number.isFinite(n) || n < 1) { log("Enter a threshold ≥ 1.", "err"); return; }
    if (!confirm(`Promote every pending alias with ≥ ${n} submission_count votes to 'approved'?`)) return;
    await withBusy(event?.target, "Promoting…", async () => {
      try {
        const filter = `status = "pending" && submission_count >= ${n}`;
        const rows = await listAllRecords("shared_entity_aliases", filter, "id,submission_count");
        log(`Promoting ${rows.length} aliases with ${n}+ votes…`, "info");
        let ok = 0, fail = 0;
        for (const r of rows) {
          const res = await pbAuth(`/api/collections/shared_entity_aliases/records/${r.id}`, {
            method: "PATCH",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ status: "approved" }),
          });
          if (res.ok) ok++; else fail++;
        }
        log(`Promotion complete — ${ok} approved, ${fail} failed.`, fail ? "err" : "ok");
      } catch (e) { log(`Promotion threw: ${e.message}`, "err"); }
    });
  }

  async function mOpenAliasReviewer() {
    const panel = document.getElementById("aliasReviewerPanel");
    panel.style.display = "block";
    panel.innerHTML = `<div style="padding:14px;color:var(--text-dim);font-size:12px">Loading…</div>`;
    try {
      const r = await pbAuth(`/api/collections/shared_entity_aliases/records?perPage=20&sort=created&filter=${encodeURIComponent("status = \"pending\"")}`);
      if (!r.ok) throw new Error(`list failed (${r.status})`);
      const data = await r.json();
      const items = data.items || [];
      if (!items.length) {
        panel.innerHTML = `<div style="padding:14px;color:var(--success);font-size:13px">✓ No pending aliases. Canonicalization is caught up.</div>`;
        return;
      }
      panel.innerHTML = items.map(r => `
        <div class="row" data-id="${r.id}">
          <span class="alias-text">${(r.alias || "").replace(/</g, "&lt;")} → ${(r.alias_key || "").slice(0, 30)}</span>
          <span class="alias-meta">${r.submission_count || 0} votes · ${r.reject_count || 0} rej</span>
          <button class="mini-btn approve" onclick="mApproveAlias('${r.id}')">Approve</button>
          <button class="mini-btn reject"  onclick="mRejectAlias('${r.id}')">Reject</button>
        </div>`).join("");
    } catch (e) {
      panel.innerHTML = `<div style="padding:14px;color:var(--danger);font-size:13px">Failed to load: ${e.message}</div>`;
    }
  }

  async function mSetAliasStatus(id, status) {
    const row = document.querySelector(`#aliasReviewerPanel .row[data-id="${id}"]`);
    if (row) row.querySelectorAll("button").forEach(b => b.disabled = true);
    try {
      const r = await pbAuth(`/api/collections/shared_entity_aliases/records/${id}`, {
        method: "PATCH",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ status }),
      });
      if (r.ok) {
        if (row) row.style.opacity = 0.4;
        log(`Alias ${id} → ${status} ✓`, "ok");
      } else {
        log(`Alias ${id} patch failed (${r.status})`, "err");
        if (row) row.querySelectorAll("button").forEach(b => b.disabled = false);
      }
    } catch (e) {
      log(`Alias ${id} patch threw: ${e.message}`, "err");
      if (row) row.querySelectorAll("button").forEach(b => b.disabled = false);
    }
  }
  async function mApproveAlias(id) { await mSetAliasStatus(id, "approved"); }
  async function mRejectAlias(id)  { await mSetAliasStatus(id, "rejected"); }

  // ─── Operations: maintenance mode ────────────────────
  async function mCheckMaintenanceFlag() {
    const s = document.getElementById("maintenanceStatus");
    try {
      const r = await pbAuth(`/api/collections/_app_config/records?filter=${encodeURIComponent("key = \"maintenance_mode\"")}&perPage=1`);
      if (r.status === 404) {
        s.textContent = "_app_config not created yet — use this button to create + toggle.";
        maintenanceFlag = null;
        return;
      }
      if (!r.ok) { s.textContent = `check failed (${r.status})`; return; }
      const data = await r.json();
      const rec = (data.items || [])[0];
      maintenanceFlag = rec ? rec.value === "true" : false;
      s.innerHTML = maintenanceFlag
        ? `<strong style="color:var(--danger)">ON — clients should be read-only</strong>`
        : `<span style="color:var(--success)">OFF — normal writes</span>`;
    } catch (e) { s.textContent = `check threw: ${e.message}`; }
  }

  async function mToggleMaintenance() {
    const target = !maintenanceFlag;
    if (!confirm(`Set maintenance_mode = ${target}?\n\nNote: PBJ app doesn't check this yet — this is a stub for future app builds. Safe to toggle now.`)) return;
    await withBusy(event?.target, "Toggling…", async () => {
      try {
        // Find existing row or create new
        const r = await pbAuth(`/api/collections/_app_config/records?filter=${encodeURIComponent("key = \"maintenance_mode\"")}&perPage=1`);
        if (r.status === 404) {
          // collection doesn't exist — create it first
          const create = await pbAuth(`/api/collections`, {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({
              name: "_app_config",
              type: "base",
              listRule: "", viewRule: "",
              createRule: null, updateRule: null, deleteRule: null,
              fields: [
                { name: "key",   type: "text", required: true },
                { name: "value", type: "text", required: false },
                { name: "note",  type: "text", required: false },
              ],
            }),
          });
          if (!create.ok) { log(`Couldn't create _app_config (${create.status})`, "err"); return; }
          log("_app_config collection created ✓", "ok");
        }
        const data = r.ok ? await r.json() : { items: [] };
        const existing = (data.items || [])[0];
        const body = {
          key: "maintenance_mode",
          value: target ? "true" : "false",
          note: target ? `Enabled via dashboard ${new Date().toISOString()}` : `Disabled via dashboard ${new Date().toISOString()}`,
        };
        if (existing) {
          const p = await pbAuth(`/api/collections/_app_config/records/${existing.id}`, {
            method: "PATCH",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify(body),
          });
          if (!p.ok) { log(`Toggle PATCH failed (${p.status})`, "err"); return; }
        } else {
          const c = await pbAuth(`/api/collections/_app_config/records`, {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify(body),
          });
          if (!c.ok) { log(`Toggle POST failed (${c.status})`, "err"); return; }
        }
        log(`Maintenance mode → ${target ? "ON" : "OFF"} ✓`, "ok");
        await mCheckMaintenanceFlag();
      } catch (e) { log(`Toggle threw: ${e.message}`, "err"); }
    });
  }

  // ─── Operations: log tail ────────────────────────────
  async function mToggleLogTail() {
    const btn = document.getElementById("logTailBtn");
    const pane = document.getElementById("logTailPane");
    const status = document.getElementById("logTailStatus");

    if (logTailTick) {
      clearInterval(logTailTick);
      logTailTick = null;
      btn.textContent = "Start log tail (every 30s)";
      status.textContent = "stopped";
      return;
    }
    pane.style.display = "block";
    btn.textContent = "Stop log tail";
    status.textContent = "polling…";

    const poll = async () => {
      try {
        const r = await pbAuth("/api/logs?perPage=20&sort=-created");
        if (r.status === 429) { status.textContent = "rate-limited — slow down"; return; }
        if (!r.ok) { status.textContent = `error ${r.status}`; return; }
        const data = await r.json();
        const items = (data.items || []).reverse();
        pane.innerHTML = items.map(l => {
          const level = (l.level || "").toLowerCase();
          const klass = level.includes("err") ? "l-error"
                      : level.includes("warn") ? "l-warn"
                      : "l-info";
          const when = (l.created || "").slice(11, 19);
          const msg = (l.message || JSON.stringify(l).slice(0, 300)).replace(/</g, "&lt;");
          return `<div class="${klass}">${when}  ${msg}</div>`;
        }).join("") || "(no recent log entries)";
        status.textContent = `last poll ${new Date().toLocaleTimeString()}`;
      } catch (e) { status.textContent = `poll threw: ${e.message}`; }
    };
    await poll();
    logTailTick = setInterval(poll, 30000);
  }

  // ─── Force-run server jobs ───────────────────────────
  async function mForceRun(job) {
    const labels = {
      aggregate: "aggregation",
      staleness: "staleness sweep",
      anomaly:   "anomaly detection",
      retention: "retention cleanup",
    };
    if (!confirm(`Force-run ${labels[job] || job} on the server?`)) return;
    await withBusy(event?.target, "Running…", async () => {
      try {
        log(`POST /api/ops/${job} …`, "info");
        const r = await pbAuth(`/api/ops/${job}`, {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: "{}",
        });
        if (r.status === 404) {
          log(`/api/ops/${job} not found — deploy ops_routes.pb.js to pb_hooks/`, "err");
          return;
        }
        const body = await r.text();
        if (!r.ok) { log(`${job} failed (${r.status}): ${body.slice(0, 200)}`, "err"); return; }
        let parsed;
        try { parsed = JSON.parse(body); } catch { parsed = body; }
        log(`${job} ✓ — ${typeof parsed === 'object' ? JSON.stringify(parsed).slice(0, 300) : parsed.slice(0, 300)}`, "ok");
      } catch (e) { log(`${job} threw: ${e.message}`, "err"); }
    });
  }

  async function mOpsHealth() {
    await withBusy(event?.target, "Pinging…", async () => {
      try {
        const r = await pbAuth("/api/ops/health");
        if (r.status === 404) {
          log("ops_routes.pb.js not deployed (404). Upload the file to pb_hooks/ via FTP.", "err");
          return;
        }
        const body = await r.json();
        log(`/api/ops/health ✓ — ${body.routes_available.length} routes live at ${body.timestamp}`, "ok");
      } catch (e) { log(`Ping threw: ${e.message}`, "err"); }
    });
  }

  // ─── Week-over-week banner ───────────────────────────
  async function updateWowBanner() {
    const banner = document.getElementById("wowBanner");
    if (!banner) return;
    try {
      const weekAgo = new Date(Date.now() - 7 * 86400000).toISOString().replace("T", " ").slice(0, 19);
      const twoWeek = new Date(Date.now() - 14 * 86400000).toISOString().replace("T", " ").slice(0, 19);
      const [thisWeek, lastWeek, newAnomalies] = await Promise.all([
        pbCount("pbj_merchant_submissions", `created >= "${weekAgo}"`),
        pbCount("pbj_merchant_submissions", `created >= "${twoWeek}" && created < "${weekAgo}"`),
        pbCount("_anomaly_log", `detected_at >= "${weekAgo}" && resolved = false`),
      ]);
      const items = [];
      if (thisWeek != null && lastWeek != null && lastWeek > 0) {
        const pct = ((thisWeek - lastWeek) / lastWeek) * 100;
        if (Math.abs(pct) >= 40) {
          const klass = pct > 0 ? "up" : "down";
          items.push(`<div class="wow-item ${klass}">Merchant submissions ${pct > 0 ? "up" : "down"} <strong>${Math.abs(pct).toFixed(0)}%</strong> vs. last week — ${thisWeek} this week, ${lastWeek} last week.</div>`);
        }
      }
      if (newAnomalies && newAnomalies > 0) {
        items.push(`<div class="wow-item crit"><strong>${newAnomalies}</strong> new unresolved anomal${newAnomalies === 1 ? 'y' : 'ies'} this week — check the Quality &amp; Security section.</div>`);
      }
      if (items.length === 0) {
        banner.style.display = "none";
        return;
      }
      banner.innerHTML = `<strong>Week-over-week signal</strong><br>${items.join("")}`;
      banner.style.display = "block";
    } catch {
      banner.style.display = "none";
    }
  }

  // ─── Ask Claude (clipboard + open tab) ─────────────────
  // No server-side dependency — just scrapes the rendered dashboard
  // DOM, turns every card into a bullet line, formats an analysis
  // prompt, copies it to the clipboard, and opens claude.ai in a
  // new tab. User pastes manually. No API key, no cost.
  async function mAskClaude() {
    await withBusy(event?.target, "Preparing…", async () => {
      try {
        // Walk the grid — each section-header groups the cards below it.
        const grid = document.getElementById("grid");
        const nodes = Array.from(grid.children);
        const lines = [];
        let section = "";
        for (const n of nodes) {
          if (n.classList?.contains("section-header")) {
            section = n.textContent.trim();
            lines.push(`\n### ${section}`);
            continue;
          }
          if (n.classList?.contains("card")) {
            const label = n.querySelector(".label")?.textContent.trim() || "";
            const value = n.querySelector(".value")?.textContent.trim() || "";
            const sub   = n.querySelector(".sub")?.textContent.trim() || "";
            if (label || value) {
              const subPart = sub ? `  — _${sub}_` : "";
              lines.push(`- **${label}**: \`${value}\`${subPart}`);
            }
          }
          if (n.classList?.contains("list-card")) {
            const title = n.querySelector(".head span")?.textContent.trim() || "";
            const items = Array.from(n.querySelectorAll("li")).slice(0, 10).map(li => {
              const when = li.querySelector(".when")?.textContent.trim() || "";
              const what = li.querySelector(".what")?.textContent.trim().replace(/\s+/g, ' ').slice(0, 180) || "";
              return `  - ${when} — ${what}`;
            });
            const empty = n.querySelector(".empty")?.textContent.trim();
            lines.push(`\n**${title}:**`);
            if (items.length) lines.push(items.join("\n"));
            else if (empty)   lines.push(`  - ${empty}`);
          }
        }
        const question = document.getElementById("claudeQuestion")?.value?.trim() || "";
        const prompt = `I'm looking at the live JosspaTech Flywheel Ops dashboard for ${new Date().toLocaleString()}. Here's the current state:
${lines.join("\n")}

Context: this dashboard watches the shared PocketBase instance that three JosspaTech apps write to — PBJ (PocketBudJet, budgeting), HHH (Handy Horology Helper, watch collection), and CVC (Curator's Vault, collectibles). Users scan receipts / catalog items / do searches; anonymized submissions feed consensus tables; server-side hooks aggregate into canonical merchants/employers/payees and per-item market intel; each app reads the enriched data back on the next scan or search.

${question
  ? `My specific question: ${question}`
  : `Please analyze:
1. What's working well (flywheel signals that look healthy)?
2. What's concerning (queue depths, anomalies, gaps)?
3. What should I focus on this week?
Keep it tight — 3-5 bullets per section.`}
`;

        // Copy to clipboard
        let copied = false;
        try {
          await navigator.clipboard.writeText(prompt);
          copied = true;
        } catch (_) {
          // Fallback — older browsers / insecure context
          const ta = document.createElement("textarea");
          ta.value = prompt;
          ta.style.position = "fixed"; ta.style.opacity = "0";
          document.body.appendChild(ta);
          ta.select();
          try { copied = document.execCommand("copy"); } catch {}
          ta.remove();
        }

        if (copied) {
          log(`Prompt (${prompt.length} chars) copied to clipboard. Opening Claude…`, "ok");
          // Open Claude in a new tab. claude.ai's /new spawns a fresh conversation.
          window.open("https://claude.ai/new", "_blank", "noopener");
        } else {
          log(`Clipboard copy blocked by browser. Prompt printed below — select + copy manually.`, "err");
          log(`<pre style="white-space:pre-wrap;margin-top:6px">${prompt.replace(/</g,"&lt;")}</pre>`, "info");
        }
      } catch (e) { log(`Ask Claude failed: ${e.message}`, "err"); }
    });
  }

  async function mSiteTraffic() {
    await withBusy(event?.target, "Building…", async () => {
      try {
        log("Streaming 7-day site visits for analysis…", "info");
        const weekAgo = new Date(Date.now() - 7 * 86400000).toISOString().replace("T", " ").slice(0, 19);
        const rows = await listAllRecords("_site_visits", `created >= "${weekAgo}"`);
        // Group by day
        const byDay = {};
        const bySource = {};
        const byPage = {};
        const byReferrer = {};
        const uniqueSessions = new Set();
        for (const v of rows) {
          const day = (v.created || "").slice(0, 10) || "unknown";
          byDay[day] = (byDay[day] || 0) + 1;
          bySource[v.source || "unknown"] = (bySource[v.source || "unknown"] || 0) + 1;
          byPage[v.page || "/"] = (byPage[v.page || "/"] || 0) + 1;
          if (v.referrer_host) byReferrer[v.referrer_host] = (byReferrer[v.referrer_host] || 0) + 1;
          if (v.session_id) uniqueSessions.add(v.session_id);
        }
        const sortEntries = (obj) => Object.entries(obj).sort((a, b) => b[1] - a[1]);
        const today = new Date().toISOString().slice(0, 10);
        const md = `# josspatech.com — 7-day Site Traffic
**Through ${today}**

- **Total page loads:** ${rows.length}
- **Unique sessions:** ${uniqueSessions.size}
- **Tracked pages:** ${Object.keys(byPage).length}
- **Distinct referrer domains:** ${Object.keys(byReferrer).length}

## By day
${sortEntries(byDay).sort((a, b) => a[0].localeCompare(b[0])).map(([d, c]) => `- ${d}: ${c}`).join("\n")}

## By source
${sortEntries(bySource).map(([s, c]) => `- ${s}: ${c}`).join("\n") || "- (no visits yet — install the tracker on josspatech.com)"}

## Top pages
${sortEntries(byPage).slice(0, 10).map(([p, c]) => `- \`${p}\` — ${c}`).join("\n")}

## Top external referrers
${sortEntries(byReferrer).slice(0, 10).map(([r, c]) => `- ${r} — ${c}`).join("\n") || "- (none recorded yet)"}

Generated ${new Date().toISOString()}.
`;
        downloadFile(`site_traffic_${today}.md`, md, "text/markdown;charset=utf-8");
        log(`Traffic report (${rows.length} visits) downloaded ✓`, "ok");
      } catch (e) { log(`Report failed: ${e.message}`, "err"); }
    });
  }

  /* ─── App Version Snapshot — manually maintained ─────────────
     Update the rows when you ship. There's no free, auth-less
     source of truth from Apple/Google for this; both stores
     gate the relevant APIs behind App Store Connect Auth or Play
     Console service-account keys. Keeping it manual is acceptable
     because the act of submitting is already a manual gesture.
     ──────────────────────────────────────────────────────────── */
  const APP_VERSIONS = [
    {
      app: "PocketBudJet (PBJ)",
      ios:    { version: "1.0.0", build: "271", status: "testflight" },
      android:{ version: "1.0.0", build: "271", status: "testflight" },
      lastSubmitted: "2026-06-20",
      bundleId: "com.josspatech.pocketbudjet",
      appStoreId: "6761077263",
      notes: "Build 271 — closed testing (alpha), 21-day trial, shopping intelligence, Web Companion, SCHEMA v78+"
    },
    {
      app: "Handy Horology Helper (HHH)",
      ios:    { version: null,   build: null,  status: "notship" },
      android:{ version: null,   build: null,  status: "notship" },
      lastSubmitted: null,
      bundleId: "com.josspatech.handyhorology",   // Verify against actual bundle ID
      appStoreId: null,
      notes: "AI calls migrated to Worker (Session 67). Awaiting first build."
    },
    {
      app: "Curator's Vault: Classics (CVC)",
      ios:    { version: null,   build: null,  status: "notship" },
      android:{ version: null,   build: null,  status: "notship" },
      lastSubmitted: null,
      bundleId: "com.josspatech.curatorsvault",   // Verify against actual bundle ID
      appStoreId: null,
      notes: "First-ever build owed — SetCompletion, GradingGuide, cert-verify, photo-studio camera all in source."
    },
  ];

  function renderAppVersions() {
    const root = document.getElementById("appVersionsTable");
    if (!root) return;
    const statusLabel = (s) => ({
      live: "Live", review: "In Review", rejected: "Rejected",
      notship: "Not Shipped", testflight: "TestFlight / Closed Testing",
    }[s] || s);
    const cell = (s) => s.version
      ? `<span class="v-mono">${s.version} (${s.build})</span> <span class="v-status ${s.status}">${statusLabel(s.status)}</span>`
      : `<span class="v-dim">—</span>`;
    // Public-listings column — Play URL is constructible from the bundle ID
    // (works the moment the listing goes live), so we link it any time the
    // bundle ID is known. App Store URL needs the Apple-assigned numeric ID
    // which is only known post-approval — placeholder dash until then.
    const listings = (a) => {
      const playUrl = a.bundleId ? `https://play.google.com/store/apps/details?id=${a.bundleId}` : null;
      const appUrl  = a.appStoreId ? `https://apps.apple.com/us/app/id${a.appStoreId}` : null;
      const ios     = appUrl  ? `<a href="${appUrl}"  target="_blank" rel="noopener noreferrer" style="text-decoration:none">🍎 App Store ↗</a>` : `<span class="v-dim">🍎 —</span>`;
      const android = playUrl ? `<a href="${playUrl}" target="_blank" rel="noopener noreferrer" style="text-decoration:none">🤖 Play ↗</a>`     : `<span class="v-dim">🤖 —</span>`;
      return `<div style="display:flex; gap:10px; flex-direction:column; font-size:11px;">${ios}<br>${android}</div>`;
    };
    root.innerHTML = `
      <table>
        <thead><tr>
          <th>App</th><th>iOS</th><th>Android</th><th>Last Submitted</th><th>Public Listings</th><th>Notes</th>
        </tr></thead>
        <tbody>
          ${APP_VERSIONS.map(a => `
            <tr>
              <td class="v-app">${a.app}</td>
              <td>${cell(a.ios)}</td>
              <td>${cell(a.android)}</td>
              <td class="v-mono">${a.lastSubmitted || '<span class="v-dim">—</span>'}</td>
              <td>${listings(a)}</td>
              <td style="color: var(--text-dim); font-size: 12px;">${a.notes}</td>
            </tr>
          `).join("")}
        </tbody>
      </table>`;
  }

  /* ─── Quick Actions ──────────────────────────────────────────
     Buttons that fire admin tasks. Output streams into #qaLog.
     Each function appends a timestamped line to the log. */
  function qaLog(msg, level) {
    const log = document.getElementById("qaLog");
    if (!log) return;
    log.style.display = "block";
    const t = new Date().toLocaleTimeString();
    const color = level === "err" ? "var(--danger)"
                : level === "ok"  ? "var(--success)"
                : "var(--text-dim)";
    log.innerHTML += `<div style="color:${color}">[${t}] ${msg}</div>`;
    log.scrollTop = log.scrollHeight;
  }

  async function qaPingWorker() {
    qaLog("Pinging Worker /...");
    try {
      const t0 = performance.now();
      const r = await fetch(WORKER_BASE + "/", { cache: "no-store", signal: AbortSignal.timeout(8000) });
      const ms = (performance.now() - t0).toFixed(0);
      const txt = await r.text();
      const j = (() => { try { return JSON.parse(txt); } catch { return null; } })();
      if (j) qaLog(`Worker OK (${ms}ms) — endpoints: ${(j.endpoints || []).join(", ")}`, "ok");
      else   qaLog(`Worker responded ${r.status} (${ms}ms): ${txt.slice(0, 200)}`, r.ok ? "ok" : "err");
    } catch (e) { qaLog(`Worker ping failed: ${e.message}`, "err"); }
  }

  async function qaPingPocketBase() {
    qaLog("Pinging PocketBase /api/health...");
    try {
      const t0 = performance.now();
      const r = await fetch("https://josspatech.pockethost.io/api/health", { cache: "no-store", signal: AbortSignal.timeout(8000) });
      const ms = (performance.now() - t0).toFixed(0);
      const j = await r.json();
      qaLog(`PocketBase ${j.code === 200 ? "OK" : "?"} (${ms}ms) — ${j.message || JSON.stringify(j)}`, j.code === 200 ? "ok" : "err");
    } catch (e) { qaLog(`PocketBase ping failed: ${e.message}`, "err"); }
  }

  async function qaCheckQuotas() {
    qaLog("Re-fetching /health/quotas...");
    try {
      const r = await fetch(WORKER_BASE + "/health/quotas", { cache: "no-store", signal: AbortSignal.timeout(8000) });
      if (!r.ok) {
        qaLog(`/health/quotas returned HTTP ${r.status} — endpoint may not be deployed yet`, "err");
        return;
      }
      const j = await r.json();
      quotaCache = j;
      qaLog(`/health/quotas OK — ${Object.keys(j).length} services tracked: ${Object.keys(j).join(", ")}`, "ok");
      renderServices({}); // re-render the Services panel with the new data
    } catch (e) { qaLog(`/health/quotas failed: ${e.message}`, "err"); }
  }

  // ─── PBJ_SHARED_KEY storage (per-browser localStorage) ────
  // The Worker requires X-PBJ-Key on every auth-gated POST. The key
  // never lives in the HTML or in git — it's prompted on first use
  // and cached in localStorage. To rotate, click "Clear PBJ key" in
  // Quick Actions, then run any smoke test to be re-prompted.
  const PBJ_KEY_STORAGE = "pbj_shared_key";
  function getPbjKey() {
    const raw = localStorage.getItem(PBJ_KEY_STORAGE);
    const key = wmNormalizeSharedKey(raw);
    if (raw != null && raw !== key) {
      if (key) localStorage.setItem(PBJ_KEY_STORAGE, key);
      else localStorage.removeItem(PBJ_KEY_STORAGE);
    }
    if (key) return key;
    const entered = prompt(
      "Enter PBJ_SHARED_KEY (the Worker shared secret).\n\n" +
      "This is the value you set with `wrangler secret put PBJ_SHARED_KEY`.\n" +
      "Stored only in this browser's localStorage — never sent to GitHub.\n\n" +
      "Cancel to abort."
    );
    if (!entered) return null;
    const trimmed = wmNormalizeSharedKey(entered);
    if (trimmed.length < 8) {
      alert("That doesn't look long enough. Try again or paste the full value.");
      return null;
    }
    localStorage.setItem(PBJ_KEY_STORAGE, trimmed);
    return trimmed;
  }
  function clearPbjKey() {
    if (!confirm("Forget the stored PBJ_SHARED_KEY in this browser?")) return;
    localStorage.removeItem(PBJ_KEY_STORAGE);
    qaLog("PBJ key cleared from localStorage. Next smoke test will re-prompt.", "ok");
  }

  async function qaTestIdentify(category, description) {
    const app = HHH_IDENTIFY_CATEGORIES.includes(category)
      ? WORKER_APPS.find(a => a.id === "hhh")
      : WORKER_APPS.find(a => a.id === "cvc");
    if (!app) { qaLog(`Unknown identify category: ${category}`, "err"); return; }
    qaLog(`Testing ${app.short} /identify/${category} with description: "${description}"...`);
    const key = app.id === "pbj" ? getPbjKey() : wmGetKey(app, true);
    if (!key) { qaLog(`Aborted — no ${app.secretName} supplied.`, "err"); return; }
    const base = wmGetUrl(app);
    try {
      const t0 = performance.now();
      const r = await fetch(base + `/identify/${category}`, {
        method: "POST",
        headers: { "Content-Type": "application/json", [app.authHeader]: key },
        body: JSON.stringify({ description }),
        signal: AbortSignal.timeout(45000),
      });
      const ms = (performance.now() - t0).toFixed(0);
      if (r.status === 404) {
        qaLog(`${app.short} /identify/${category} returned 404 (${ms}ms) — deploy ${app.short} worker first.`, "err");
        return;
      }
      if (!r.ok) {
        qaLog(`${app.short} /identify/${category} returned HTTP ${r.status} (${ms}ms)`, "err");
        return;
      }
      const j = await r.json();
      const confDisplay = (typeof j.confidence === "number")
        ? (j.confidence * 100).toFixed(0) + "%"
        : (j.confidence || "?");
      const summary = j.success
        ? `success — brand=${j.brand || "?"}, model=${j.model || "?"}, confidence=${confDisplay}`
        : `success=false (${j.error || "model returned no usable identification"})`;
      qaLog(`${app.short} /identify/${category} responded in ${ms}ms — ${summary}`, "ok");
    } catch (e) { qaLog(`${app.short} /identify/${category} failed: ${e.message}`, "err"); }
  }

  async function qaSampleVision() {
    // Sample image: a 64x64 white JPEG (~600 bytes base64). Doesn't
    // contain a real receipt — just verifies the endpoint accepts
    // a payload and routes through Gemini Vision. Vision will say
    // "no receipt found" but should return success: false cleanly.
    qaLog("Testing /vision/receipt with a 64x64 placeholder image...");
    try {
      // Generate a tiny solid-color JPEG via canvas → dataURL → base64
      const c = document.createElement("canvas");
      c.width = 64; c.height = 64;
      const ctx = c.getContext("2d");
      ctx.fillStyle = "#FFFFFF"; ctx.fillRect(0, 0, 64, 64);
      ctx.fillStyle = "#000000"; ctx.font = "10px sans-serif";
      ctx.fillText("test", 4, 36);
      const dataUrl = c.toDataURL("image/jpeg", 0.7);
      const b64 = dataUrl.split(",")[1];
      const key = getPbjKey();
      if (!key) { qaLog("Aborted — no PBJ_SHARED_KEY supplied.", "err"); return; }
      const t0 = performance.now();
      const r = await fetch(WORKER_BASE + "/vision/receipt", {
        method: "POST",
        headers: { "Content-Type": "application/json", "X-PBJ-Key": key },
        body: JSON.stringify({ image: b64 }),
        signal: AbortSignal.timeout(45000),
      });
      const ms = (performance.now() - t0).toFixed(0);
      if (!r.ok) { qaLog(`/vision/receipt returned HTTP ${r.status} (${ms}ms)`, "err"); return; }
      const j = await r.json();
      const summary = j.success
        ? `parsed something (merchant=${j.merchant || "?"}, total=${j.total || "?"})`
        : `success=false (${j.error || "no fields extractable — expected for a blank image"})`;
      qaLog(`/vision/receipt responded in ${ms}ms — ${summary}`, "ok");
    } catch (e) { qaLog(`/vision/receipt failed: ${e.message}`, "err"); }
  }

  /* ─── Cron Health — read a heartbeat written by the hook ─────
     The aggregation hook writes to a `_cron_heartbeat` collection
     in PocketBase on every run. This card polls that collection
     and computes how recently each cron ticked. Honors the user
     having authenticated against PocketBase already (the existing
     dashboard's login flow stores a token in localStorage). */
  const CRON_HEARTBEATS_TO_TRACK = [
    { name: "aggregate_submissions", description: "Aggregation cron (hourly)" },
    { name: "retention",             description: "Retention cleanup (daily)" },
    { name: "anomaly_detection",     description: "Anomaly scan (hourly)" },
  ];

  function cronStateFromAge(minutes, expectedHourly) {
    if (minutes == null) return "unknown";
    const limit = expectedHourly ? 90 : 36 * 60; // hourly: 90 min OK, daily: 36 hrs OK
    if (minutes < limit)             return "green";
    if (minutes < limit * 2)         return "yellow";
    return "red";
  }



  /* ─── Teller Status & Cost — Worker /teller/stats ─────────── */
  async function loadTellerStatusPanel() {
    const root = document.getElementById("tellerStatusGrid");
    if (!root) return;

    const key = localStorage.getItem("pbj_shared_key") || "";
    if (!key) {
      root.innerHTML = `
        <div class="cron-card unknown">
          <div>
            <div class="cron-name">X-PBJ-Key not set in this browser</div>
            <div class="cron-last">Log in through the existing dashboard auth flow so the shared key is stored; this panel uses the same key.</div>
          </div>
        </div>`;
      return;
    }

    let stats = null;
    let httpStatus = 0;
    try {
      const r = await fetch(`${WORKER_BASE}/teller/stats`, {
        headers: { "X-PBJ-Key": key },
        signal: AbortSignal.timeout(8000),
      });
      httpStatus = r.status;
      if (r.ok) stats = await r.json();
    } catch (e) { /* network error */ }

    if (!stats) {
      root.innerHTML = `
        <div class="cron-card red">
          <div>
            <div class="cron-name">Could not load Teller stats (HTTP ${httpStatus || "network error"})</div>
            <div class="cron-last">Verify Worker is deployed and the X-PBJ-Key matches the Worker's PBJ_SHARED_KEY secret.</div>
          </div>
        </div>`;
      return;
    }

    const cardStyle = "background: var(--surface, #fff); border: 1px solid var(--border, rgba(0,0,0,0.1)); border-radius: 12px; padding: 16px;";
    const muted     = "color: var(--text-muted, #666); font-size: 12px;";
    const num       = "font-variant-numeric: tabular-nums; font-size: 18px; font-weight: 700;";

    const envBadgeColor = stats.environment === "production" ? "var(--danger, #dc2626)"
                        : stats.environment === "development" ? "var(--warning, #f59e0b)"
                        : "var(--success, #10b981)"; // sandbox default
    const whColor = stats.webhookHealth === "healthy" ? "var(--success, #10b981)"
                  : stats.webhookHealth === "stale"  ? "var(--danger, #dc2626)"
                  : "var(--text-muted, #666)";
    const whLabel = stats.webhookHealth === "healthy" ? "Healthy"
                  : stats.webhookHealth === "stale"  ? "Stale"
                  : "No data yet";

    function ago(iso) {
      if (!iso) return "never";
      const t = new Date(iso).getTime();
      if (!Number.isFinite(t)) return "never";
      const m = (Date.now() - t) / 60000;
      if (m < 1)    return "just now";
      if (m < 60)   return `${m.toFixed(0)} min ago`;
      if (m < 1440) return `${(m/60).toFixed(1)} hr ago`;
      return `${(m/1440).toFixed(1)} days ago`;
    }

    const notesHtml = stats.notes && stats.notes.length
      ? `<div style="${cardStyle} background: var(--surface-alt, #fffbe6); border-color: var(--warning, #f59e0b);">
           <strong style="display: block; margin-bottom: 6px;">Notes</strong>
           <ul style="margin: 0; padding-left: 20px; font-size: 13px; color: var(--text-secondary, #444);">
             ${stats.notes.map(n => `<li style="margin-bottom: 4px;">${n}</li>`).join("")}
           </ul>
         </div>`
      : "";

    root.innerHTML = `
      <div style="display: grid; gap: 14px;">
        <div style="${cardStyle}">
          <div style="display: flex; justify-content: space-between; align-items: baseline; margin-bottom: 10px; flex-wrap: wrap; gap: 12px;">
            <strong>Environment</strong>
            <span style="font-weight: 700; color: ${envBadgeColor}; text-transform: uppercase; letter-spacing: 1px;">
              ${stats.environment}
            </span>
          </div>
          <div style="${muted}">App ID: <code>${stats.appId}</code></div>
        </div>

        <div style="${cardStyle}">
          <strong style="display: block; margin-bottom: 10px;">Active enrollments &amp; estimated cost</strong>
          <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(180px, 1fr)); gap: 12px;">
            <div>
              <div style="${muted}">Active enrollments</div>
              <div style="${num}">${stats.active.toLocaleString()}</div>
              <div class="metric-hint">Users with a live bank link — counted on exchange, decremented on disconnect.</div>
            </div>
            <div>
              <div style="${muted}">Rate per connection</div>
              <div style="${num}">$${Number(stats.costPerConnectionUsd).toFixed(2)}/mo</div>
              <div class="metric-hint">From <code>TELLER_COST_PER_CONNECTION_USD</code> in wrangler.toml.</div>
            </div>
            <div>
              <div style="${muted}">Estimated monthly cost</div>
              <div style="${num}; color: ${stats.estimatedMonthlyCostUsd > 0 ? 'var(--danger, #dc2626)' : 'var(--text)'};">
                $${Number(stats.estimatedMonthlyCostUsd).toFixed(2)}
              </div>
              <div class="metric-hint">$0 in sandbox/dev — real only when <code>TELLER_ENV=production</code>.</div>
            </div>
          </div>
        </div>

        <div style="${cardStyle}">
          <div style="display: flex; justify-content: space-between; align-items: baseline; margin-bottom: 10px; flex-wrap: wrap; gap: 12px;">
            <strong>Webhook health</strong>
            <span style="font-weight: 700; color: ${whColor};">${whLabel}</span>
          </div>
          <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(180px, 1fr)); gap: 12px;">
            <div>
              <div style="${muted}">Last webhook</div>
              <div style="${num}">${ago(stats.lastWebhook)}</div>
              <div class="metric-hint">Last POST to <code>/teller/webhook</code> — stale with active enrollments = investigate.</div>
            </div>
            <div>
              <div style="${muted}">Webhooks today</div>
              <div style="${num}">${stats.today.webhooks.toLocaleString()}</div>
              <div class="metric-hint">Transaction/sync events received today (UTC).</div>
            </div>
            <div>
              <div style="${muted}">Webhooks MTD</div>
              <div style="${num}">${stats.month_to_date.webhooks.toLocaleString()}</div>
              <div class="metric-hint">Month-to-date webhook volume.</div>
            </div>
          </div>
          <div style="${muted}; margin-top: 10px;">
            Last exchange: ${ago(stats.lastExchange)} · Last disconnect: ${ago(stats.lastDisconnect)}
          </div>
        </div>

        ${notesHtml}

        ${panelUpgradeBox(["teller"], stats.environment === "production"
          ? `~$${Number(stats.estimatedMonthlyCostUsd).toFixed(2)}/mo at ${stats.active} active enrollments.`
          : "Sandbox/dev is $0 — switch TELLER_ENV to production in wrangler.toml when users connect real banks.")}

        <div style="${muted}; text-align: right;">Data fetched ${new Date().toLocaleTimeString()}</div>
      </div>
    `;
  }

  /* ─── OCR Quota & Cost — Worker /ocr/quota/stats (manual refresh) ── */
  function ocrRenderStats(stats) {
    const root = document.getElementById("ocrQuotaGrid");
    if (!root || !stats) return;

    const usedPct = stats.caps.globalDailyLimit > 0
      ? Math.min(100, (stats.today.total / stats.caps.globalDailyLimit) * 100)
      : 0;
    const barColor = usedPct >= 90 ? "var(--danger, #dc2626)"
                    : usedPct >= 75 ? "var(--warning, #f59e0b)"
                    : "var(--success, #10b981)";
    const cb = stats.today.circuitBreakerArmed;
    const costToday = Number(stats.today.estimatedCostUsd || 0);
    const costMtd   = Number(stats.month_to_date.estimatedCostUsd || 0);
    const cardStyle = "background: var(--surface, #fff); border: 1px solid var(--border, rgba(0,0,0,0.1)); border-radius: 12px; padding: 16px;";
    const muted = "color: var(--text-muted, #666); font-size: 12px;";
    const num = "font-variant-numeric: tabular-nums; font-size: 18px; font-weight: 700;";
    const histNote = Array.isArray(stats.cost_history) && stats.cost_history.length
      ? `${stats.cost_history.length} month(s) in cost_history`
      : "Cost graph history empty — use Heavy refresh";

    root.innerHTML = `
      <div style="display: grid; gap: 14px;">
        <div style="${cardStyle}">
          <div style="display: flex; justify-content: space-between; align-items: baseline; margin-bottom: 10px; gap: 12px; flex-wrap: wrap;">
            <strong>Today's global usage</strong>
            <span style="font-variant-numeric: tabular-nums;">
              ${stats.today.total.toLocaleString()} / ${stats.caps.globalDailyLimit.toLocaleString()}
              ${cb ? `<span style="color: var(--danger, #dc2626); font-weight: 700; margin-left: 8px;">⚠ breaker armed</span>` : ""}
            </span>
          </div>
          <div style="background: rgba(0,0,0,0.08); border-radius: 8px; height: 12px; overflow: hidden;">
            <div style="background: ${barColor}; height: 100%; width: ${usedPct.toFixed(1)}%; transition: width 0.3s;"></div>
          </div>
          <div style="display: flex; gap: 18px; margin-top: 10px; ${muted}; flex-wrap: wrap;">
            <div>OCR.Space: <strong style="color: var(--text); font-variant-numeric: tabular-nums;">${stats.today.space.toLocaleString()}</strong> / ${stats.freeTier.spaceDaily.toLocaleString()} free</div>
            <div>Gemini: <strong style="color: var(--text); font-variant-numeric: tabular-nums;">${stats.today.gemini.toLocaleString()}</strong> / ${stats.freeTier.geminiDaily.toLocaleString()} free</div>
          </div>
        </div>

        <div style="${cardStyle}">
          <strong style="display: block; margin-bottom: 10px;">Today's overage &amp; cost</strong>
          <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(180px, 1fr)); gap: 12px;">
            <div>
              <div style="${muted}">OCR.Space overage</div>
              <div style="${num}">${stats.today.overageSpace.toLocaleString()} calls</div>
              <div class="metric-hint">Calls beyond ${stats.freeTier.spaceDaily.toLocaleString()}/day free tier.</div>
            </div>
            <div>
              <div style="${muted}">Gemini overage</div>
              <div style="${num}">${stats.today.overageGemini.toLocaleString()} calls</div>
              <div class="metric-hint">Calls beyond ${stats.freeTier.geminiDaily.toLocaleString()}/day free tier.</div>
            </div>
            <div>
              <div style="${muted}">Estimated cost today</div>
              <div style="${num}; color: ${costToday > 0 ? 'var(--danger, #dc2626)' : 'var(--text)'};">$${costToday.toFixed(4)}</div>
              <div class="metric-hint">Overage × per-call rates in wrangler.toml — $0 under free caps.</div>
            </div>
          </div>
        </div>

        <div style="${cardStyle}">
          <strong style="display: block; margin-bottom: 10px;">Month-to-date</strong>
          <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(160px, 1fr)); gap: 12px;">
            <div>
              <div style="${muted}">Total calls</div>
              <div style="${num}">${stats.month_to_date.total.toLocaleString()}</div>
              <div class="metric-hint">All cloud OCR + vision calls this calendar month.</div>
            </div>
            <div>
              <div style="${muted}">OCR.Space</div>
              <div style="${num}">${stats.month_to_date.space.toLocaleString()}</div>
              <div class="metric-hint">OCR.Space leg only (stage-2 fallback).</div>
            </div>
            <div>
              <div style="${muted}">Gemini</div>
              <div style="${num}">${stats.month_to_date.gemini.toLocaleString()}</div>
              <div class="metric-hint">Gemini vision/parser leg.</div>
            </div>
            <div>
              <div style="${muted}">Estimated cost MTD</div>
              <div style="${num}; color: ${costMtd > 0 ? 'var(--danger, #dc2626)' : 'var(--text)'};">$${costMtd.toFixed(2)}</div>
              <div class="metric-hint">Running overage bill estimate — compare to Google/OCR invoices. ${histNote}.</div>            </div>
          </div>
        </div>

        <details style="${cardStyle}">
          <summary style="cursor: pointer; font-weight: 600;">Currently deployed caps &amp; rates</summary>
          <div style="margin-top: 12px; display: grid; grid-template-columns: repeat(auto-fit, minmax(220px, 1fr)); gap: 8px; font-size: 13px; font-variant-numeric: tabular-nums;">
            <div>Free monthly cap: <strong>${stats.caps.monthlyFree}</strong></div>
            <div>Trial monthly cap: <strong>${stats.caps.monthlyTrial}</strong></div>
            <div>Active monthly cap: <strong>${stats.caps.monthlyActive}</strong></div>
            <div>Per-device daily ceiling: <strong>${stats.caps.dailyCeiling}</strong></div>
            <div>Global circuit breaker: <strong>${stats.caps.globalDailyLimit}/day</strong></div>
            <div>OCR.Space free tier: <strong>${stats.freeTier.spaceDaily}/day</strong></div>
            <div>Gemini free tier: <strong>${stats.freeTier.geminiDaily}/day</strong></div>
            <div>OCR.Space rate: <strong>$${stats.rates.spaceUsd}/call</strong></div>
            <div>Gemini rate: <strong>$${stats.rates.geminiUsd}/call</strong></div>
          </div>
          <div style="margin-top: 12px; ${muted};">
            To adjust: edit the <code>OCR_*</code> lines in <code>cloudflare-worker/wrangler.toml</code>
            and run <code>wrangler deploy</code>. No app rebuild required.
          </div>
        </details>

        ${(usedPct >= 75 || cb) ? panelUpgradeBox(["gemini", "ocr_space", "wrangler"], cb ? "Circuit breaker armed — free users blocked from cloud OCR until UTC reset or you raise limits." : "") : ""}

        <div style="${muted}; text-align: right;">Data fetched ${ocrQuotaCache?.fetchedAt ? new Date(ocrQuotaCache.fetchedAt).toLocaleTimeString() : new Date().toLocaleTimeString()}</div>      </div>
    `;
  }

  function ocrRenderFromCache() {
    const root = document.getElementById("ocrQuotaGrid");
    const status = document.getElementById("ocrQuotaStatus");
    if (!root) return;
    const key = localStorage.getItem("pbj_shared_key") || "";
    if (!key) {
      root.innerHTML = `
        <div class="cron-card unknown">
          <div>
            <div class="cron-name">X-PBJ-Key not set in this browser</div>
            <div class="cron-last">Log in through the existing dashboard auth flow so the shared key is stored; this panel uses the same key.</div>
          </div>
        </div>`;
      return;
    }
    if (!ocrQuotaCache?.data) {
      root.innerHTML = "";
      if (status) status.textContent = "Click Refresh to load PBJ OCR quota from Worker KV.";
      return;
    }
    ocrRenderStats(ocrQuotaCache.data);
    if (status) {
      const label = ocrQuotaCache.costHistoryLoaded ? "Heavy (~20 KV reads)" : "Medium (~6 KV reads)";
      status.textContent = `Loaded · ${new Date(ocrQuotaCache.fetchedAt).toLocaleTimeString()} · ${label}`;
    }
  }

  async function ocrFetchTier(heavy) {
    const status = document.getElementById("ocrQuotaStatus");
    const pbj = WORKER_APPS.find(a => a.id === "pbj");
    if (!pbj) return;
    if (status) {
      status.textContent = heavy ? "Loading Heavy (cost graph)…" : "Loading Medium…";
      status.className = "ref-status";
    }
    const stats = await wmFetchStats(pbj, { costHistory: heavy });
    if (stats.error) {
      const root = document.getElementById("ocrQuotaGrid");
      if (root) {
        root.innerHTML = `
          <div class="cron-card red">
            <div>
              <div class="cron-name">Could not load OCR stats (${stats.error}${stats.status ? ` HTTP ${stats.status}` : ""})</div>
              <div class="cron-last">Verify Worker is deployed and the X-PBJ-Key in localStorage matches the Worker's PBJ_SHARED_KEY secret.</div>
            </div>
          </div>`;
      }
      if (status) {
        status.textContent = `Failed — ${stats.error}`;
        status.className = "ref-status err";
      }
      return;
    }
    ocrQuotaCache = {
      data: stats.data,
      costHistoryLoaded: heavy,
      fetchedAt: Date.now(),
    };
    ocrRenderFromCache();
    updateOpsAlertBanner().catch(() => {});
  }

  async function ocrRefreshMedium() { return ocrFetchTier(false); }
  async function ocrRefreshHeavy() { return ocrFetchTier(true); }

  function loadOcrQuotaPanel() {
    ocrRenderFromCache();
  }

  /* ─── OpenCellID Quota — Worker /opencellid/stats ──────────
     Daily cell-tower lookup counter. Free tier cap = 1,000/day;
     Worker caches each tower for 7 days so this only grows on
     new towers. Watch levels:
       <50%  green
       50-79% yellow
       >=80%  red
  */
  async function loadOpenCellIdPanel() {
    const root = document.getElementById("openCellIdGrid");
    if (!root) return;

    const key = localStorage.getItem("pbj_shared_key") || "";
    if (!key) {
      root.innerHTML = `
        <div class="cron-card unknown">
          <div>
            <div class="cron-name">X-PBJ-Key not set in this browser</div>
            <div class="cron-last">Log in through the existing dashboard auth flow so the shared key is stored; this panel uses the same key.</div>
          </div>
        </div>`;
      return;
    }

    let stats = null;
    let httpStatus = 0;
    try {
      const r = await fetch(`${WORKER_BASE}/opencellid/stats`, {
        headers: { "X-PBJ-Key": key },
        signal: AbortSignal.timeout(8000),
      });
      httpStatus = r.status;
      if (r.ok) stats = await r.json();
    } catch (e) { /* network error */ }

    if (!stats) {
      root.innerHTML = `
        <div class="cron-card red">
          <div>
            <div class="cron-name">Could not load OpenCellID stats (HTTP ${httpStatus || "network error"})</div>
            <div class="cron-last">Verify the Worker is deployed with the /opencellid/stats route and the X-PBJ-Key matches the Worker's PBJ_SHARED_KEY secret.</div>
          </div>
        </div>`;
      return;
    }

    const pct = Number(stats.pct_used) || 0;
    const cap = Number(stats.cap) || 0;
    const used = Number(stats.used_today) || 0;
    const remaining = Number(stats.remaining) || 0;
    const history = Array.isArray(stats.history) ? stats.history : [];

    let color, label;
    if (pct >= 80)      { color = "#dc2626"; label = "RED"; }
    else if (pct >= 50) { color = "#d97706"; label = "YELLOW"; }
    else                { color = "#16a34a"; label = "GREEN"; }

    const cardStyle = "background: #fff; border: 1px solid #e5e7eb; border-radius: 12px; padding: 18px;";
    const muted = "color: #6b7280; font-size: 12px;";

    // Mini sparkline: last 7 days as horizontal bars.
    const maxCount = Math.max(...history.map(h => Number(h.count) || 0), 1);
    const historyHtml = history.map(h => {
      const c = Number(h.count) || 0;
      const w = Math.round((c / maxCount) * 100);
      return `
        <div style="display: flex; align-items: center; gap: 10px; margin-bottom: 4px;">
          <div style="${muted}; width: 90px; flex-shrink: 0;">${h.date}</div>
          <div style="flex: 1; background: #f3f4f6; border-radius: 4px; height: 14px; overflow: hidden;">
            <div style="background: #60a5fa; height: 100%; width: ${w}%;"></div>
          </div>
          <div style="font-variant-numeric: tabular-nums; min-width: 50px; text-align: right;">${c}</div>
        </div>`;
    }).join("");

    root.innerHTML = `
      <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(260px, 1fr)); gap: 14px;">
        <div style="${cardStyle}">
          <div style="display: flex; justify-content: space-between; align-items: baseline; margin-bottom: 10px; flex-wrap: wrap; gap: 12px;">
            <strong>Today &mdash; ${stats.today}</strong>
            <span style="font-weight: 700; color: ${color};">${label}</span>
          </div>
          <div style="font-size: 32px; font-weight: 700; line-height: 1.1;">
            ${used.toLocaleString()} <span style="${muted}; font-weight: 400; font-size: 16px;">/ ${cap.toLocaleString()}</span>
          </div>
          <div style="${muted}; margin-top: 4px;">${pct}% used &mdash; ${remaining.toLocaleString()} remaining</div>
          <div class="metric-hint">Uncached tower lookups only — repeats hit 7-day KV cache.</div>
          <div style="margin-top: 12px; background: #f3f4f6; border-radius: 6px; height: 10px; overflow: hidden;">
            <div style="background: ${color}; height: 100%; width: ${Math.min(pct, 100)}%;"></div>
          </div>
        </div>

        <div style="${cardStyle}">
          <div style="margin-bottom: 10px;"><strong>Last 7 days</strong></div>
          ${historyHtml}
        </div>
      </div>
      ${pct >= 50 ? panelUpgradeBox(["opencellid", "wrangler"], pct >= 80 ? "At 100% the Worker refuses new lookups — GPS/IP fallback only." : "") : ""}
      <div style="${muted}; text-align: right; margin-top: 8px;">
        Data fetched ${new Date().toLocaleTimeString()} &middot;
        <a href="https://my.opencellid.org/dashboard" target="_blank" rel="noopener">OpenCellID Dashboard &rarr;</a>
      </div>
    `;
  }

  async function loadCronHealth() {
    const root = document.getElementById("cronHealthGrid");
    if (!root) return;
    root.innerHTML = `<div class="cron-card unknown"><div class="cron-name">Loading…</div></div>`;

    const authHdr = token ? { Authorization: `Bearer ${token}` } : {};
    let rows = [];
    let collectionMissing = false;
    let fetchNote = "";
    try {
      const r = await fetch("https://josspatech.pockethost.io/api/collections/_cron_heartbeat/records?perPage=50&sort=-last_run", {
        headers: authHdr,
        signal: AbortSignal.timeout(8000),
      });
      if (r.status === 404) {
        collectionMissing = true;
      } else if (r.status === 429) {
        fetchNote = "PocketBase rate-limited this poll — try again in ~15 min. Not an outage.";
      } else if (r.status === 401 || r.status === 403) {
        fetchNote = "Sign in to the dashboard to read _cron_heartbeat (PocketBase is up).";
      } else if (!r.ok) {
        fetchNote = `Could not read heartbeat (HTTP ${r.status}) — not necessarily a PocketBase outage.`;
      } else {
        const j = await r.json();
        rows = j.items || [];
      }
    } catch {
      fetchNote = "Network timeout reading cron heartbeat — check PocketBase /api/health separately.";
    }

    if (fetchNote) {
      root.innerHTML = `
        <div class="cron-card unknown">
          <div>
            <div class="cron-name">${fetchNote}</div>
            <div class="cron-last">Cron Health is PBJ flywheel housekeeping only — HHH/CVC workers are unaffected.</div>
          </div>
        </div>`;
      return;
    }

    if (collectionMissing) {
      root.innerHTML = `
        <div class="cron-card unknown">
          <div>
            <div class="cron-name"><code>_cron_heartbeat</code> not created yet — expected while <code>pb_hooks</code> isn't deployed</div>
            <div class="cron-last">When ready: PocketBase admin → New collection → <code>_cron_heartbeat</code> with <code>name</code> (text) + <code>last_run</code> (date). Upload aggregation hooks to PocketHost.</div>
          </div>
        </div>`;
      return;
    }

    const hooksNotDeployed = rows.length === 0;
    const byName = Object.fromEntries(rows.map(r => [r.name, r]));
    const cards = CRON_HEARTBEATS_TO_TRACK.map(c => {
      const row = byName[c.name];
      const lastRun = row?.last_run ? new Date(row.last_run) : null;
      const minutes = lastRun ? (Date.now() - lastRun.getTime()) / 60000 : null;
      const expectedHourly = c.name === "aggregate_submissions" || c.name === "anomaly_detection";
      const state = lastRun ? cronStateFromAge(minutes, expectedHourly) : "unknown";
      const stateLabel = !lastRun
        ? (hooksNotDeployed ? "Not configured yet (pb_hooks not deployed)" : "No heartbeat yet")
        : state === "green" ? "Healthy"
        : state === "yellow" ? "Possibly stale"
        : state === "red" ? "Stalled — investigate"
        : "Unknown";
      const timeStr = lastRun
        ? `Last: ${lastRun.toLocaleString()} (${minutes < 60 ? `${minutes.toFixed(0)} min` : `${(minutes/60).toFixed(1)} hr`} ago) — ${stateLabel}`
        : `${stateLabel}`;
      return `
        <div class="cron-card ${state}" style="margin-bottom: 10px;">
          <div>
            <div class="cron-name">${c.description} — <code>${c.name}</code></div>
            <div class="cron-last">${timeStr}</div>
          </div>
        </div>`;
    });
    root.innerHTML = cards.join("");
  }

  /* ─── Quarantine Watch — count of PII-flagged submissions ──── */
  async function loadQuarantineWatch() {
    const root = document.getElementById("quarantineWatchGrid");
    if (!root) return;
    root.innerHTML = `<div class="qw-card"><div class="qw-label">Loading…</div></div>`;

    const authHdr = token ? { Authorization: `Bearer ${token}` } : {};
    try {
      const r = await fetch("https://josspatech.pockethost.io/api/collections/_quarantine_submissions/records?perPage=1", {
        headers: authHdr,
        signal: AbortSignal.timeout(8000),
      });
      if (!r.ok) {
        root.innerHTML = `<div class="qw-card"><div class="qw-label">Couldn't read collection (HTTP ${r.status}). Are you logged in to PocketBase admin?</div></div>`;
        return;
      }
      const j = await r.json();
      const count = j.totalItems || 0;
      const cls = count === 0 ? "green" : count <= 10 ? "yellow" : "red";
      const countCls = count === 0 ? "" : count <= 10 ? "warn" : "crit";
      const advice = count === 0
        ? "No PII-flagged submissions. The aggregation hook's privacy guard is doing its job; nothing leaked into public collections."
        : count <= 10
          ? `${count} record${count === 1 ? "" : "s"} flagged for PII. Open the collection in PocketBase admin → review whether each is genuinely PII or a false-positive worth tuning the regex for.`
          : `${count} records flagged. Either users are submitting a lot of PII (concerning) or the hook's PII patterns are too aggressive (also concerning). Investigate.`;
      root.innerHTML = `
        <div class="qw-card ${cls}">
          <div class="qw-count ${countCls}">${count}</div>
          <div style="flex: 1;">
            <div style="font-weight: 700; color: var(--text); margin-bottom: 4px;">Quarantine submissions awaiting review</div>
            <div class="qw-label">${advice}</div>
          </div>
          <a class="m-btn" style="text-decoration: none; color: #fff; padding: 8px 14px;" href="https://josspatech.pockethost.io/_/#/collections?collection=_quarantine_submissions" target="_blank" rel="noopener noreferrer">Open in admin ↗</a>
        </div>`;
    } catch (e) {
      root.innerHTML = `<div class="qw-card"><div class="qw-label">Network error: ${e.message}</div></div>`;
    }
  }

  /* ─── Recent Commits — public + private repos when PAT set ────
     The website repo is public; commits are read without auth.
     App-source repos are private; reading their commits requires
     a fine-grained PAT with read-only "Contents" access on the
     specific repos. The PAT is stored in localStorage under the
     key `gh_pat` — set it once via:
        localStorage.setItem("gh_pat", "github_pat_xxxxxxxxxx")
     in the browser console. The token never gets committed to
     source because localStorage is per-browser.
     ──────────────────────────────────────────────────────────── */
  const GITHUB_REPOS = [
    // Public repo — always queried, no auth needed.
    { repo: "josspatech/josspatech.github.io", label: "Website",       isPrivate: false },
    // Private repos — only queried when a PAT is in localStorage.
    // Repo paths are placeholders; update if your repo names differ.
    { repo: "josspatech/PocketBudJet",         label: "PBJ source",    isPrivate: true },
    { repo: "josspatech/HandyHorology",        label: "HHH source",    isPrivate: true },
    { repo: "josspatech/CuratorsVault",        label: "CVC source",    isPrivate: true },
  ];

  async function loadRecentCommits() {
    const root = document.getElementById("recentCommitsGrid");
    if (!root) return;
    root.innerHTML = `<div class="commit-row"><div class="commit-sha">…</div><div class="commit-msg">Loading…</div><div class="commit-date"></div></div>`;

    const pat = (() => { try { return localStorage.getItem("gh_pat") || ""; } catch { return ""; } })();
    const headers = { "Accept": "application/vnd.github+json" };
    if (pat) headers["Authorization"] = `Bearer ${pat}`;

    // Walk repos in order. Skip private ones if no PAT. Build a flat
    // list of {repo, label, commit} entries, take the most recent
    // 8 across all repos.
    const all = [];
    let firstError = null;
    for (const r of GITHUB_REPOS) {
      if (r.isPrivate && !pat) continue;
      try {
        const resp = await fetch(`https://api.github.com/repos/${r.repo}/commits?per_page=3`, {
          headers, cache: "no-store", signal: AbortSignal.timeout(8000),
        });
        if (!resp.ok) {
          if (!firstError) firstError = `${r.label} returned HTTP ${resp.status}${resp.status === 404 ? " (repo not found or PAT lacks access)" : ""}`;
          continue;
        }
        const commits = await resp.json();
        for (const c of commits) all.push({ repo: r.label, ...c });
      } catch (e) {
        if (!firstError) firstError = `${r.label}: ${e.message}`;
      }
    }
    // Sort newest first across all repos and slice the top 8.
    all.sort((a, b) => {
      const ad = new Date(a.commit?.author?.date || 0).getTime();
      const bd = new Date(b.commit?.author?.date || 0).getTime();
      return bd - ad;
    });
    const top = all.slice(0, 8);

    if (top.length === 0) {
      const msg = pat
        ? (firstError || "No commits returned from any repo.")
        : "No PAT set; only the public website repo is queried. To include PBJ/HHH/CVC source repos, run in the browser console: <code>localStorage.setItem(\"gh_pat\", \"github_pat_…\")</code> with a fine-grained token scoped to read-only Contents on those repos.";
      root.innerHTML = `<div class="commit-row"><div class="commit-sha"></div><div class="commit-msg">${msg}</div><div class="commit-date"></div></div>`;
      return;
    }

    root.innerHTML = top.map(c => {
      const sha = c.sha?.slice(0, 7) || "—";
      const msg = (c.commit?.message || "").split("\n")[0];
      const url = c.html_url || "#";
      const dateStr = c.commit?.author?.date
        ? new Date(c.commit.author.date).toLocaleDateString("en-US", { month: "short", day: "numeric", year: "2-digit" })
        : "";
      return `
        <div class="commit-row" style="grid-template-columns: 80px 90px 1fr 90px;">
          <div class="commit-sha">${sha}</div>
          <div class="commit-sha" style="color: var(--primary); font-weight: 700;">${c.repo}</div>
          <div class="commit-msg"><a href="${url}" target="_blank" rel="noopener noreferrer">${msg.replace(/[<>]/g, "")}</a></div>
          <div class="commit-date">${dateStr}</div>
        </div>`;
    }).join("");

    if (!pat) {
      root.innerHTML += `<div class="commit-row" style="grid-template-columns: 1fr; padding: 8px 14px;"><div class="commit-msg" style="color: var(--text-muted); font-size: 11px; font-style: italic;">PBJ / HHH / CVC source repos hidden — set <code>gh_pat</code> in localStorage to include them.</div></div>`;
    }
  }

  /* ─── Quick Links — flat bookmarks of every admin URL ─────────
     Grouped by category. Each group becomes a card; each link
     becomes a row. Edit this array when a service is added or
     replaced; the panel re-renders automatically. */
  const QUICK_LINKS = [
    {
      group: "App stores & dev portals",
      links: [
        { label: "Apple App Store Connect",     url: "https://appstoreconnect.apple.com/" },
        { label: "Apple Developer Account",     url: "https://developer.apple.com/account/" },
        { label: "Apple Developer Members",     url: "https://developer.apple.com/membercenter/" },
        { label: "Google Play Console",         url: "https://play.google.com/console/" },
        { label: "Google Play — Closed testing", url: "https://play.google.com/console/u/0/developers/closed-testing" },
        { label: "BetaFamily (Play 12-tester gate)", url: "https://betafamily.com/" },
        { label: "TestFlight (Apple beta)",      url: "https://testflight.apple.com/" },
      ],
    },
    {
      group: "Build & deploy",
      links: [
        { label: "Expo / EAS dashboard",         url: "https://expo.dev/" },
        { label: "EAS — projects",               url: "https://expo.dev/accounts/josspatech/projects" },
        { label: "EAS — billing",                url: "https://expo.dev/accounts/josspatech/settings/billing" },
        { label: "Cloudflare dashboard",         url: "https://dash.cloudflare.com/" },
        { label: "Cloudflare — Workers",         url: "https://dash.cloudflare.com/?to=/:account/workers" },
        { label: "GitHub — josspatech profile",  url: "https://github.com/josspatech" },
        { label: "GitHub Status",                url: "https://www.githubstatus.com/" },
      ],
    },
    {
      group: "AI & API consoles",
      links: [
        { label: "Anthropic — API keys",         url: "https://console.anthropic.com/settings/keys" },
        { label: "Anthropic — usage",            url: "https://console.anthropic.com/settings/usage" },
        { label: "Anthropic — billing",          url: "https://console.anthropic.com/settings/billing" },
        { label: "Google AI Studio (Gemini)",    url: "https://aistudio.google.com/" },
        { label: "Google AI Studio — usage",     url: "https://aistudio.google.com/app/usage" },
        { label: "Google AI Studio — keys",      url: "https://aistudio.google.com/app/apikey" },
        { label: "Google Cloud — billing",       url: "https://console.cloud.google.com/billing" },
        { label: "OCR.Space — account",          url: "https://ocr.space/ocrapi" },
        { label: "OCR.Space — upgrade",          url: "https://ocr.space/ocrapi#price" },
      ],
    },
    {
      group: "Backend",
      links: [
        { label: "PocketBase admin (josspatech)", url: "https://josspatech.pockethost.io/_/" },
        { label: "PocketBase — health endpoint",  url: "https://josspatech.pockethost.io/api/health" },
        { label: "PocketHost dashboard",          url: "https://pockethost.io/dashboard" },
        { label: "PocketHost status",             url: "https://status.pockethost.io/" },
        { label: "Cloudflare Worker — health",    url: "https://pbj-import-worker.morning-star-b5e0.workers.dev/" },
      ],
    },
    {
      group: "Subscriptions & analytics",
      links: [
        { label: "RevenueCat dashboard",         url: "https://app.revenuecat.com/" },
        { label: "RevenueCat — projects",        url: "https://app.revenuecat.com/projects" },
        { label: "RevenueCat — pricing",         url: "https://www.revenuecat.com/pricing/" },
        { label: "Firebase — PBJ (PocketBudJet)", url: "https://console.firebase.google.com/project/pocketbudjet-b70f3" },
        { label: "Firebase — HHH (placeholder, set when configured)", url: "https://console.firebase.google.com/" },
        { label: "Firebase — CVC (placeholder, set when configured)", url: "https://console.firebase.google.com/" },
        { label: "Firebase — all projects",      url: "https://console.firebase.google.com/" },
      ],
    },
    {
      group: "Domain & website",
      links: [
        { label: "josspatech.com (live site)",   url: "https://josspatech.com/" },
        { label: "GitHub Pages repo",            url: "https://github.com/josspatech/josspatech.github.io" },
        { label: "Admin dashboard (this page)",  url: "https://josspatech.com/admin/josspatech-dashboard.html" },
      ],
    },
    {
      group: "Reference docs",
      links: [
        { label: "PocketBase docs",              url: "https://pocketbase.io/docs/" },
        { label: "Cloudflare Workers docs",      url: "https://developers.cloudflare.com/workers/" },
        { label: "Expo docs",                    url: "https://docs.expo.dev/" },
        { label: "Apple Human Interface guide",  url: "https://developer.apple.com/design/human-interface-guidelines/" },
        { label: "Material 3 design",            url: "https://m3.material.io/" },
      ],
    },
  ];

  function renderQuickLinks() {
    const grid = document.getElementById("quickLinksGrid");
    if (!grid) return;
    grid.innerHTML = QUICK_LINKS.map(g => {
      const links = g.links.map(l =>
        `<a class="ql-link" href="${l.url}" target="_blank" rel="noopener noreferrer">
           <span class="ql-label">${l.label}</span>
           <span class="ql-arrow">↗</span>
         </a>`
      ).join("");
      return `<div class="ql-group">
        <div class="ql-group-title">${g.group}</div>
        ${links}
      </div>`;
    }).join("");
  }

  /* ─── External services & status ──────────────────────────────
     Each entry describes a service the apps depend on. The optional
     `probe` field is a function that returns a Promise resolving to:
       { state: 'green'|'yellow'|'red'|'unknown',
         used?: number, limit?: number, unit?: string }
     - state alone: status-only card (no usage data available)
     - state + used + limit: shows a "used / limit" meter that colors
       green/yellow/red based on the percentage of capacity consumed
     Services without a probe show 'unknown' and rely on the user
     clicking through to their dashboard for a manual check.

     Bulk-loaded usage from the Worker's /health/quotas endpoint
     overrides individual probes when available — single network call
     gets capacity numbers for ALL the auth-gated services at once
     (Gemini, Anthropic, OCR.Space, RevenueCat). The Worker tallies
     them via Workers KV counters incremented on every proxied call.
     ──────────────────────────────────────────────────────────── */
  const WORKER_BASE = "https://pbj-import-worker.morning-star-b5e0.workers.dev";

  /** One-click vendor pages when quota is tight or something is red. */
  const VENDOR_BUY = {
    gemini: {
      key: "gemini",
      label: "Enable Gemini billing",
      url: "https://console.cloud.google.com/billing",
      hint: "Link a billing account in Google Cloud — free tier becomes pay-as-you-go for calls over 1,500/day.",
    },
    gemini_usage: {
      key: "gemini_usage",
      label: "Gemini usage dashboard",
      url: "https://aistudio.google.com/app/usage",
      hint: "See today's call count before you buy.",
    },
    anthropic: {
      key: "anthropic",
      label: "Top up Claude credits",
      url: "https://platform.claude.com/settings/billing",
      hint: "Pre-paid credits — HHH/CVC identify stops with 402 when empty.",
    },
    ocr_space: {
      key: "ocr_space",
      label: "Upgrade OCR.Space to PRO ($30/mo)",
      url: "https://ocr.space/ocrapi#price",
      hint: "300K calls/month + 5MB uploads vs 25K/mo free.",
    },
    cloudflare: {
      key: "cloudflare",
      label: "Cloudflare Workers paid ($5/mo)",
      url: "https://dash.cloudflare.com/",
      hint: "Workers & Pages → change plan if you hit 100K req/day.",
    },
    pockethost: {
      key: "pockethost",
      label: "Upgrade PocketHost plan",
      url: "https://pockethost.io/dashboard",
      hint: "More DB storage / CPU if crowd data grows past fair-use.",
    },
    opencellid: {
      key: "opencellid",
      label: "OpenCellID paid plan",
      url: "https://opencellid.org/#download",
      hint: "Raise daily lookup cap above 1,000/day.",
    },
    teller: {
      key: "teller",
      label: "Teller pricing (production)",
      url: "https://teller.io/pricing",
      hint: "~$2/active bank connection/mo when TELLER_ENV=production.",
    },
    revenuecat: {
      key: "revenuecat",
      label: "RevenueCat pricing",
      url: "https://www.revenuecat.com/pricing/",
      hint: "Free until ~$10K MTR; then 1% of tracked revenue.",
    },
    expo: {
      key: "expo",
      label: "Expo EAS billing",
      url: "https://expo.dev/accounts/josspatech/settings/billing",
      hint: "More than 30 iOS cloud builds/month.",
    },
    capacity: {
      key: "capacity",
      label: "Raise app caps (dashboard)",
      url: "#capacityControl",
      hint: "KV overrides via /ops/caps — no redeploy. Do this after enabling vendor billing.",
      internal: true,
    },
    wrangler: {
      key: "wrangler",
      label: "Raise caps in wrangler.toml",
      url: "#thresholdsBaselines",
      hint: "Defaults for new deploys — live caps are in Capacity Control.",
      internal: true,
    },
  };

  /** Vendor purchases with no /ops/caps — remind to raise app caps manually where applicable. */
  const VENDOR_ONLY_CAP_REMINDERS = [
    {
      service: "Anthropic Claude credits",
      buy: "anthropic",
      controllable: "HHH + CVC global AI cap (this dashboard)",
      remember: "After topping up credits, raise Global AI daily limit for HHH/CVC here if identify volume is high.",
    },
    {
      service: "Gemini billing (Google Cloud)",
      buy: "gemini",
      controllable: "PBJ global OCR + HHH/CVC global AI",
      remember: "Enable billing in GCP, then check billing box + Match caps (PBJ) or Growing preset (all apps).",
    },
    {
      service: "OCR.Space PRO",
      buy: "ocr_space",
      controllable: "PBJ global OCR cap",
      remember: "After PRO upgrade, check OCR.Space PRO + Match caps on the PBJ card.",
    },
    {
      service: "OpenCellID paid plan",
      buy: "opencellid",
      controllable: "PBJ OpenCellID daily cap",
      remember: "Raise OpenCellID daily cap on the PBJ card after vendor plan upgrade.",
    },
    {
      service: "Cloudflare Workers plan",
      buy: "cloudflare",
      controllable: "None (platform req/day)",
      remember: "No app cap to raise — upgrades Workers platform limits only.",
    },
    {
      service: "Teller bank connections",
      buy: "teller",
      controllable: "None",
      remember: "Per-connection billing only — no Worker OCR/AI cap.",
    },
    {
      service: "RevenueCat MTR",
      buy: "revenuecat",
      controllable: "None",
      remember: "Platform fee — does not affect API quotas.",
    },
    {
      service: "Expo EAS builds",
      buy: "expo",
      controllable: "None",
      remember: "Build minutes only — unrelated to runtime API caps.",
    },
    {
      service: "PocketHost / PocketBase",
      buy: "pockethost",
      controllable: "None",
      remember: "DB storage/CPU — crowd-data flywheel only, not OCR/AI caps.",
    },
    {
      service: "eBay Browse API",
      buy: null,
      controllable: "None (CVC)",
      remember: "Optional keys on CVC worker — no dashboard cap control yet.",
    },
  ];

  const UPGRADE_PLAYBOOK = [
    {
      service: "Gemini Flash",
      trigger: "Red banner ≥80% (1,200/1,500/day) or overage $ on OCR panel",
      steps: ["Enable billing in Google Cloud", "Optional: separate API key per app (CLOUD_KEYS.md)", "Or raise OCR_GLOBAL_DAILY_LIMIT in wrangler.toml if only the circuit breaker is the issue"],
      buy: ["gemini", "gemini_usage"],
    },
    {
      service: "Anthropic Claude",
      trigger: "Low balance log, 402 errors on identify, or red Anthropic card",
      steps: ["Open billing → Add credits", "Record new balance in the Anthropic service card on this dashboard"],
      buy: ["anthropic"],
    },
    {
      service: "OCR.Space",
      trigger: "Rate limits on receipt scan or OCR panel shows Space overage",
      steps: ["Upgrade to PRO on ocr.space", "Update OCR_SPACE_API_KEY worker secret if key changes"],
      buy: ["ocr_space"],
    },
    {
      service: "PBJ circuit breaker",
      trigger: "Red banner: circuit breaker ARMED — free users blocked",
      steps: ["Raise Global daily OCR in Capacity Control (Growing preset)", "Or enable Gemini billing + Match caps to vendor billing", "Premium/trial users keep working until global cap hits"],
      buy: ["capacity", "gemini"],
    },
    {
      service: "Cloudflare Workers",
      trigger: "429 rate limits or worker health red",
      steps: ["Cloudflare dashboard → Workers & Pages → upgrade to Paid ($5/mo)"],
      buy: ["cloudflare"],
    },
    {
      service: "PocketHost / PocketBase",
      trigger: "DB backup size growing or PocketHost warns on fair-use",
      steps: ["PocketHost dashboard → upgrade tier or migrate per HETZNER_MIGRATION_RUNBOOK"],
      buy: ["pockethost"],
    },
    {
      service: "OpenCellID",
      trigger: "OpenCellID panel ≥80% (800/1,000/day)",
      steps: ["Upgrade plan on OpenCellID", "Or raise OPENCELLID_DAILY_CAP in wrangler.toml temporarily"],
      buy: ["opencellid", "wrangler"],
    },
    {
      service: "Teller bank sync",
      trigger: "Real users connecting banks (production enrollments)",
      steps: ["Set TELLER_ENV=production in wrangler.toml", "Budget ~$2/active enrollment/mo"],
      buy: ["teller"],
    },
    {
      service: "RevenueCat",
      trigger: "Monthly tracked revenue passes ~$10K",
      steps: ["Automatic platform fee — review pricing page; no action until MTR threshold"],
      buy: ["revenuecat"],
    },
    {
      service: "Expo EAS",
      trigger: "Out of free 30 cloud builds/month",
      steps: ["Expo dashboard → Billing → upgrade build tier"],
      buy: ["expo"],
    },
  ];

  function vendorBuyLinkHtml(v, asButton) {
    if (!v) return "";
    const cls = asButton ? "ops-buy-btn" : "";
    const target = v.internal ? "" : ' target="_blank" rel="noopener noreferrer"';
    return `<a class="${cls}" href="${v.url}"${target} title="${v.hint || ""}">${v.label} ↗</a>`;
  }

  function vendorBuyKeysFromIssues(issues) {
    const keys = [];
    const seen = new Set();
    const add = (k) => { if (k && !seen.has(k)) { seen.add(k); keys.push(k); } };
    for (const raw of issues) {
      const i = String(raw).toLowerCase();
      if (i.includes("gemini")) add("gemini");
      if (i.includes("circuit breaker") || i.includes("ocr circuit") || i.includes("billing is marked on") || i.includes("capacity —")) {
        add("gemini");
        add("ocr_space");
        add("capacity");
      }
      if (i.includes("anthropic") || i.includes("claude") || i.includes("balance")) add("anthropic");
      if (i.includes("worker unreachable") || i.includes("worker health failed") || i.includes("health ping failed")) add("cloudflare");
      if (i.includes("ocr stats")) add("cloudflare");
    }
    if (keys.length === 0 && issues.length > 0) add("gemini");
    return keys;
  }

  function renderOpsBuyBar(issues) {
    const bar = document.getElementById("opsBuyBar");
    const btns = document.getElementById("opsBuyBtns");
    if (!bar || !btns) return;
    if (!issues || issues.length === 0) {
      bar.style.display = "none";
      btns.innerHTML = "";
      return;
    }
    const keys = vendorBuyKeysFromIssues(issues);
    btns.innerHTML = keys.map(k => vendorBuyLinkHtml(VENDOR_BUY[k], true)).join("") +
      `<a class="ops-buy-btn secondary" href="flywheel.html#capacityControl">Raise app caps ↓</a>` +
      `<a class="ops-buy-btn secondary" href="flywheel.html#upgradePlaybook">Upgrade playbook ↓</a>`;
    bar.style.display = "block";
  }

  function panelUpgradeBox(buyKeys, extraNote) {
    if (!buyKeys || !buyKeys.length) return "";
    const links = buyKeys.map(k => vendorBuyLinkHtml(VENDOR_BUY[k], false)).join(" · ");
    return `<div class="panel-upgrade-box"><strong>Need more capacity?</strong> ${links}${extraNote ? `<br>${extraNote}` : ""}</div>`;
  }

  function renderUpgradePlaybook() {
    const root = document.getElementById("upgradePlaybookGrid");
    if (!root) return;
    root.innerHTML = `
      <table>
        <thead>
          <tr>
            <th>Service</th>
            <th>When it goes red</th>
            <th>What to do</th>
            <th>Buy / fix (one click)</th>
          </tr>
        </thead>
        <tbody>
          ${UPGRADE_PLAYBOOK.map(row => `
            <tr>
              <td><strong>${row.service}</strong></td>
              <td>${row.trigger}</td>
              <td><ul>${row.steps.map(s => `<li>${s}</li>`).join("")}</ul></td>
              <td class="up-links">${row.buy.map(k => vendorBuyLinkHtml(VENDOR_BUY[k], false)).join("<br>")}</td>
            </tr>
          `).join("")}
        </tbody>
      </table>`;
  }

  function renderVendorOnlyCapReminders() {
    const root = document.getElementById("vendorOnlyCapGrid");
    if (!root) return;
    root.innerHTML = `
      <table>
        <thead>
          <tr>
            <th>Vendor / service</th>
            <th>Buy link</th>
            <th>App cap you can raise here</th>
            <th>After you buy — remember</th>
          </tr>
        </thead>
        <tbody>
          ${VENDOR_ONLY_CAP_REMINDERS.map(row => `
            <tr>
              <td><strong>${row.service}</strong></td>
              <td>${row.buy ? vendorBuyLinkHtml(VENDOR_BUY[row.buy], false) : "—"}</td>
              <td>${row.controllable}</td>
              <td class="remember">${row.remember}</td>
            </tr>
          `).join("")}
        </tbody>
      </table>`;
  }

  let capacityCache = { pbj: null, hhh: null, cvc: null };

  async function capFetch(app) {
    const key = wmGetKey(app, false);
    const base = wmGetUrl(app);
    if (!key) return { error: "no_key", message: `${app.authHeader} not set — run a ${app.short} smoke test once.` };
    try {
      const r = await fetch(`${base}/ops/caps`, {
        headers: { [app.authHeader]: key },
        signal: AbortSignal.timeout(10000),
      });
      if (r.status === 404) {
        return { error: "not_deployed", message: `${app.short} /ops/caps not deployed yet — run wrangler deploy.` };
      }
      if (!r.ok) {
        const t = await r.text();
        return { error: "http", message: `HTTP ${r.status}: ${t.slice(0, 120)}` };
      }
      return await r.json();
    } catch (e) {
      return { error: "network", message: e instanceof Error ? e.message : String(e) };
    }
  }

  async function capPut(app, body) {
    const key = wmGetKey(app, true);
    const base = wmGetUrl(app);
    const r = await fetch(`${base}/ops/caps`, {
      method: "PUT",
      headers: { "Content-Type": "application/json", [app.authHeader]: key },
      body: JSON.stringify(body),
      signal: AbortSignal.timeout(12000),
    });
    if (!r.ok) {
      const t = await r.text();
      throw new Error(`HTTP ${r.status}: ${t.slice(0, 200)}`);
    }
    return r.json();
  }

  function capBnHtml(bn) {
    const cls = bn.severity === "critical" ? "critical" : "";
    return `<div class="cap-bn ${cls}"><strong>${bn.message}</strong><br><span style="color:var(--text-muted)">Fix: ${bn.fix}</span></div>`;
  }

  function capField(id, label, value, def) {
    return `<div class="cap-field-row">
      <label for="${id}">${label} <span style="color:var(--text-muted)">(default ${def})</span></label>
      <input type="number" id="${id}" min="1" value="${value}">
    </div>`;
  }

  function renderPbjCapCard(app, data) {
    if (data.error) {
      return `<div class="cap-card"><h3>${app.short} — ${app.name}</h3><p style="color:var(--warning);font-size:12px;">${data.message}</p></div>`;
    }
    const eff = data.effective || {};
    const def = data.defaults || {};
    const usage = data.usage || {};
    const preset = data.preset || "prelaunch";
    const vb = data.vendorBilling || {};
    const bns = (data.bottlenecks || []).map(capBnHtml).join("");
    return `<div class="cap-card" id="cap-card-pbj">
      <h3>${app.short} — OCR &amp; OpenCellID caps</h3>
      <div class="cap-meta">Preset: <strong>${preset}</strong>${data.overrides?.updatedAt ? ` · updated ${new Date(data.overrides.updatedAt).toLocaleString()}` : ""}</div>
      <div class="cap-usage">
        Global OCR today: <strong>${usage.globalOcrToday ?? "—"}</strong> / ${eff.globalDailyLimit ?? "—"}
        (${(usage.appGlobalPct ?? 0).toFixed(0)}%)
        · Gemini vendor ${(usage.vendorGeminiPct ?? 0).toFixed(0)}%
        · Space ${(usage.vendorSpacePct ?? 0).toFixed(0)}%
        ${usage.circuitBreakerArmed ? " · <span style='color:var(--danger)'>CIRCUIT BREAKER</span>" : ""}
      </div>
      ${bns}
      <div class="cap-preset-row">
        ${["prelaunch", "growing", "scale"].map(p =>
          `<button type="button" class="m-btn${preset === p ? " active" : ""}" onclick="capApplyPreset('pbj','${p}')">${p}</button>`
        ).join("")}
      </div>
      ${capField("cap-pbj-free", "Monthly free", eff.monthlyFree, def.monthlyFree)}
      ${capField("cap-pbj-trial", "Monthly trial", eff.monthlyTrial, def.monthlyTrial)}
      ${capField("cap-pbj-active", "Monthly pro", eff.monthlyActive, def.monthlyActive)}
      ${capField("cap-pbj-daily", "Daily ceiling / user", eff.dailyCeiling, def.dailyCeiling)}
      ${capField("cap-pbj-global", "Global daily OCR", eff.globalDailyLimit, def.globalDailyLimit)}
      ${capField("cap-pbj-oci", "OpenCellID daily", eff.opencellidDailyCap, def.opencellidDailyCap)}
      <label class="cap-vendor-chk"><input type="checkbox" id="cap-pbj-vb-gemini" ${vb.gemini ? "checked" : ""}> Gemini billing enabled</label>
      <label class="cap-vendor-chk"><input type="checkbox" id="cap-pbj-vb-space" ${vb.ocr_space ? "checked" : ""}> OCR.Space PRO</label>
      <div class="cap-action-row">
        <button type="button" class="m-btn accent" onclick="capSaveCustom('pbj')">Save caps</button>
        <button type="button" class="m-btn" onclick="capMatchVendor('pbj')">Match caps to vendor billing</button>
        <button type="button" class="m-btn" onclick="loadCapacityControl()">Refresh</button>
      </div>
    </div>`;
  }

  function renderAiCapCard(app, data) {
    if (data.error) {
      return `<div class="cap-card"><h3>${app.short} — ${app.name}</h3><p style="color:var(--warning);font-size:12px;">${data.message}</p></div>`;
    }
    const eff = data.effective || {};
    const def = data.defaults || {};
    const usage = data.usage || {};
    const preset = data.preset || "prelaunch";
    const vb = data.vendorBilling || {};
    const bns = (data.bottlenecks || []).map(capBnHtml).join("");
    return `<div class="cap-card" id="cap-card-${app.id}">
      <h3>${app.short} — Global AI cap</h3>
      <div class="cap-meta">Preset: <strong>${preset}</strong>${data.overrides?.updatedAt ? ` · updated ${new Date(data.overrides.updatedAt).toLocaleString()}` : ""}</div>
      <div class="cap-usage">
        Global AI today: <strong>${usage.globalAiToday ?? "—"}</strong> / ${eff.globalDailyLimit ?? "—"}
        (${(usage.appGlobalPct ?? 0).toFixed(0)}%)
        · Gemini vendor ${(usage.vendorGeminiPct ?? 0).toFixed(0)}%
        ${usage.circuitBreakerArmed ? " · <span style='color:var(--danger)'>CIRCUIT BREAKER</span>" : ""}
      </div>
      ${bns}
      <div class="cap-preset-row">
        ${["prelaunch", "growing", "scale"].map(p =>
          `<button type="button" class="m-btn${preset === p ? " active" : ""}" onclick="capApplyPreset('${app.id}','${p}')">${p}</button>`
        ).join("")}
      </div>
      ${capField(`cap-${app.id}-global`, "Global daily AI", eff.globalDailyLimit, def.globalDailyLimit)}
      <label class="cap-vendor-chk"><input type="checkbox" id="cap-${app.id}-vb-gemini" ${vb.gemini ? "checked" : ""}> Gemini billing enabled</label>
      <label class="cap-vendor-chk"><input type="checkbox" id="cap-${app.id}-vb-anthropic" ${vb.anthropic ? "checked" : ""}> Anthropic credits topped up</label>
      <div class="cap-action-row">
        <button type="button" class="m-btn accent" onclick="capSaveCustom('${app.id}')">Save cap</button>
        <button type="button" class="m-btn" onclick="capMatchVendor('${app.id}')">Match caps to vendor billing</button>
        <button type="button" class="m-btn" onclick="loadCapacityControl()">Refresh</button>
      </div>
    </div>`;
  }

  function renderCapacityBottleneckBanner() {
    const banner = document.getElementById("capacityBottleneckBanner");
    if (!banner) return;
    const all = [];
    for (const id of ["pbj", "hhh", "cvc"]) {
      const d = capacityCache[id];
      if (!d || d.error || !d.bottlenecks) continue;
      for (const bn of d.bottlenecks) {
        if (bn.severity === "critical" || bn.severity === "warning") {
          all.push({ app: id.toUpperCase(), ...bn });
        }
      }
    }
    if (all.length === 0) {
      banner.style.display = "none";
      banner.innerHTML = "";
      return;
    }
    const hasCritical = all.some(b => b.severity === "critical");
    banner.className = hasCritical ? "capacity-bottleneck-banner" : "capacity-bottleneck-banner warn";
    banner.innerHTML =
      `<strong>${hasCritical ? "App cap bottleneck — users may be failing now" : "Capacity warning — vendor may look fine, app cap may not"}</strong>` +
      `<ul>${all.map(b => `<li><strong>${b.app}:</strong> ${b.message} — ${b.fix}</li>`).join("")}</ul>`;
    banner.style.display = "block";
  }

  async function loadCapacityControl() {
    const grid = document.getElementById("capacityControlGrid");
    if (!grid) return;
    grid.innerHTML = '<div style="color:var(--text-muted);font-size:13px;">Loading…</div>';
    const results = await Promise.all(WORKER_APPS.map(app => capFetch(app)));
    WORKER_APPS.forEach((app, i) => { capacityCache[app.id] = results[i]; });
    grid.innerHTML = WORKER_APPS.map((app, i) =>
      app.id === "pbj" ? renderPbjCapCard(app, results[i]) : renderAiCapCard(app, results[i])
    ).join("");
    renderCapacityBottleneckBanner();
    renderVendorOnlyCapReminders();
  }

  async function capApplyPreset(appId, preset) {
    const app = WORKER_APPS.find(a => a.id === appId);
    if (!app) return;
    try {
      const data = await capPut(app, { preset });
      capacityCache[appId] = data;
      qaLog(`${app.short} caps → preset "${preset}" applied.`, "ok");
      await loadCapacityControl();
      updateOpsAlertBanner().catch(() => {});
    } catch (e) {
      qaLog(`${app.short} cap preset failed: ${e.message}`, "err");
    }
  }

  async function capMatchVendor(appId) {
    const app = WORKER_APPS.find(a => a.id === appId);
    if (!app) return;
    const body = { matchVendorBilling: true };
    if (appId === "pbj") {
      body.vendorBilling = {
        gemini: document.getElementById("cap-pbj-vb-gemini")?.checked ?? false,
        ocr_space: document.getElementById("cap-pbj-vb-space")?.checked ?? false,
      };
    } else {
      body.vendorBilling = {
        gemini: document.getElementById(`cap-${appId}-vb-gemini`)?.checked ?? false,
        anthropic: document.getElementById(`cap-${appId}-vb-anthropic`)?.checked ?? false,
      };
    }
    try {
      const data = await capPut(app, body);
      capacityCache[appId] = data;
      qaLog(`${app.short} caps matched to vendor billing flags.`, "ok");
      await loadCapacityControl();
      updateOpsAlertBanner().catch(() => {});
    } catch (e) {
      qaLog(`${app.short} match vendor failed: ${e.message}`, "err");
    }
  }

  async function capSaveCustom(appId) {
    const app = WORKER_APPS.find(a => a.id === appId);
    if (!app) return;
    const body = { overrides: {}, vendorBilling: {} };
    if (appId === "pbj") {
      const fields = [
        ["monthlyFree", "cap-pbj-free"],
        ["monthlyTrial", "cap-pbj-trial"],
        ["monthlyActive", "cap-pbj-active"],
        ["dailyCeiling", "cap-pbj-daily"],
        ["globalDailyLimit", "cap-pbj-global"],
        ["opencellidDailyCap", "cap-pbj-oci"],
      ];
      for (const [k, elId] of fields) {
        const n = parseInt(document.getElementById(elId)?.value ?? "", 10);
        if (Number.isFinite(n) && n > 0) body.overrides[k] = n;
      }
      body.vendorBilling = {
        gemini: document.getElementById("cap-pbj-vb-gemini")?.checked ?? false,
        ocr_space: document.getElementById("cap-pbj-vb-space")?.checked ?? false,
      };
    } else {
      const n = parseInt(document.getElementById(`cap-${appId}-global`)?.value ?? "", 10);
      if (Number.isFinite(n) && n > 0) body.overrides.globalDailyLimit = n;
      body.vendorBilling = {
        gemini: document.getElementById(`cap-${appId}-vb-gemini`)?.checked ?? false,
        anthropic: document.getElementById(`cap-${appId}-vb-anthropic`)?.checked ?? false,
      };
    }
    try {
      const data = await capPut(app, body);
      capacityCache[appId] = data;
      qaLog(`${app.short} custom caps saved.`, "ok");
      await loadCapacityControl();
      updateOpsAlertBanner().catch(() => {});
    } catch (e) {
      qaLog(`${app.short} save caps failed: ${e.message}`, "err");
    }
  }

  function capacityIssuesFromCache() {
    const issues = [];
    for (const app of WORKER_APPS) {
      const d = capacityCache[app.id];
      if (!d || d.error || !d.bottlenecks) continue;
      for (const bn of d.bottlenecks) {
        if (bn.severity !== "critical" && bn.severity !== "warning") continue;
        if (bn.code === "billing_on_caps_not_raised") {
          issues.push(`${app.short} — ${bn.message}`);
        } else if (bn.code === "circuit_breaker_armed") {
          issues.push(`${app.short} — ${bn.message}`);
        } else if (bn.code === "global_cap_high" || bn.code === "vendor_headroom_app_low") {
          issues.push(`${app.short} capacity — ${bn.message}`);
        }
      }
    }
    return issues;
  }

  /* ─── Per-app Worker Monitoring (PBJ · HHH · CVC) ─────────── */
  const WORKER_APPS = [
    {
      id: "pbj",
      short: "PBJ",
      name: "Pocket Budget Journal",
      defaultUrl: WORKER_BASE,
      urlKey: "pbj_worker_url",
      keyKey: "pbj_shared_key",
      secretName: "PBJ_SHARED_KEY",
      authHeader: "X-PBJ-Key",
      statsKind: "ocr",
    },
    {
      id: "hhh",
      short: "HHH",
      name: "Handy Horology Helper",
      defaultUrl: "https://handyhorology-worker.morning-star-b5e0.workers.dev",
      urlKey: "hhh_worker_url",
      keyKey: "hhh_shared_key",
      secretName: "HHH_SHARED_KEY",
      authHeader: "X-HHH-Key",
      statsKind: "ops",
    },
    {
      id: "cvc",
      short: "CVC",
      name: "Curator's Vault",
      defaultUrl: "https://cvc-worker.morning-star-b5e0.workers.dev",
      urlKey: "cvc_worker_url",
      keyKey: "cvc_shared_key",
      secretName: "CVC_SHARED_KEY",
      authHeader: "X-CVC-Key",
      statsKind: "ops",
    },
  ];
  const HHH_IDENTIFY_CATEGORIES = ["watch", "clock"];
  let wmActiveTab = localStorage.getItem("wm_active_tab") || "pbj";

  function wmGetUrl(app) {
    return (localStorage.getItem(app.urlKey) || app.defaultUrl).replace(/\/$/, "");
  }

  function wmSaveUrl(appId) {
    const app = WORKER_APPS.find(a => a.id === appId);
    if (!app) return;
    const input = document.getElementById(`wm-url-${appId}`);
    const val = (input?.value || "").trim().replace(/\/$/, "");
    if (!val) {
      localStorage.removeItem(app.urlKey);
      qaLog(`${app.short} worker URL reset to default.`, "ok");
    } else {
      localStorage.setItem(app.urlKey, val);
      qaLog(`${app.short} worker URL saved: ${val}`, "ok");
    }
    wmCache = null;
    wmRenderFromCache();
  }

  function wmNormalizeSharedKey(raw) {
    let s = String(raw ?? "").trim();
    if (!s) return "";
    const nl = s.search(/[\r\n]/);
    if (nl >= 0) s = s.slice(0, nl).trim();
    const tsAssign = s.match(
      /(?:export\s+)?const\s+(?:WORKER_SHARED_KEY|PBJ_SHARED_KEY|HHH_SHARED_KEY|CVC_SHARED_KEY)\s*=\s*['"]([a-f0-9]{32,128})['"]\s*;?/i,
    );
    if (tsAssign) return tsAssign[1];
    if (/^export\s+/i.test(s)) s = s.replace(/^export\s+/i, "").trim();
    const eq = s.indexOf("=");
    if (eq > 0) {
      const name = s.slice(0, eq).trim().replace(/^const\s+/i, "");
      let val = s.slice(eq + 1).trim().replace(/;+\s*$/, "");
      if ((val.startsWith('"') && val.endsWith('"')) || (val.startsWith("'") && val.endsWith("'"))) {
        val = val.slice(1, -1).trim();
      }
      if (/^(EXPO_PUBLIC_(?:PBJ|HHH|CVC)_WORKER_(?:KEY|URL)|PBJ_SHARED_KEY|HHH_SHARED_KEY|CVC_SHARED_KEY)$/i.test(name)) {
        s = val;
      } else if (/(?:SHARED_KEY|WORKER_KEY)$/i.test(name) && /^[a-f0-9]{32,128}$/i.test(val)) {
        s = val;
      }
    }
    if ((s.startsWith('"') && s.endsWith('"')) || (s.startsWith("'") && s.endsWith("'"))) {
      s = s.slice(1, -1).trim();
    }
    return s;
  }

  const WM_LEGACY_KEY_ALIASES = {
    pbj: ["PBJ_SHARED_KEY", "EXPO_PUBLIC_PBJ_WORKER_KEY"],
    hhh: ["HHH_SHARED_KEY", "EXPO_PUBLIC_HHH_WORKER_KEY"],
    cvc: ["CVC_SHARED_KEY", "EXPO_PUBLIC_CVC_WORKER_KEY"],
  };

  function wmHealStoredWorkerKey(app) {
    let key = wmNormalizeSharedKey(localStorage.getItem(app.keyKey));
    const legacy = WM_LEGACY_KEY_ALIASES[app.id] || [];
    if (!key) {
      for (const alias of legacy) {
        const fromLegacy = wmNormalizeSharedKey(localStorage.getItem(alias));
        if (fromLegacy) {
          key = fromLegacy;
          break;
        }
      }
    }
    const raw = localStorage.getItem(app.keyKey);
    if (key) {
      if (raw !== key) localStorage.setItem(app.keyKey, key);
      for (const alias of legacy) localStorage.removeItem(alias);
      return key;
    }
    if (raw != null && raw !== "") localStorage.removeItem(app.keyKey);
    for (const alias of legacy) {
      const lr = localStorage.getItem(alias);
      if (lr != null && lr !== "") localStorage.removeItem(alias);
    }
    return "";
  }

  function wmGetKey(app, promptIfMissing) {
    let key = wmHealStoredWorkerKey(app);
    if (key || !promptIfMissing) return key || "";
    const entered = prompt(
      `Enter ${app.secretName} for ${app.name}.\n\n` +
      `Set via wrangler secret put ${app.secretName} on the ${app.short} worker.\n` +
      `Stored only in this browser — never sent to GitHub.\n\nCancel to skip.`,
    );
    if (!entered) return "";
    const trimmed = wmNormalizeSharedKey(entered);
    if (trimmed.length < 8) {
      alert("That doesn't look long enough. Paste the full shared key.");
      return "";
    }
    localStorage.setItem(app.keyKey, trimmed);
    return trimmed;
  }

  function wmClearKey(appId) {
    const app = WORKER_APPS.find(a => a.id === appId);
    if (!app) return;
    if (!confirm(`Forget ${app.secretName} for ${app.name} in this browser?`)) return;
    localStorage.removeItem(app.keyKey);
    qaLog(`${app.short} key cleared. Next stats fetch will re-prompt.`, "ok");
    wmCache = null;
    wmRenderFromCache();
  }

  function wmBarColor(pct, breaker) {
    if (breaker || pct >= 90) return "var(--danger)";
    if (pct >= 75) return "var(--warning)";
    return "var(--success)";
  }

  function wmCardState(health, metrics) {
    if (!health.ok) return "red";
    if (health.gemini_configured === false) return "yellow";
    if (metrics?.circuitBreaker) return "red";
    const pct = Math.max(metrics?.geminiPct || 0, metrics?.quotaPct || 0);
    if (pct >= 90) return "red";
    if (pct >= 75) return "yellow";
    return "green";
  }

  async function wmFetchHealth(app) {
    const url = wmGetUrl(app);
    try {
      const r = await fetch(url + "/", { cache: "no-store", signal: AbortSignal.timeout(8000) });
      if (!r.ok) return { state: "red", ok: false, httpStatus: r.status, url };
      const j = await r.json();
      const geminiOk = j.gemini_configured !== false;
      return {
        state: j.ok ? (geminiOk ? "green" : "yellow") : "red",
        ok: j.ok === true,
        service: j.service || app.short,
        gemini_configured: j.gemini_configured,
        url,
      };
    } catch {
      return { state: "red", ok: false, error: "network", url };
    }
  }

  async function wmFetchStats(app, { costHistory = false } = {}) {
    const url = wmGetUrl(app);
    const path = app.statsKind === "ocr" ? "/ocr/quota/stats" : "/ops/stats";
    const qs = costHistory ? "?cost_history=1" : "";
    const fetchOnce = async (key) => {
      const r = await fetch(url + path + qs, {
        headers: { [app.authHeader]: key },
        signal: AbortSignal.timeout(8000),
      });
      if (r.status === 401) return { error: "auth", status: 401 };
      if (!r.ok) return { error: "http", status: r.status };
      return { data: await r.json() };
    };
    let key = wmGetKey(app, false);
    if (!key) return { error: "no_key" };
    try {
      let result = await fetchOnce(key);
      if (result.error === "auth") {
        const healed = wmHealStoredWorkerKey(app);
        if (healed && healed !== key) result = await fetchOnce(healed);
      }
      return result;
    } catch {
      return { error: "network" };
    }
  }

  function wmNormalizeMetrics(app, statsData) {
    if (!statsData) return null;
    if (app.statsKind === "ocr") {
      const s = statsData;
      const geminiCap = s.freeTier?.geminiDaily || 1500;
      const geminiPct = geminiCap > 0 ? (s.today.gemini / geminiCap) * 100 : 0;
      const globalCap = s.caps?.globalDailyLimit || 1800;
      const quotaPct = globalCap > 0 ? (s.today.total / globalCap) * 100 : 0;
      return {
        geminiToday: s.today.gemini,
        geminiCap,
        geminiPct,
        anthropicToday: null,
        costToday: Number(s.today.estimatedCostUsd || 0),
        costMtd: Number(s.month_to_date?.estimatedCostUsd || 0),
        costHistory: Array.isArray(s.cost_history) ? s.cost_history : [],
        circuitBreaker: s.today.circuitBreakerArmed,
        quotaPct,
        quotaLabel: "Global OCR daily",
        quotaUsed: s.today.total,
        quotaCap: globalCap,
        spaceToday: s.today.space,
      };
    }
    const s = statsData;
    const geminiCap = s.caps?.geminiDaily || 1500;
    const geminiPct = geminiCap > 0 ? (s.today.gemini / geminiCap) * 100 : 0;
    const globalCap = s.caps?.globalDailyLimit || 500;
    const quotaPct = globalCap > 0 ? (s.today.total / globalCap) * 100 : 0;
    return {
      geminiToday: s.today.gemini,
      geminiCap,
      geminiPct,
      anthropicToday: s.today.anthropic,
      anthropicCap: s.caps?.anthropicDaily || 5000,
      costToday: Number(s.today.estimatedCostUsd || 0),
      costMtd: Number(s.month_to_date?.estimatedCostUsd || 0),
      costHistory: Array.isArray(s.cost_history) ? s.cost_history : [],
      circuitBreaker: s.today.circuitBreakerArmed,
      quotaPct,
      quotaLabel: "Global AI daily",
      quotaUsed: s.today.total,
      quotaCap: globalCap,
    };
  }

  function wmStatusLabel(state) {
    if (state === "green") return "Healthy";
    if (state === "yellow") return "Attention";
    if (state === "red") return "Problem";
    return "Unknown";
  }

  function wmFormatMonthShort(monthStr) {
    const parts = String(monthStr || "").split("-");
    if (parts.length < 2) return monthStr || "—";
    return `${parts[1]}/${parts[0].slice(2)}`;
  }

  function wmFormatCostUsd(val, decimals) {
    const n = Number(val || 0);
    const d = decimals != null ? decimals : (n > 0 && n < 0.01 ? 4 : 2);
    return `$${n.toFixed(d)}`;
  }

  const wmCostChartData = {};

  function wmCurrentMonthStr() {
    const d = new Date();
    return `${d.getUTCFullYear()}-${String(d.getUTCMonth() + 1).padStart(2, "0")}`;
  }

  function wmBuildChartSeries(history, mtdCost) {
    const past = Array.isArray(history) ? history.slice() : [];
    past.sort((a, b) => a.month.localeCompare(b.month));
    const series = past.map(h => ({
      month: h.month,
      cost: Number(h.estimatedCostUsd || 0),
      isMtd: false,
    }));
    series.push({
      month: wmCurrentMonthStr(),
      cost: Number(mtdCost || 0),
      isMtd: true,
    });
    return series.slice(-13);
  }

  function wmRenderCostChartSvg(series) {
    const n = series.length;
    const width = Math.max(320, n * 44 + 56);
    const height = 220;
    const padL = 44;
    const padR = 12;
    const padT = 28;
    const padB = 36;
    const chartW = width - padL - padR;
    const chartH = height - padT - padB;
    const maxCost = Math.max(0.01, ...series.map(s => s.cost));
    const gap = 6;
    const barW = Math.max(14, (chartW - gap * (n - 1)) / n);
    const yTicks = 4;
    let grid = "";
    for (let t = 0; t <= yTicks; t++) {
      const val = (maxCost / yTicks) * t;
      const y = padT + chartH - (val / maxCost) * chartH;
      grid += `<line x1="${padL}" y1="${y}" x2="${width - padR}" y2="${y}" stroke="var(--border)" stroke-width="1"/>`;
      grid += `<text class="axis-label" x="${padL - 6}" y="${y + 3}" text-anchor="end">$${val.toFixed(val >= 1 ? 0 : 2)}</text>`;
    }
    let bars = "";
    series.forEach((s, i) => {
      const h = Math.max(2, (s.cost / maxCost) * chartH);
      const x = padL + i * (barW + gap);
      const y = padT + chartH - h;
      const cls = s.isMtd ? "bar-mtd" : "bar-past";
      const label = s.isMtd ? "MTD" : wmFormatMonthShort(s.month);
      bars += `<rect class="${cls}" x="${x}" y="${y}" width="${barW}" height="${h}" rx="3"/>`;
      bars += `<text class="bar-value" x="${x + barW / 2}" y="${y - 4}" text-anchor="middle">${wmFormatCostUsd(s.cost, s.cost > 0 && s.cost < 0.01 ? 4 : 2)}</text>`;
      bars += `<text class="bar-label" x="${x + barW / 2}" y="${height - 10}" text-anchor="middle">${label}</text>`;
    });
    return `<svg class="wm-cost-chart" viewBox="0 0 ${width} ${height}" preserveAspectRatio="xMidYMid meet">${grid}${bars}</svg>`;
  }

function wmOpenCostChart(chartId) {
    const data = wmCostChartData[chartId];
    if (!data) return;
    const series = wmBuildChartSeries(data.history, data.mtdCost);
    const overlay = document.getElementById("wmCostModalOverlay");
    const titleEl = document.getElementById("wmCostModalTitle");
    const chartEl = document.getElementById("wmCostModalChart");
    const noteEl = document.getElementById("wmCostModalNote");
    if (!overlay || !titleEl || !chartEl || !noteEl) return;
    titleEl.textContent = `${data.title} — estimated cost`;
    chartEl.innerHTML = wmRenderCostChartSvg(series);
    const pastCount = series.filter(s => !s.isMtd).length;
    noteEl.textContent = pastCount
      ? `Showing ${pastCount} finalized month${pastCount === 1 ? "" : "s"} plus current MTD from worker KV snapshots.`
      : "History builds as months complete — only current month MTD is available so far.";
    overlay.hidden = false;
    document.body.style.overflow = "hidden";
  }

  function wmCloseCostChart() {
    const overlay = document.getElementById("wmCostModalOverlay");
    if (overlay) overlay.hidden = true;
    document.body.style.overflow = "";
  }

  document.addEventListener("keydown", e => {
    if (e.key === "Escape") wmCloseCostChart();
  });

  function wmRegisterCostChart(chartId, title, mtdCost, history) {
    wmCostChartData[chartId] = { title, mtdCost, history: Array.isArray(history) ? history : [] };
  }

  function wmRenderCostClickable(chartId, mtdCost) {
    const costStr = wmFormatCostUsd(mtdCost);
    return `
      <div class="wm-cost-block">
        <div class="wm-stat-row wm-cost-row wm-cost-click" role="button" tabindex="0"
          onclick="event.stopPropagation();wmOpenCostChart('${chartId}')"
          onkeydown="if(event.key==='Enter'||event.key===' '){event.preventDefault();event.stopPropagation();wmOpenCostChart('${chartId}');}"
          title="Click for yearly cost chart">
          <span>Est. cost</span>
          <strong>${costStr}<span class="wm-cost-hint">MTD ↗</span></strong>
        </div>
      </div>`;
  }

  function wmMergeCostHistory(results) {
    const byMonth = {};
    for (const r of results) {
      const hist = r.stats?.data?.cost_history || [];
      for (const h of hist) {
        byMonth[h.month] = (byMonth[h.month] || 0) + Number(h.estimatedCostUsd || 0);
      }
    }
    return Object.entries(byMonth)
      .sort((a, b) => b[0].localeCompare(a[0]))
      .slice(0, 12)
      .map(([month, estimatedCostUsd]) => ({
        month,
        estimatedCostUsd: Math.round(estimatedCostUsd * 100) / 100,
      }));
  }

  function wmRenderDetailPanel(result) {
    const { app, health, stats, metrics } = result;
    const cardState = wmCardState(health, metrics);
    const fetchedAt = new Date().toLocaleTimeString();
    const url = wmGetUrl(app);
    const keySet = Boolean(wmGetKey(app, false));

    let statsBlock = "";
    if (!keySet) {
      statsBlock = `<div class="cron-card unknown"><div><div class="cron-name">${app.authHeader} not set</div><div class="cron-last">Click "Set ${app.short} key" below or run a smoke test — you'll be prompted once.</div></div></div>`;
    } else if (stats.error === "auth") {
      statsBlock = `<div class="cron-card red"><div><div class="cron-name">Auth failed (401)</div><div class="cron-last">Key in this browser doesn't match ${app.secretName} on the worker.</div></div></div>`;
    } else if (stats.error) {
      statsBlock = `<div class="cron-card red"><div><div class="cron-name">Stats unavailable (${stats.error}${stats.status ? ` HTTP ${stats.status}` : ""})</div><div class="cron-last">Check worker deploy and ${app.statsKind === "ocr" ? "/ocr/quota/stats" : "/ops/stats"} route.</div></div></div>`;
    } else if (metrics) {
      const barColor = wmBarColor(Math.max(metrics.geminiPct, metrics.quotaPct), metrics.circuitBreaker);
      statsBlock = `
        <div style="display:grid;gap:14px;">
          <div>
            <strong>${metrics.quotaLabel}</strong>
            ${metrics.circuitBreaker ? `<span style="color:var(--danger);font-weight:700;margin-left:8px;">⚠ circuit breaker armed</span>` : ""}
            <div class="wm-meter"><div class="wm-meter-fill" style="width:${Math.min(100, metrics.quotaPct).toFixed(1)}%;background:${barColor};"></div></div>
            <div style="font-size:12px;color:var(--text-dim);">${metrics.quotaUsed.toLocaleString()} / ${metrics.quotaCap.toLocaleString()} (${metrics.quotaPct.toFixed(0)}%) — watch 75% · stop 100%</div>
            <div class="wm-threshold-legend">Gemini free tier: alert at 80% (${Math.round(metrics.geminiCap * 0.8).toLocaleString()} / ${metrics.geminiCap.toLocaleString()}/day)</div>
          </div>
          <div style="display:grid;grid-template-columns:repeat(auto-fit,minmax(160px,1fr));gap:12px;">
            <div><div style="font-size:11px;color:var(--text-muted);">Gemini today</div><div style="font-size:20px;font-weight:700;">${metrics.geminiToday.toLocaleString()} <span style="font-size:12px;font-weight:400;color:var(--text-dim);">/ ${metrics.geminiCap.toLocaleString()} free/day</span></div><div class="metric-hint">Google AI Studio free tier; email alert at 80%.</div></div>
            ${metrics.anthropicToday != null ? `<div><div style="font-size:11px;color:var(--text-muted);">Anthropic today</div><div style="font-size:20px;font-weight:700;">${metrics.anthropicToday.toLocaleString()} <span style="font-size:12px;font-weight:400;color:var(--text-dim);">/ ${metrics.anthropicCap.toLocaleString()} free</span></div><div class="metric-hint">Identify/ask calls — billed from pre-paid credits.</div></div>` : ""}
            ${metrics.spaceToday != null ? `<div><div style="font-size:11px;color:var(--text-muted);">OCR.Space today</div><div style="font-size:20px;font-weight:700;">${metrics.spaceToday.toLocaleString()}</div><div class="metric-hint">Cloud OCR fallback when on-device OCR is thin.</div></div>` : ""}
            <div><div style="font-size:11px;color:var(--text-muted);">Est. cost today</div><div style="font-size:20px;font-weight:700;color:${metrics.costToday > 0 ? "var(--danger)" : "var(--text)"};">$${metrics.costToday.toFixed(4)}</div><div class="metric-hint">Non-zero only after free-tier daily caps exceeded.</div></div>
            <div><div style="font-size:11px;color:var(--text-muted);">Est. cost MTD</div><div style="font-size:20px;font-weight:700;color:${metrics.costMtd > 0 ? "var(--danger)" : "var(--text)"};">$${metrics.costMtd.toFixed(2)}</div><div class="metric-hint">Month-to-date overage estimate from KV counters.</div></div>
          </div>
          ${metrics.geminiToday === 0 && app.statsKind === "ops" ? `<div style="font-size:12px;color:var(--text-dim);">KV tracking active — counters increment on the first Gemini or Anthropic call through this worker.</div>` : ""}
        </div>`;
    }

    const wmUpgrade = (metrics && (metrics.quotaPct >= 75 || metrics.geminiPct >= 75 || metrics.circuitBreaker))
      ? panelUpgradeBox(
          app.statsKind === "ocr" ? ["gemini", "ocr_space", "wrangler"] : ["gemini", "anthropic", "wrangler"],
          metrics.circuitBreaker ? "Circuit breaker armed on this worker." : "",
        )
      : "";

    return `
      <div class="wm-detail">
        <div class="wm-detail-head">
          <div>
            <div class="wm-app-name">${app.short}</div>
            <div style="font-size:18px;font-weight:700;color:var(--primary);">${app.name}</div>
          </div>
          <span class="wm-status-pill ${cardState}"><span class="wm-status-dot"></span>${wmStatusLabel(cardState)}</span>
        </div>
        <div style="display:grid;grid-template-columns:repeat(auto-fit,minmax(180px,1fr));gap:10px;font-size:13px;margin-bottom:14px;">
          <div><span style="color:var(--text-muted);">Worker</span><br><strong>${health.ok ? "OK" : "Down / error"}</strong><div class="metric-hint">GET / returns JSON — false = DNS, deploy, or Worker error.</div></div>
          <div><span style="color:var(--text-muted);">Gemini key</span><br><strong>${health.gemini_configured === false ? "Not configured" : health.gemini_configured === true ? "Configured" : "—"}</strong><div class="metric-hint">Worker secret GEMINI_API_KEY — required for receipt/PDF vision.</div></div>
          <div><span style="color:var(--text-muted);">Service</span><br><strong style="font-family:var(--mono);font-size:12px;">${health.service || "—"}</strong><div class="metric-hint">Worker self-identifies in health JSON.</div></div>
          <div><span style="color:var(--text-muted);">Health URL</span><br><a href="${url}/" target="_blank" rel="noopener">${url}/ ↗</a><div class="metric-hint">Public ping — no API key needed.</div></div>
        </div>
        ${statsBlock}
        ${wmUpgrade}
        <div class="wm-url-row">
          <label style="color:var(--text-muted);">Worker URL override:</label>
          <input id="wm-url-${app.id}" type="url" value="${url}" placeholder="${app.defaultUrl}">
          <button class="m-btn" type="button" onclick="wmSaveUrl('${app.id}')">Save URL</button>
          <button class="m-btn" type="button" onclick="wmGetKey(WORKER_APPS.find(a=>a.id==='${app.id}'),true);wmRenderFromCache();">Set ${app.short} key</button>
          <button class="m-btn" type="button" onclick="wmClearKey('${app.id}')">Clear key</button>
        </div>
        <div class="wm-updated">Last updated ${fetchedAt}</div>
      </div>`;
  }

  
  function wmSetStatus(msg) {
    const el = document.getElementById("wmStatus");
    if (el) el.textContent = msg;
  }

  function wmShowIdle() {
    wmSetStatus("Click Refresh to load worker data. Light = health only · Medium ≈18 KV reads · Heavy ≈60 KV reads (cost chart).");
    const summaryEl = document.getElementById("workerMonitoringSummary");
    const gridEl = document.getElementById("workerMonitoringGrid");
    const combinedEl = document.getElementById("workerMonitoringCombined");
    const tabsEl = document.getElementById("workerMonitoringTabs");
    if (summaryEl) summaryEl.textContent = "Click Refresh (Light / Medium / Heavy) above.";
    if (gridEl) gridEl.innerHTML = "";
    if (combinedEl) combinedEl.innerHTML = "";
    if (tabsEl) tabsEl.innerHTML = "";
  }

  function wmEstimateKvReads(tier) {
    if (tier === "light") return 0;
    if (tier === "medium") return 18;
    if (tier === "heavy") return 60;
    return null;
  }

  function wmRenderMonitoring(results) {
    const combinedEl = document.getElementById("workerMonitoringCombined");
    const summaryEl = document.getElementById("workerMonitoringSummary");
    const tabsEl = document.getElementById("workerMonitoringTabs");
    const gridEl = document.getElementById("workerMonitoringGrid");
    if (!gridEl) return;

    const fetchedAt = wmCache?.fetchedAt ? new Date(wmCache.fetchedAt).toLocaleTimeString() : new Date().toLocaleTimeString();
    const tier = wmCache?.tier || "light";
    const costReady = wmCache?.costHistoryLoaded;
    const combinedToday = results.reduce((s, r) => s + (r.metrics?.costToday || 0), 0);
    const combinedMtd = results.reduce((s, r) => s + (r.metrics?.costMtd || 0), 0);
    const combinedHistory = wmMergeCostHistory(results);

    if (combinedEl) {
      if (tier === "light") {
        combinedEl.innerHTML = `<div class="wm-combined"><span style="color:var(--text-muted);">Health-only refresh — load Medium for combined cost totals.</span></div>`;
      } else {
        wmRegisterCostChart("wm-combined", "Combined PBJ + HHH + CVC", combinedMtd, combinedHistory);
        combinedEl.innerHTML = `
          <div class="wm-combined">
            <span><strong>Combined AI/OCR cost today:</strong> $${combinedToday.toFixed(4)}</span>
            <span class="metric-hint" style="display:inline;margin:0 8px 0 0;">Sum of estimated overage across PBJ + HHH + CVC workers.</span>
            <div class="wm-combined-cost">${costReady ? wmRenderCostClickable("wm-combined", combinedMtd) : `<span class="metric-hint">Cost chart needs Heavy refresh.</span>`}</div>
            <span class="metric-hint" style="display:inline;margin:0 8px 0 0;">${costReady ? "Click Est. cost for yearly chart." : "MTD shown; yearly bars need Heavy."} Calendar month MTD; $0 while under free tiers.</span>
            <span style="color:var(--text-muted);">All three workers · ${tier} · ${fetchedAt}</span>
          </div>`;
      }
    }

    if (summaryEl) {
      summaryEl.innerHTML = results.map(r => {
        const state = wmCardState(r.health, r.metrics);
        let costBlock;
        if (r.metrics && tier !== "light") {
          const chartId = `wm-${r.app.id}`;
          wmRegisterCostChart(chartId, `${r.app.short} · ${r.app.name}`, r.metrics.costMtd, r.metrics.costHistory);
          costBlock = costReady && r.metrics.costHistory?.length
            ? wmRenderCostClickable(chartId, r.metrics.costMtd)
            : `<div class="wm-stat-row wm-cost-row"><span>Est. cost MTD</span><strong>$${r.metrics.costMtd.toFixed(2)}</strong></div>`;
        } else if (r.metrics) {
          costBlock = `<div class="wm-stat-row wm-cost-row"><span>Est. cost</span><strong>—</strong></div>`;
        } else {
          costBlock = `<div class="wm-stat-row wm-cost-row"><span>Est. cost</span><strong>${r.stats?.error === "no_key" ? "key needed" : r.stats?.error === "skipped" ? "Medium+" : "—"}</strong></div>`;
        }
        const gemini = r.metrics
          ? `${r.metrics.geminiToday.toLocaleString()} / ${r.metrics.geminiCap.toLocaleString()} Gemini`
          : (tier === "light" ? "— (Medium)" : "—");
        const quota = r.metrics
          ? `${r.metrics.quotaUsed.toLocaleString()} / ${r.metrics.quotaCap.toLocaleString()} ${r.metrics.quotaLabel}`
          : (tier === "light" ? "— (Medium)" : "—");
        return `
          <div class="wm-summary-card ${state}" role="button" tabindex="0" onclick="wmSelectTab('${r.app.id}')" onkeydown="if(event.key==='Enter')wmSelectTab('${r.app.id}')">
            <div class="wm-app-name">${r.app.short}</div>
            <div class="wm-app-title">${r.app.name}</div>
            <div class="wm-stat-row"><span>Status</span><strong>${wmStatusLabel(state)}</strong></div>
            <div class="wm-stat-row"><span>Gemini today</span><strong>${gemini}</strong></div>
            <div class="wm-stat-row"><span>Daily total</span><strong>${quota}</strong></div>
            <div class="metric-hint" style="margin-top:6px;">Status = worker + keys + quota %. Daily total = circuit-breaker counter.</div>
            ${costBlock}
            <div class="wm-stat-row"><span>Updated</span><strong>${fetchedAt}</strong></div>
          </div>`;
      }).join("");
    }

    if (tabsEl) {
      tabsEl.innerHTML = WORKER_APPS.map(app =>
        `<button type="button" class="wm-tab ${app.id === wmActiveTab ? "active" : ""}" onclick="wmSelectTab('${app.id}')">${app.short} · ${app.name}</button>`,
      ).join("");
    }

    const active = results.find(r => r.app.id === wmActiveTab) || results[0];
    gridEl.innerHTML = wmRenderDetailPanel(active);
    updateThresholdsLiveUsage(results);
  }

  function wmRenderFromCache() {
    if (!wmCache?.results) {
      wmShowIdle();
      return;
    }
    wmRenderMonitoring(wmCache.results);
  }

  async function wmFetchTier(tier) {
    const costHistory = tier === "heavy";
    const fetchStats = tier !== "light";
    wmSetStatus(`${tier === "light" ? "Light" : tier === "medium" ? "Medium" : "Heavy"} refresh…`);
    for (const app of WORKER_APPS) wmHealStoredWorkerKey(app);

    const results = await Promise.all(WORKER_APPS.map(async app => {
      const health = await wmFetchHealth(app);
      let stats = { error: "skipped" };
      if (fetchStats) {
        stats = await wmFetchStats(app, { costHistory });
      }
      const metrics = stats.data ? wmNormalizeMetrics(app, stats.data) : null;
      return { app, health, stats, metrics };
    }));

    wmCache = {
      results,
      tier,
      costHistoryLoaded: costHistory,
      fetchedAt: Date.now(),
    };

    const pbjResult = results.find(r => r.app.id === "pbj");
    if (pbjResult?.stats?.data) {
      ocrQuotaCache = {
        data: pbjResult.stats.data,
        costHistoryLoaded: costHistory,
        fetchedAt: Date.now(),
      };
      ocrRenderFromCache();
    }

    wmRenderMonitoring(results);
    const kv = wmEstimateKvReads(tier);
    wmSetStatus(
      `${tier.charAt(0).toUpperCase() + tier.slice(1)} loaded · ${new Date().toLocaleTimeString()}` +
      (kv != null ? ` · ~${kv} KV reads (3 workers)` : " · 0 KV reads (health only)"),
    );
    updateOpsAlertBanner().catch(() => {});
    return results;
  }

  async function wmRefreshLight() { return wmFetchTier("light"); }
  async function wmRefreshMedium() { return wmFetchTier("medium"); }
  async function wmRefreshHeavy() { return wmFetchTier("heavy"); }

  function wmSetAutoRefresh() {
    const autoEl = document.getElementById("wmAutoRefresh");
    const selEl = document.getElementById("wmAutoInterval");
    const on = autoEl && autoEl.checked;
    if (selEl) selEl.disabled = !on;
    if (wmAutoTick) {
      clearInterval(wmAutoTick);
      wmAutoTick = null;
    }
    if (!on) return;
    const sec = parseInt(selEl?.value || "1800", 10);
    wmAutoTick = setInterval(() => wmRefreshMedium(), sec * 1000);
  }

  function wmSelectTab(id) {
    wmActiveTab = id;
    localStorage.setItem("wm_active_tab", id);
    wmRenderFromCache();
  }

  async function loadWorkerMonitoring() {
    wmRenderFromCache();
  }

  /* ─── Partner Referrals (HHH) — manual refresh only ─────────── */
  let refActiveTab = localStorage.getItem("ref_active_tab") || "all";
  let refLastData = null;
  let refLastDetail = null;

  function refHhhApp() {
    return WORKER_APPS.find(a => a.id === "hhh");
  }

  function refOnRangePresetChange() {
    const preset = document.getElementById("refRangePreset")?.value || "7";
    const showCustom = preset === "custom";
    document.getElementById("refCustomFromWrap").style.display = showCustom ? "" : "none";
    document.getElementById("refCustomToWrap").style.display = showCustom ? "" : "none";
  }

  function refSelectTab(tab) {
    refActiveTab = tab;
    localStorage.setItem("ref_active_tab", tab);
    document.getElementById("refTabAll")?.classList.toggle("active", tab === "all");
    document.getElementById("refTabJj")?.classList.toggle("active", tab === "jj");
    document.getElementById("refJjNote").hidden = tab !== "jj";
    document.getElementById("refIncludeResourcesWrap").style.display = tab === "jj" ? "" : "none";
    refRender();
  }

  function refRangeParams() {
    const preset = document.getElementById("refRangePreset")?.value || "7";
    if (preset === "custom") {
      const from = document.getElementById("refCustomFrom")?.value;
      const to = document.getElementById("refCustomTo")?.value;
      if (!from || !to) return { error: "Pick both From and To dates for custom range." };
      return { from, to };
    }
    return { days: preset };
  }

  function refRangeQueryString(extra) {
    const p = refRangeParams();
    if (p.error) return p;
    const q = new URLSearchParams(extra || {});
    if (p.from) {
      q.set("from", p.from);
      q.set("to", p.to);
    } else {
      q.set("days", p.days || "7");
    }
    return { qs: q.toString() };
  }

  async function refFetchReferrals(detail) {
    const app = refHhhApp();
    if (!app) return { error: "HHH worker config missing." };
    const key = wmGetKey(app, true);
    if (!key) return { error: "HHH Worker key required." };
    const rq = refRangeQueryString({ detail: detail === "full" ? "full" : "summary" });
    if (rq.error) return rq;
    const url = `${wmGetUrl(app)}/ops/referrals?${rq.qs}`;
    try {
      const r = await fetch(url, {
        headers: { [app.authHeader]: key },
        cache: "no-store",
        signal: AbortSignal.timeout(15000),
      });
      if (r.status === 401) return { error: "HHH key rejected (401)." };
      if (!r.ok) return { error: `HTTP ${r.status} — deploy HHH worker with /ops/referrals.` };
      return { data: await r.json() };
    } catch (e) {
      return { error: e.message || "Network error" };
    }
  }

  function refFilteredTotals(data) {
    const t = data.totals || {};
    const includeResources = document.getElementById("refIncludeResources")?.checked;
    if (refActiveTab === "all") {
      return {
        total: t.total || 0,
        commerce: t.commerce || 0,
        repair: t.repair || 0,
        resources: t.resources || 0,
        ebay: t.ebay || 0,
        clockworks: t.clockworks || 0,
      };
    }
    const commerce = t.commerce || 0;
    const repair = t.repair || 0;
    const resources = includeResources ? (t.resources || 0) : 0;
    return {
      total: commerce + repair + resources,
      commerce,
      repair,
      resources,
      ebay: 0,
      clockworks: commerce + repair + resources,
    };
  }

  function refFilterByDayRows(byDay) {
    const includeResources = document.getElementById("refIncludeResources")?.checked;
    return (byDay || []).map(row => {
      if (refActiveTab === "all") return row;
      const commerce = row.commerce || 0;
      const repair = row.repair || 0;
      const resources = includeResources ? (row.resources || 0) : 0;
      return {
        date: row.date,
        total: commerce + repair + resources,
        commerce,
        repair,
        resources,
        ebay: 0,
        clockworks: commerce + repair + resources,
      };
    });
  }

  function refRenderTable(title, headers, rows) {
    if (!rows.length) return `<div class="ref-table-wrap"><h3 style="padding:12px 14px 0;font-size:13px;color:var(--primary);">${title}</h3><p style="padding:12px 14px;color:var(--text-muted);font-size:12px;">No data in range.</p></div>`;
    return `
      <div class="ref-table-wrap">
        <h3 style="padding:12px 14px 0;font-size:13px;color:var(--primary);">${title}</h3>
        <table>
          <thead><tr>${headers.map(h => `<th>${h}</th>`).join("")}</tr></thead>
          <tbody>${rows.map(cells => `<tr>${cells.map((c, i) => `<td${i > 0 ? ' class="num"' : ""}>${c}</td>`).join("")}</tr>`).join("")}</tbody>
        </table>
      </div>`;
  }

  function refRender() {
    const el = document.getElementById("refContent");
    if (!el) return;
    const data = refLastData;
    if (!data) {
      el.innerHTML = "";
      return;
    }
    const ft = refFilteredTotals(data);
    const byDay = refFilterByDayRows(data.byDay);
    const tabLabel = refActiveTab === "jj" ? "JJ shareable" : "All stats";

    let html = `
      <div class="ref-summary-grid">
        <div class="ref-stat-card"><div class="val">${ft.total.toLocaleString()}</div><div class="lbl">Total clicks</div></div>
        <div class="ref-stat-card"><div class="val">${ft.commerce.toLocaleString()}</div><div class="lbl">Commerce</div></div>
        <div class="ref-stat-card"><div class="val">${ft.repair.toLocaleString()}</div><div class="lbl">Repair</div></div>
        <div class="ref-stat-card"><div class="val">${ft.resources.toLocaleString()}</div><div class="lbl">Resources</div></div>`;
    if (refActiveTab === "all") {
      html += `<div class="ref-stat-card"><div class="val">${ft.ebay.toLocaleString()}</div><div class="lbl">eBay</div></div>`;
    }
    html += `</div>`;

    html += refRenderTable(
      `${tabLabel} · daily breakdown (${data.range?.from || "?"} → ${data.range?.to || "?"})`,
      ["Date", "Total", "Commerce", "Repair", "Resources"].concat(refActiveTab === "all" ? ["eBay"] : []),
      byDay.map(r => [
        r.date,
        r.total.toLocaleString(),
        r.commerce.toLocaleString(),
        r.repair.toLocaleString(),
        r.resources.toLocaleString(),
      ].concat(refActiveTab === "all" ? [r.ebay.toLocaleString()] : [])),
    );

    if (refLastDetail && refActiveTab === "all") {
      const ctxRows = Object.entries(refLastDetail.byContext || {})
        .sort((a, b) => b[1] - a[1])
        .map(([ctx, n]) => [ctx, n.toLocaleString()]);
      html += refRenderTable("By context (range total)", ["Context", "Clicks"], ctxRows);

      const destRows = Object.entries(refLastDetail.byDestinationType || {})
        .sort((a, b) => b[1] - a[1])
        .map(([d, n]) => [d, n.toLocaleString()]);
      html += refRenderTable("By destination type", ["Type", "Clicks"], destRows);

      const partnerRows = Object.entries(refLastDetail.byPartner || {})
        .sort((a, b) => b[1] - a[1])
        .map(([p, n]) => [p, n.toLocaleString()]);
      html += refRenderTable("By partner", ["Partner", "Clicks"], partnerRows);

      const dayCtx = refLastDetail.byDayByContext || {};
      const matrixRows = [];
      for (const [day, ctxMap] of Object.entries(dayCtx).sort((a, b) => a[0].localeCompare(b[0]))) {
        for (const [ctx, n] of Object.entries(ctxMap).sort((a, b) => b[1] - a[1])) {
          matrixRows.push([day, ctx, n.toLocaleString()]);
        }
      }
      html += refRenderTable("Daily × context (detail)", ["Date", "Context", "Clicks"], matrixRows);
    } else if (refLastDetail && refActiveTab === "jj") {
      const cwCtx = refLastDetail.byContextByPartner?.clockworks || {};
      const ctxRows = Object.entries(cwCtx)
        .sort((a, b) => b[1] - a[1])
        .slice(0, 30)
        .map(([ctx, n]) => [ctx, n.toLocaleString()]);
      html += refRenderTable("By context (Clockworks only — JJ view)", ["Context", "Clicks"], ctxRows);
    } else if (refLastData?.byContext && Object.keys(refLastData.byContext).length) {
      const ctxRows = Object.entries(refLastData.byContext)
        .sort((a, b) => b[1] - a[1])
        .slice(0, 20)
        .map(([ctx, n]) => [ctx, n.toLocaleString()]);
      html += refRenderTable("By context (range total)", ["Context", "Clicks"], ctxRows);
    }

    el.innerHTML = html;
  }

  async function refRefreshLight() {
    const status = document.getElementById("refStatus");
    const rq = refRangeQueryString();
    if (rq.error) {
      status.textContent = rq.error;
      status.className = "ref-status err";
      return;
    }
    status.textContent = "Loading KV rollups (Light)…";
    status.className = "ref-status";
    refLastDetail = null;
    const res = await refFetchReferrals("summary");
    if (res.error) {
      status.textContent = res.error;
      status.className = "ref-status err";
      return;
    }
    refLastData = res.data;
    refRender();
    status.textContent = `KV rollups loaded · ${res.data.range?.from} → ${res.data.range?.to} · ${new Date().toLocaleTimeString()} · Light (~${(res.data.range?.days || 7) * 8} KV reads)`;
  }

  async function refLoadDetail() {
    const status = document.getElementById("refStatus");
    status.textContent = "Loading detail tables (Medium)…";
    status.className = "ref-status";
    const res = await refFetchReferrals("full");
    if (res.error) {
      status.textContent = res.error;
      status.className = "ref-status err";
      return;
    }
    refLastData = res.data;
    refLastDetail = res.data;
    refRender();
    status.textContent = `Detail tables loaded · ${res.data.range?.from} → ${res.data.range?.to} · ${new Date().toLocaleTimeString()} · Medium (context lists per day)`;
  }

  async function refLoadTopSkus() {
    if (!confirm("Top SKUs uses PocketBase quota — use sparingly. Continue?")) return;
    const status = document.getElementById("refStatus");
    const rp = refRangeParams();
    if (rp.error) {
      status.textContent = rp.error;
      status.className = "ref-status err";
      return;
    }
    status.textContent = "Querying PocketBase for top SKUs (Heavy)…";
    status.className = "ref-status";
    const fromIso = rp.from ? `${rp.from} 00:00:00.000Z` : "";
    const toIso = rp.to ? `${rp.to} 23:59:59.999Z` : "";
    let filter = 'partner = "clockworks" && product_sku != ""';
    if (fromIso && toIso) {
      filter += ` && ts >= "${fromIso}" && ts <= "${toIso}"`;
    } else {
      const days = parseInt(rp.days || "7", 10);
      const start = new Date();
      start.setUTCDate(start.getUTCDate() - days + 1);
      filter += ` && ts >= "${start.toISOString()}"`;
    }
    try {
      const res = await pbAuth(
        `/api/collections/hhh_outbound_clicks/records?perPage=500&sort=-ts&filter=${encodeURIComponent(filter)}&fields=product_sku,context,destination_type`,
      );
      if (!res.ok) throw new Error(`PocketBase HTTP ${res.status}`);
      const data = await res.json();
      const counts = {};
      for (const row of data.items || []) {
        const sku = row.product_sku || "unknown";
        counts[sku] = (counts[sku] || 0) + 1;
      }
      const top = Object.entries(counts).sort((a, b) => b[1] - a[1]).slice(0, 20);
      const el = document.getElementById("refContent");
      const table = refRenderTable(
        "Top Clockworks SKUs (Heavy · PocketBase, max 500 rows sampled)",
        ["SKU", "Clicks in sample"],
        top.map(([sku, n]) => [sku, n.toLocaleString()]),
      );
      el.insertAdjacentHTML("beforeend", table);
      status.textContent = `Top SKUs loaded from PocketBase · ${top.length} SKUs · ${new Date().toLocaleTimeString()} · Heavy`;
    } catch (e) {
      status.textContent = e.message || "PocketBase query failed";
      status.className = "ref-status err";
    }
  }

  async function refExportClickLog() {
    if (!confirm("Export uses PocketBase quota — use sparingly (up to 2,000 rows). Continue?")) return;
    const status = document.getElementById("refStatus");
    const rp = refRangeParams();
    if (rp.error) {
      status.textContent = rp.error;
      status.className = "ref-status err";
      return;
    }
    status.textContent = "Exporting click log from PocketBase (Heavy)…";
    let filter = 'id != ""';
    if (rp.from && rp.to) {
      filter = `ts >= "${rp.from} 00:00:00.000Z" && ts <= "${rp.to} 23:59:59.999Z"`;
    } else {
      const days = parseInt(rp.days || "7", 10);
      const start = new Date();
      start.setUTCDate(start.getUTCDate() - days + 1);
      filter = `ts >= "${start.toISOString()}"`;
    }
    if (refActiveTab === "jj") {
      filter += ' && partner = "clockworks"';
    }
    try {
      const records = await listAllRecords("hhh_outbound_clicks", filter);
      const capped = records.slice(0, 2000);
      const csv = recordsToCSV(capped);
      downloadFile(`hhh_outbound_clicks_${rp.from || rp.days + "d"}.csv`, csv, "text/csv");
      status.textContent = `Exported ${capped.length} rows · Heavy · PocketBase`;
    } catch (e) {
      status.textContent = e.message || "Export failed";
      status.className = "ref-status err";
    }
  }

  document.getElementById("refIncludeResources")?.addEventListener("change", () => refRender());
  refOnRangePresetChange();
  refSelectTab(refActiveTab);

  /* ─── Thresholds & Baselines — Joe ops reference tables ─── */
  const TB_TABS = [
    { id: "pbj", label: "PBJ", title: "Pocket Budget Journal" },
    { id: "hhh", label: "HHH", title: "Handy Horology Helper" },
    { id: "cvc", label: "CVC", title: "Curator's Vault" },
    { id: "shared", label: "Shared", title: "All apps / infra" },
  ];
  const TB_SCENARIOS = [
    { subs: 10, mrr: 84.9, note: "Covers realistic fixed costs (~5 subs). Daily API use stays tiny — hundreds of calls/day headroom." },
    { subs: 50, mrr: 424.5, note: "Comfortable margin. If 10 active users scan 5 receipts/day ≈ 50 calls — still under Gemini free tier." },
    { subs: 100, mrr: 849, note: "Strong buffer. Good time to split Gemini into per-app Google AI Studio projects for billing clarity." },
    { subs: 500, mrr: 4245, note: "Scale territory — budget for paid Gemini, OCR.Space PRO, Teller prod (~$2/bank/mo), and RevenueCat 1% if MTR > $10K." },
  ];
  let tbActiveTab = localStorage.getItem("tb_active_tab") || "pbj";
  let tbLiveUsage = {};

  function tbSelectTab(id) {
    tbActiveTab = id;
    localStorage.setItem("tb_active_tab", id);
    renderThresholdsBaselines();
  }

  function tbLiveCell(serviceKey, used, cap, pct) {
    if (used == null) return '<span class="tb-live">—</span>';
    const cls = pct >= 100 ? "crit" : pct >= 75 ? "warn" : "";
    return `<span class="tb-live ${cls}">${Number(used).toLocaleString()} / ${Number(cap).toLocaleString()}</span>`;
  }

  function renderThresholdsBaselines() {
    const tabsEl = document.getElementById("thresholdsTabs");
    const panelEl = document.getElementById("thresholdsPanel");
    const scenEl = document.getElementById("thresholdsScenarios");
    if (!panelEl) return;

    if (tabsEl) {
      tabsEl.innerHTML = TB_TABS.map(t =>
        `<button type="button" class="tb-tab ${t.id === tbActiveTab ? "active" : ""}" onclick="tbSelectTab('${t.id}')">${t.label} · ${t.title}</button>`,
      ).join("");
    }

    if (scenEl) {
      scenEl.innerHTML = TB_SCENARIOS.map(s => `
        <div class="tb-scenario-card">
          <div class="tb-sc-label">${s.subs} paying subs @ $9.99</div>
          <div class="tb-sc-value">~$${s.mrr.toLocaleString("en-US", { maximumFractionDigits: 0 })}/mo net</div>
          <div class="tb-sc-sub">${s.note}</div>
        </div>`).join("");
    }

    const live = tbLiveUsage[tbActiveTab] || {};
    let tableHtml = "";
    let note = "";

    if (tbActiveTab === "pbj") {
      tableHtml = `
        <table>
          <thead><tr>
            <th>Service / limit</th><th>Free tier</th><th>Yellow warning</th><th>Hard stop</th><th>Cost if exceeded</th><th>Live today</th>
          </tr></thead>
          <tbody>
            <tr>
              <td><strong>Gemini</strong> (receipt/bank vision)</td>
              <td class="num">1,500 calls/day</td>
              <td>80% → red banner + email (${live.geminiWarn || "1,200"})</td>
              <td>Vendor billing overage (no app block by itself)</td>
              <td class="num">~$0.001/call</td>
              <td>${tbLiveCell("gemini", live.geminiUsed, live.geminiCap, live.geminiPct)}</td>
            </tr>
            <tr>
              <td><strong>OCR.Space</strong> (receipt OCR layer)</td>
              <td class="num">500 calls/day</td>
              <td>Tracked for cost estimate only</td>
              <td>Rate limit from vendor</td>
              <td class="num">~$0.0002/call or $30/mo PRO</td>
              <td>${tbLiveCell("space", live.spaceUsed, live.spaceCap, live.spacePct)}</td>
            </tr>
            <tr>
              <td><strong>Global OCR</strong> (circuit breaker)</td>
              <td class="num">1,800 calls/day total</td>
              <td>75% meter yellow (${live.globalWarn || "1,350"})</td>
              <td>100% — <em>free</em> users denied cloud OCR</td>
              <td class="num">—</td>
              <td>${tbLiveCell("global", live.globalUsed, live.globalCap, live.globalPct)}</td>
            </tr>
            <tr>
              <td>Per-user <strong>free</strong> tier</td>
              <td class="num">15 scans/month · 50/day max</td>
              <td>—</td>
              <td>User sees "limit reached"</td>
              <td class="num">—</td>
              <td><span class="tb-live">per device</span></td>
            </tr>
            <tr>
              <td>Per-user <strong>trial</strong></td>
              <td class="num">200 scans/month</td>
              <td>—</td>
              <td>User limit reached</td>
              <td class="num">—</td>
              <td><span class="tb-live">per device</span></td>
            </tr>
            <tr>
              <td>Per-user <strong>premium</strong> (active sub)</td>
              <td class="num">500 scans/month</td>
              <td>—</td>
              <td>User limit reached</td>
              <td class="num">—</td>
              <td><span class="tb-live">per device</span></td>
            </tr>
          </tbody>
        </table>`;
      note = "Adjust caps in PBJ <code>cloudflare-worker/wrangler.toml</code> → <code>wrangler deploy</code>. No app rebuild.";
    } else if (tbActiveTab === "hhh" || tbActiveTab === "cvc") {
      const appLabel = tbActiveTab === "hhh" ? "HHH" : "CVC";
      tableHtml = `
        <table>
          <thead><tr>
            <th>Service / limit</th><th>Free tier</th><th>Yellow warning</th><th>Hard stop</th><th>Cost if exceeded</th><th>Live today</th>
          </tr></thead>
          <tbody>
            <tr>
              <td><strong>Gemini</strong> (photo identify)</td>
              <td class="num">1,500 calls/day</td>
              <td>80% → red banner + email</td>
              <td>Vendor billing overage</td>
              <td class="num">~$0.001/call</td>
              <td>${tbLiveCell("gemini", live.geminiUsed, live.geminiCap, live.geminiPct)}</td>
            </tr>
            <tr>
              <td><strong>Anthropic</strong> (Claude /ask, text identify)</td>
              <td class="num">5,000 calls/day tracked</td>
              <td>Low balance on billing page</td>
              <td>API returns error when credits exhausted</td>
              <td class="num">~$0.004/call (Haiku)</td>
              <td>${tbLiveCell("anthropic", live.anthropicUsed, live.anthropicCap, live.anthropicPct)}</td>
            </tr>
            <tr>
              <td><strong>Global AI</strong> (circuit breaker)</td>
              <td class="num">500 calls/day total</td>
              <td>75% meter yellow</td>
              <td>100% — circuit breaker armed</td>
              <td class="num">—</td>
              <td>${tbLiveCell("global", live.globalUsed, live.globalCap, live.globalPct)}</td>
            </tr>
            <tr>
              <td><strong>eBay Browse</strong> (worker <code>search_by_image</code>)</td>
              <td class="num">5,000/day per Production keyset (eBay)</td>
              <td>Worker cap 3,500/day default (2,500 HHH + 1,500 CVC if one shared key)</td>
              <td>100% worker cap &rarr; 429; identify continues without eBay</td>
              <td class="num">&mdash;</td>
              <td><span class="tb-live">Worker tab <code>ebay.today</code></span></td>
            </tr>
          </tbody>
        </table>`;
      note = `${appLabel} caps in <code>${appLabel === "HHH" ? "HHH" : "CVC"}/cloudflare-worker/wrangler.toml</code>. Separate Gemini API key per app (see CLOUD_KEYS.md).`;
    } else {
      tableHtml = `
        <table>
          <thead><tr>
            <th>Service</th><th>Free / fixed</th><th>Yellow warning</th><th>Hard stop</th><th>Cost if exceeded</th><th>Live today</th>
          </tr></thead>
          <tbody>
            <tr>
              <td><strong>PocketHost / PocketBase</strong></td>
              <td class="num">$5/mo fixed</td>
              <td>—</td>
              <td>Plan limits on storage/CPU</td>
              <td class="num">Upgrade tier</td>
              <td><span class="tb-live">fixed</span></td>
            </tr>
            <tr>
              <td><strong>Cloudflare Workers</strong> (3 workers)</td>
              <td class="num">100,000 req/day free</td>
              <td>—</td>
              <td>429 rate limit</td>
              <td class="num">$5/mo paid tier</td>
              <td><span class="tb-live">—</span></td>
            </tr>
            <tr>
              <td><strong>OpenCellID</strong> (PBJ geolocation)</td>
              <td class="num">1,000 lookups/day</td>
              <td>80% red in panel</td>
              <td>100% — lookups refused</td>
              <td class="num">Paid tier if needed</td>
              <td>${tbLiveCell("opencellid", live.opencellidUsed, live.opencellidCap, live.opencellidPct)}</td>
            </tr>
            <tr>
              <td><strong>Teller</strong> (PBJ bank sync)</td>
              <td class="num">$0 sandbox/dev</td>
              <td>Active enrollments rising</td>
              <td>—</td>
              <td class="num">~$2/active bank/mo in production</td>
              <td>${live.tellerEnrollments != null ? `<span class="tb-live">${live.tellerEnrollments} active</span>` : "<span class=\"tb-live\">sandbox</span>"}</td>
            </tr>
            <tr>
              <td><strong>Store + domains</strong></td>
              <td class="num">~$16 lean / ~$36 realistic/mo</td>
              <td>—</td>
              <td>—</td>
              <td class="num">See Founder Economics</td>
              <td><span class="tb-live">—</span></td>
            </tr>
          </tbody>
        </table>`;
      note = "PocketBase cron heartbeat (PBJ flywheel only) shows in the <strong>gray info banner</strong> when pb_hooks isn't deployed — not the red ops alert. Worker quota emails are separate; see collapsible explainer above.";
    }

    panelEl.innerHTML = tableHtml + `<div class="tb-note">${note}</div>`;
  }

  function updateThresholdsLiveUsage(wmResults) {
    if (!wmResults) return;
    tbLiveUsage = { pbj: {}, hhh: {}, cvc: {}, shared: {} };

    for (const r of wmResults) {
      const m = r.metrics;
      if (!m) continue;
      const bucket = r.app.id;
      tbLiveUsage[bucket] = {
        geminiUsed: m.geminiToday,
        geminiCap: m.geminiCap,
        geminiPct: m.geminiPct,
        geminiWarn: Math.round(m.geminiCap * 0.8),
        globalUsed: m.quotaUsed,
        globalCap: m.quotaCap,
        globalPct: m.quotaPct,
        globalWarn: Math.round(m.quotaCap * 0.75),
        spaceUsed: m.spaceToday,
        spaceCap: 500,
        spacePct: m.spaceToday != null ? (m.spaceToday / 500) * 100 : null,
        anthropicUsed: m.anthropicToday,
        anthropicCap: m.anthropicCap,
        anthropicPct: m.anthropicToday != null && m.anthropicCap
          ? (m.anthropicToday / m.anthropicCap) * 100 : null,
      };
    }

    renderThresholdsBaselines();
  }

  async function loadThresholdsSharedStats() {
    const key = localStorage.getItem("pbj_shared_key") || "";
    if (!key) return;
    tbLiveUsage.shared = tbLiveUsage.shared || {};
    try {
      const [ocR, telR] = await Promise.all([
        fetch(`${WORKER_BASE}/opencellid/stats`, { headers: { "X-PBJ-Key": key }, signal: AbortSignal.timeout(8000) }),
        fetch(`${WORKER_BASE}/teller/stats`, { headers: { "X-PBJ-Key": key }, signal: AbortSignal.timeout(8000) }),
      ]);
      if (ocR.ok) {
        const oc = await ocR.json();
        tbLiveUsage.shared.opencellidUsed = oc.used_today;
        tbLiveUsage.shared.opencellidCap = oc.cap || 1000;
        tbLiveUsage.shared.opencellidPct = Number(oc.pct_used) || 0;
      }
      if (telR.ok) {
        const tel = await telR.json();
        tbLiveUsage.shared.tellerEnrollments = tel.active_enrollments;
      }
      renderThresholdsBaselines();
    } catch { /* optional */ }
  }

  /* ─── Breakeven — synced with PBJ docs/JOE_OPS_COSTS.md ─── */
  const FIXED_COSTS = {
    net_per_monthly_sub: 8.49,
    stacks: { lean: 15.67, realistic: 35.67, comfort: 50.67 },
    breakeven_subs: { lean: 2, realistic: 5, comfort: 6 },
    lines: [
      { item: "josspatech.com (domain)", monthly: 1.0, note: "estimate" },
      { item: "pocketbudjet.com (domain)", monthly: 1.0, note: "estimate" },
      { item: "Apple Developer Program", monthly: 8.25, note: "$99/yr" },
      { item: "Google Play developer", monthly: 0.42, note: "$25 one-time ÷ 60 mo" },
      { item: "PocketHost / PocketBase", monthly: 5.0, note: "shared PBJ/HHH/CVC" },
      { item: "Cloudflare Workers", monthly: 0, note: "free tier" },
      { item: "GitHub Pages", monthly: 0, note: "" },
      { item: "Firebase Spark · RevenueCat · Expo EAS", monthly: 0, note: "free at current scale" },
    ],
    founder_tools: [
      { stack: "Lean", monthly: 15.67, cursor: 0, buffer: 0 },
      { stack: "Realistic", monthly: 35.67, cursor: 20, buffer: 0 },
      { stack: "Comfort", monthly: 50.67, cursor: 20, buffer: 15 },
    ],
  };
  const JOE_SUBS_KEY = "joe_paying_subs";
  const JOE_MRR_KEY = "joe_mrr_manual";

  function getJoePayingSubs() {
    const v = parseInt(localStorage.getItem(JOE_SUBS_KEY) || "0", 10);
    return Number.isFinite(v) && v >= 0 ? v : 0;
  }

  function saveJoePayingSubs() {
    const el = document.getElementById("joePayingSubs");
    const v = parseInt(el?.value || "0", 10);
    localStorage.setItem(JOE_SUBS_KEY, String(Number.isFinite(v) && v >= 0 ? v : 0));
    renderBreakevenPanel();
  }

  function saveJoeMrrManual() {
    const el = document.getElementById("joeMrrManual");
    const raw = el?.value?.trim();
    if (!raw) {
      localStorage.removeItem(JOE_MRR_KEY);
    } else {
      const v = parseFloat(raw);
      localStorage.setItem(JOE_MRR_KEY, String(Number.isFinite(v) && v >= 0 ? v : 0));
    }
    renderBreakevenPanel();
  }

  function renderFounderCostTable() {
    const root = document.getElementById("founderBreakevenGrid");
    if (!root) return;
    const infraSubtotal = FIXED_COSTS.lines.reduce((s, l) => s + l.monthly, 0);
    const rows = FIXED_COSTS.lines.map(l => `
      <tr>
        <td>${l.item}${l.note ? ` <span style="color:var(--text-muted)">(${l.note})</span>` : ""}</td>
        <td class="num">$${l.monthly.toFixed(2)}</td>
      </tr>`).join("");
    const stackRows = FIXED_COSTS.founder_tools.map(s => `
      <tr>
        <td><strong>${s.stack}</strong> stack${s.cursor ? ` (+ Cursor $${s.cursor})` : ""}${s.buffer ? ` (+ buffer $${s.buffer})` : ""}</td>
        <td class="num">$${s.monthly.toFixed(2)} · ${FIXED_COSTS.breakeven_subs[s.stack.toLowerCase()]} subs</td>
      </tr>`).join("");
    root.innerHTML = `
      <div class="founder-cost-wrap">
        <table>
          <thead><tr><th>Fixed line item</th><th>$/mo</th></tr></thead>
          <tbody>${rows}
            <tr class="subtotal"><td>Infra subtotal</td><td class="num">$${infraSubtotal.toFixed(2)}</td></tr>
            ${stackRows}
          </tbody>
        </table>
        <div class="cost-note">Source: <code>docs/JOE_OPS_COSTS.md</code> (PBJ repo). Variable: Gemini overage, Claude, Teller prod — see panels below.</div>
      </div>`;
  }

  function renderBreakevenPanel() {
    const grid = document.getElementById("breakevenGrid");
    const status = document.getElementById("breakevenStatus");
    if (!grid) return;

    const subs = getJoePayingSubs();
    const manualMrr = localStorage.getItem(JOE_MRR_KEY);
    const mrr = manualMrr != null && manualMrr !== ""
      ? parseFloat(manualMrr)
      : subs * FIXED_COSTS.net_per_monthly_sub;

    grid.innerHTML = `
      <div class="be-grid">
        ${["lean", "realistic", "comfort"].map(stack => `
          <div class="be-card">
            <div class="be-label">${stack.charAt(0).toUpperCase() + stack.slice(1)} stack</div>
            <div class="be-value">$${FIXED_COSTS.stacks[stack].toFixed(2)}/mo</div>
            <div class="be-sub">${FIXED_COSTS.breakeven_subs[stack]} paying subs @ $${FIXED_COSTS.net_per_monthly_sub} net</div>
          </div>
        `).join("")}
        <div class="be-card">
          <div class="be-label">Your net MRR (est.)</div>
          <div class="be-value">$${mrr.toFixed(2)}/mo</div>
          <div class="be-sub">${subs} paying monthly subs × $${FIXED_COSTS.net_per_monthly_sub}</div>
        </div>
      </div>`;

    if (status) {
      const realistic = FIXED_COSTS.stacks.realistic;
      const comfort = FIXED_COSTS.stacks.comfort;
      let cls = "be-status-bad";
      let msg = `Below realistic breakeven — need ${FIXED_COSTS.breakeven_subs.realistic} subs ($${realistic.toFixed(2)}/mo fixed).`;
      if (mrr >= comfort) {
        cls = "be-status-ok";
        msg = `At or above comfort stack ($${comfort.toFixed(2)}/mo) — ${subs} subs cover fixed burn + buffer.`;
      } else if (mrr >= realistic) {
        cls = "be-status-warn";
        msg = `Covers realistic stack ($${realistic.toFixed(2)}/mo) — ${subs} subs; comfort needs ${FIXED_COSTS.breakeven_subs.comfort}.`;
      } else if (mrr >= FIXED_COSTS.stacks.lean) {
        cls = "be-status-warn";
        msg = `Covers lean infra only ($${FIXED_COSTS.stacks.lean.toFixed(2)}/mo) — realistic needs ${FIXED_COSTS.breakeven_subs.realistic} subs.`;
      }
      status.innerHTML = `<span class="${cls}">${msg}</span>`;
    }

    const subsEl = document.getElementById("joePayingSubs");
    const mrrEl = document.getElementById("joeMrrManual");
    if (subsEl && document.activeElement !== subsEl) subsEl.value = subs || "";
    if (mrrEl && document.activeElement !== mrrEl && manualMrr != null && manualMrr !== "") {
      mrrEl.value = parseFloat(manualMrr).toFixed(2);
    }
  }

  function renderSubscriptionUsersCard(row) {
    const hb = row.heartbeats || {};
    const rc = row.revenuecat || {};
    const rcPaying = rc.paying_subscribers != null ? rc.paying_subscribers : "—";
    const rcTrials = rc.active_trials != null ? rc.active_trials : "—";
    const rcNote = rc.error
      ? `RevenueCat: ${rc.error}`
      : rc.configured
        ? (rc.project_id ? "RevenueCat project wired" : "RC key set — add project id for this app")
        : (rc.hint || "RevenueCat not configured on Worker");
    const hbNote = hb.source === "unavailable"
      ? (hb.hint || "Heartbeats unavailable")
      : `${hb.total_devices ?? 0} devices with heartbeat in last ${hb.active_window_days ?? 30} days`;

    return `
      <div class="sub-users-card">
        <h3>${row.display_name || row.app}</h3>
        <div class="sub-users-source-tag">RevenueCat — store subscriptions</div>
        <div class="sub-users-metrics">
          <div class="sub-users-metric paying">
            <div class="lbl">Paying subscribers</div>
            <div class="val">${rcPaying}</div>
            <div class="hint">Active paid subs in App Store / Play right now. Billing truth for MRR.</div>
          </div>
          <div class="sub-users-metric trial">
            <div class="lbl">Store trials in progress</div>
            <div class="val">${rcTrials}</div>
            <div class="hint">Free intro period started via store; card on file, not charged yet.</div>
          </div>
        </div>
        <div class="sub-users-source-tag">App heartbeats — installs (30 days)</div>
        <div class="sub-users-metrics">
          <div class="sub-users-metric trial">
            <div class="lbl">In trial (app)</div>
            <div class="val">${hb.trial ?? 0}</div>
            <div class="hint">Devices the app reports as in a trial window. May differ from RC until store trials ship.</div>
          </div>
          <div class="sub-users-metric paying">
            <div class="lbl">Pro / paying (app)</div>
            <div class="val">${hb.active ?? 0}</div>
            <div class="hint">Devices the app reports as entitled to Pro features.</div>
          </div>
          <div class="sub-users-metric">
            <div class="lbl">Free tier</div>
            <div class="val">${hb.free ?? 0}</div>
            <div class="hint">Installed and using the app without Pro — no card required.</div>
          </div>
          <div class="sub-users-metric">
            <div class="lbl">Trial ended, not paying</div>
            <div class="val">${hb.expired ?? 0}</div>
            <div class="hint">Trial over, still opening the app, has not subscribed.</div>
          </div>
        </div>
        <div class="sub-users-foot"><strong>RC:</strong> ${rcNote}<br><strong>Heartbeats:</strong> ${hbNote}</div>
      </div>`;
  }

  async function loadSubscriptionUsers() {
    const grid = document.getElementById("subscriptionUsersGrid");
    const hint = document.getElementById("subscriptionUsersHint");
    if (!grid) return;

    const key = localStorage.getItem("pbj_shared_key") || "";
    if (!key) {
      grid.innerHTML = `<p class="section-explainer">Enter your PBJ Worker key (smoke test or Worker Monitoring) so this panel can call <code>/ops/subscriptions</code>.</p>`;
      if (hint) hint.textContent = "Needs X-PBJ-Key in this browser.";
      return;
    }

    grid.innerHTML = "Loading…";
    if (hint) hint.textContent = "";

    try {
      const r = await fetch(`${WORKER_BASE}/ops/subscriptions`, {
        headers: { "X-PBJ-Key": key },
        signal: AbortSignal.timeout(12000),
      });
      if (!r.ok) {
        grid.innerHTML = `<p class="section-explainer" style="color:var(--danger);">HTTP ${r.status} — deploy the PBJ Worker with <code>/ops/subscriptions</code> and retry.</p>`;
        if (hint) hint.textContent = `Failed ${new Date().toLocaleTimeString()}`;
        return;
      }
      const j = await r.json();
      const apps = Array.isArray(j.apps) ? j.apps : [];
      const totals = j.totals || {};
      grid.innerHTML = `
        <div class="sub-users-grid">${apps.map(renderSubscriptionUsersCard).join("")}</div>
        <div class="sub-users-totals">
          <strong>Totals across PBJ + HHH + CVC</strong><br>
          <span style="color:var(--text-dim);font-size:12px;">
            Heartbeats (unique devices, last 30 days):
            ${totals.trial ?? 0} in trial · ${totals.active ?? 0} Pro · ${totals.free ?? 0} free · ${totals.expired ?? 0} trial ended
            (${totals.total_devices ?? 0} devices reported at least once)
            ${totals.paying_revenuecat != null ? `<br>RevenueCat (all wired projects): ${totals.paying_revenuecat} paying · ${totals.trials_revenuecat ?? 0} store trials` : ""}
          </span>
        </div>`;
      if (hint) {
        hint.textContent = `Updated ${new Date(j.generated_at || Date.now()).toLocaleString()}`;
      }
    } catch (e) {
      grid.innerHTML = `<p class="section-explainer" style="color:var(--danger);">Network error — ${String(e).slice(0, 120)}</p>`;
      if (hint) hint.textContent = "Refresh failed";
    }
  }


  function pctRate(r) {
    if (r == null || Number.isNaN(r)) return "—";
    return (r * 100).toFixed(1) + "%";
  }

  const RUNTIME_TRUTH_JSON_URL =
    "https://raw.githubusercontent.com/josspa1/PocketBudJet/master/docs/runtime-truth-data.json";
  const RUNTIME_TRUTH_DOC_URL =
    "https://github.com/josspa1/PocketBudJet/blob/master/docs/RUNTIME_TRUTH.md";
  const FIREBASE_PBJ_CONSOLE =
    "https://console.firebase.google.com/project/pocketbudjet-b70f3";
  const RUNTIME_CRASH_FREE_GATE = 99;
  const RUNTIME_P95_GATE_MS = 2500;

  function runtimeFmtMs(ms) {
    if (ms == null || Number.isNaN(ms)) return "—";
    if (ms >= 1000) return (ms / 1000).toFixed(1) + "s";
    return Math.round(ms) + "ms";
  }

  function runtimeGateBadge(pass) {
    if (pass === true) return '<span style="color:var(--success);font-weight:700;">PASS</span>';
    if (pass === false) return '<span style="color:var(--danger);font-weight:700;">FAIL</span>';
    return '<span style="color:var(--text-muted);">—</span>';
  }

  async function loadRuntimeTruthFromGithub() {
    const grid = document.getElementById("runtimeTruthGrid");
    const hint = document.getElementById("runtimeTruthHint");
    if (!grid) return;
    grid.textContent = "Loading…";
    try {
      const r = await fetch(RUNTIME_TRUTH_JSON_URL, {
        signal: AbortSignal.timeout(12000),
        headers: { Accept: "application/json" },
      });
      if (!r.ok) {
        grid.innerHTML = `<p style="color:var(--danger);">HTTP ${r.status} — JSON not reachable.</p>`;
        if (hint) hint.textContent = "";
        return;
      }
      const j = await r.json();
      const build = j.metricsBuild ?? "—";
      const crashFree = j.crashFreeSessionsPct;
      const p95 = j.coldStartP95Ms;
      const crashPass = crashFree == null ? null : crashFree >= RUNTIME_CRASH_FREE_GATE;
      const p95Pass = p95 == null ? null : p95 <= RUNTIME_P95_GATE_MS;
      const gatePass = crashPass === null || p95Pass === null ? null : crashPass && p95Pass;
      if (hint) {
        const windowTxt = j.dateRangeStart && j.dateRangeEnd
          ? `${j.dateRangeStart} → ${j.dateRangeEnd}`
          : "";
        hint.textContent = [windowTxt, j.dataSource].filter(Boolean).join(" · ");
      }
      grid.innerHTML = `<div class="be-grid">
        <div class="be-card">
          <div class="be-label">Metrics build</div>
          <div class="be-value">${build}</div>
          <div class="be-sub">Source JSON build number</div>
        </div>
        <div class="be-card">
          <div class="be-label">Crash-free (≥ ${RUNTIME_CRASH_FREE_GATE}%)</div>
          <div class="be-value" style="color:${crashPass === false ? "var(--danger)" : crashPass ? "var(--success)" : "var(--primary)"};">
            ${crashFree == null ? "—" : crashFree.toFixed(1) + "%"}
          </div>
          <div class="be-sub">${runtimeGateBadge(crashPass)} vs gate</div>
        </div>
        <div class="be-card">
          <div class="be-label">Cold start P95 (≤ ${runtimeFmtMs(RUNTIME_P95_GATE_MS)})</div>
          <div class="be-value" style="color:${p95Pass === false ? "var(--danger)" : p95Pass ? "var(--success)" : "var(--primary)"};">
            ${runtimeFmtMs(p95)}
          </div>
          <div class="be-sub">${runtimeGateBadge(p95Pass)} vs gate</div>
        </div>
        <div class="be-card">
          <div class="be-label">Ship gate</div>
          <div class="be-value">${runtimeGateBadge(gatePass)}</div>
          <div class="be-sub">Both metrics must pass</div>
        </div>
      </div>
      <p style="margin-top:12px;font-size:12px;color:var(--text-muted);">
        <a href="${RUNTIME_TRUTH_DOC_URL}" target="_blank" rel="noopener noreferrer">RUNTIME_TRUTH.md</a>
        · <a href="${FIREBASE_PBJ_CONSOLE}/crashlytics" target="_blank" rel="noopener noreferrer">Firebase Crashlytics</a>
        · <a href="${FIREBASE_PBJ_CONSOLE}/performance" target="_blank" rel="noopener noreferrer">Firebase Performance</a>
        ${j.notes ? `<br><span style="font-style:italic;">${j.notes}</span>` : ""}
      </p>`;
    } catch (e) {
      grid.innerHTML = `<p style="color:var(--danger);">${e instanceof Error ? e.message : String(e)}</p>`;
      if (hint) hint.textContent = "";
    }
  }

  async function loadCommercialProofFromWorker() {
    const grid = document.getElementById("commercialProofGrid");
    const hint = document.getElementById("commercialProofHint");
    if (!grid) return;
    const app = WORKER_APPS.find(a => a.id === "pbj") || WORKER_APPS[0];
    const key = wmGetKey(app, false);
    const base = wmGetUrl(app);
    if (!key) {
      if (hint) hint.textContent = "Set X-PBJ-Key (run PBJ smoke test once).";
      grid.innerHTML = "<p style=\"color:var(--warning);font-size:12px;\">Worker key not in browser.</p>";
      return;
    }
    grid.textContent = "Loading…";
    try {
      const r = await fetch(`${base}/ops/commercial-proof`, {
        headers: { [app.authHeader]: key },
        signal: AbortSignal.timeout(12000),
      });
      if (r.status === 404) {
        grid.innerHTML = "<p style=\"color:var(--warning);\">/ops/commercial-proof not deployed — run wrangler deploy on PBJ worker.</p>";
        return;
      }
      if (!r.ok) {
        grid.innerHTML = `<p style=\"color:var(--danger);\">HTTP ${r.status}</p>`;
        return;
      }
      const j = await r.json();
      const c = j.counts || {};
      const rates = j.rates || {};
      if (hint) {
        hint.textContent = j.generated_at
          ? `Updated ${new Date(j.generated_at).toLocaleString()} · ${j.unique_devices ?? c.unique_devices ?? 0} devices (90d window)`
          : "";
      }
      grid.innerHTML = `<table><thead><tr><th>Metric</th><th>Count</th></tr></thead><tbody>
        <tr><td>Import success</td><td><strong>${c.import_success ?? 0}</strong></td></tr>
        <tr><td>Post-import home view</td><td><strong>${c.post_import_home_view ?? 0}</strong></td></tr>
        <tr><td>Activation complete</td><td><strong>${c.activation_complete ?? 0}</strong></td></tr>
        <tr><td>Trial start</td><td><strong>${c.trial_start ?? 0}</strong></td></tr>
        <tr><td>Trial convert</td><td><strong>${c.trial_convert ?? 0}</strong></td></tr>
        <tr><td>Subscribe success</td><td><strong>${c.subscribe_success ?? 0}</strong></td></tr>
        <tr><td>Unique devices</td><td><strong>${c.unique_devices ?? 0}</strong></td></tr>
      </tbody></table>
      <p style=\"margin-top:10px;font-size:12px;color:var(--text-muted);\">
        Import→home ${pctRate(rates.import_to_home)} · trial→paid ${pctRate(rates.trial_to_paid)} · subscribe start→success ${pctRate(rates.subscribe_start_to_success)}
      </p>`;
    } catch (e) {
      grid.innerHTML = `<p style=\"color:var(--danger);\">${e instanceof Error ? e.message : String(e)}</p>`;
    }
  }
  async function loadRevenueFromWorker() {
    const hint = document.getElementById("revenueCatHint");
    if (!hint) return;
    const key = localStorage.getItem("pbj_shared_key") || "";
    if (!key) {
      hint.textContent = "RevenueCat: enter paying subs above. Worker /ops/revenue needs X-PBJ-Key in this browser.";
      return;
    }
    try {
      const r = await fetch(`${WORKER_BASE}/ops/revenue`, {
        headers: { "X-PBJ-Key": key },
        signal: AbortSignal.timeout(8000),
      });
      if (!r.ok) {
        hint.textContent = `RevenueCat API not available (HTTP ${r.status}) — use manual paying subs field.`;
        return;
      }
      const j = await r.json();
      if (j.source === "api" && j.paying_subscribers != null) {
        localStorage.setItem(JOE_SUBS_KEY, String(Math.round(j.paying_subscribers)));
        const mrrEl = document.getElementById("joeMrrManual");
        if (j.mrr_usd != null && mrrEl) {
          mrrEl.value = Number(j.mrr_usd).toFixed(2);
          localStorage.setItem(JOE_MRR_KEY, String(j.mrr_usd));
        }
        renderBreakevenPanel();
        hint.textContent = `RevenueCat live: ${j.paying_subscribers} active subs${j.mrr_usd != null ? ` · $${Number(j.mrr_usd).toFixed(2)} MRR` : ""}.`;
      } else if (j.hint) {
        hint.textContent = j.hint;
      } else if (j.error) {
        hint.textContent = `RevenueCat error: ${j.error} — use manual field.`;
      } else {
        hint.textContent = "RevenueCat not configured on Worker — enter paying subs manually (saved in this browser).";
      }
    } catch {
      hint.textContent = "Could not reach /ops/revenue — enter paying subs manually.";
    }
  }

  /* ─── Proactive ops alerts (red = outage/quota; amber = housekeeping) ─── */
  function opsAnthropicInfoLines() {
    const h = antGetHistory();
    if (h.length === 0) {
      return ["Anthropic Claude — no balance logged yet. The API is not down; tap Record balance in the Anthropic service card after checking platform.claude.com billing."];
    }
    const last = h[h.length - 1];
    const ageDays = (Date.now() - new Date(last.at)) / 86400000;
    const lines = [];
    if (ageDays > 14) {
      lines.push(
        `Anthropic Claude — last balance log is ${Math.floor(ageDays)} days old ($${last.amount.toFixed(2)}). Service is not down — record current credits from the billing page.`,
      );
    }
    if (last.amount < 5) {
      lines.push(`Anthropic Claude — logged balance is low ($${last.amount.toFixed(2)}). Top up credits before HHH/CVC identify calls fail with 402.`);
    } else if (last.amount < 10 && ageDays <= 14) {
      lines.push(`Anthropic Claude — logged balance is getting low ($${last.amount.toFixed(2)}). Plan a top-up soon.`);
    }
    return lines;
  }

  async function updateOpsAlertBanner() {
    const banner = document.getElementById("opsAlertBanner");
    const infoBanner = document.getElementById("opsInfoBanner");
    if (!banner || !token) {
      if (banner) banner.style.display = "none";
      if (infoBanner) infoBanner.style.display = "none";
      return;
    }

    const issues = [];
    const infoIssues = [];
    const key = localStorage.getItem("pbj_shared_key") || "";

    const pbjStats =
      ocrQuotaCache?.data ||
      wmCache?.results?.find(r => r.app.id === "pbj")?.stats?.data;

    if (pbjStats) {
      const geminiCap = pbjStats.freeTier?.geminiDaily || 1500;
      const geminiPct = geminiCap > 0 ? (pbjStats.today.gemini / geminiCap) * 100 : 0;
      if (geminiPct >= 80) {
        issues.push(`PBJ Gemini daily quota at ${geminiPct.toFixed(0)}% (${pbjStats.today.gemini.toLocaleString()} / ${geminiCap.toLocaleString()})`);
      }
      if (pbjStats.today.circuitBreakerArmed) {
        issues.push("PBJ OCR circuit breaker ARMED — free users denied cloud OCR");
      }
    } else if (key) {
      try {
        const r = await fetch(`${WORKER_BASE}/`, { cache: "no-store", signal: AbortSignal.timeout(6000) });
        if (!r.ok) issues.push(`PBJ Worker health ping failed (HTTP ${r.status})`);
      } catch {
        issues.push("PBJ Worker health ping failed — pbj-import-worker may be down");
      }
      infoIssues.push("PBJ quota — load Worker Monitoring Medium or OCR panel for Gemini/breaker checks (skipped KV stats poll).");
    } else {
      infoIssues.push("PBJ Worker stats — X-PBJ-Key not set in this browser (run a PBJ smoke test once; worker may still be healthy).");
    }

    for (const app of WORKER_APPS.filter(a => a.statsKind === "ops")) {
      const appKey = wmGetKey(app, false);
      const base = wmGetUrl(app);
      try {
        const hr = await fetch(base + "/", { cache: "no-store", signal: AbortSignal.timeout(6000) });
        if (!hr.ok) {
          issues.push(`${app.short} worker health failed (HTTP ${hr.status})`);
          continue;
        }
        const hj = await hr.json();
        if (hj.gemini_configured === false) {
          infoIssues.push(`${app.short} (${app.name}) — Gemini API key not set on worker yet (identify may fall back to Anthropic).`);
        }
      } catch {
        issues.push(`${app.short} worker unreachable — ${base}`);
      }
      /* Skip /ops/stats KV poll — use wmCache from manual Medium refresh instead */
      if (appKey && wmCache?.results) {
        const wr = wmCache.results.find(x => x.app.id === app.id);
        const stats = wr?.stats?.data;
        if (stats) {
          const geminiCap = stats.caps?.geminiDaily || stats.freeTier?.geminiDaily || 1500;
          const geminiPct = geminiCap > 0 ? (stats.today.gemini / geminiCap) * 100 : 0;
          if (geminiPct >= 80) {
            issues.push(`${app.short} Gemini daily quota at ${geminiPct.toFixed(0)}% (${stats.today.gemini.toLocaleString()} / ${geminiCap.toLocaleString()})`);
          }
          if (stats.today.circuitBreakerArmed) {
            issues.push(`${app.short} AI circuit breaker ARMED`);
          }
        }
      }
    }

    try {
      const authHdr = token ? { Authorization: `Bearer ${token}` } : {};
      const r = await fetch(
        "https://josspatech.pockethost.io/api/collections/_cron_heartbeat/records?perPage=1&sort=-last_run&filter=" +
        encodeURIComponent('name="aggregate_submissions"'),
        { headers: authHdr, signal: AbortSignal.timeout(8000) },
      );
      if (r.status === 429) {
        infoIssues.push("PocketBase rate-limited this tab's poll — cron status unknown right now. PocketBase is up; wait ~15 min or use Cron Health panel.");
      } else if (r.ok) {
        const j = await r.json();
        const lastRun = j.items?.[0]?.last_run;
        if (lastRun) {
          const minutes = (Date.now() - new Date(lastRun).getTime()) / 60000;
          if (minutes > 180) {
            infoIssues.push(
              `PocketBase aggregation cron last ran ${Math.round(minutes)} min ago — PBJ crowd-data flywheel only; HHH/CVC unaffected. See Cron Health panel if you care about merchant consensus.`,
            );
          }
        } else {
          infoIssues.push(
            "PocketBase aggregation cron — no heartbeat yet (pb_hooks may not be deployed). PBJ flywheel only; not a site outage.",
          );
        }
      } else if (r.status === 401 || r.status === 403) {
        infoIssues.push("PocketBase cron heartbeat — sign in again to read _cron_heartbeat (not a PocketBase outage).");
      } else if (r.status === 404) {
        infoIssues.push("PocketBase aggregation cron — _cron_heartbeat not set up yet (pb_hooks not deployed). Expected; HHH/CVC unaffected.");
      }
    } catch {
      infoIssues.push("PocketBase cron heartbeat — could not poll (network or rate limit). Check /api/health or Cron Health panel.");
    }

    infoIssues.push(...opsAnthropicInfoLines());

    await Promise.all(WORKER_APPS.map(async (app) => {
      const appKey = wmGetKey(app, false);
      if (!appKey) return;
      const data = await capFetch(app);
      capacityCache[app.id] = data;
    }));
    const capIssues = capacityIssuesFromCache();
    for (const ci of capIssues) {
      if (!issues.some(x => x.includes(ci.slice(0, 20)))) issues.push(ci);
    }
    renderCapacityBottleneckBanner();

    if (issues.length === 0) {
      banner.style.display = "none";
      banner.innerHTML = "";
      const infoBuy = infoIssues.filter(i => /anthropic|claude|balance|gemini/i.test(i));
      renderOpsBuyBar(infoBuy);
    } else {
      banner.innerHTML =
        `<div class="ops-alert-title">⚠ Ops alert — action needed</div>` +
        `<ul>${issues.map(i => `<li>${i}</li>`).join("")}</ul>`;
      banner.style.display = "block";
      renderOpsBuyBar(issues);
    }

    if (infoBanner) {
      if (infoIssues.length === 0) {
        infoBanner.style.display = "none";
        infoBanner.innerHTML = "";
      } else {
        infoBanner.innerHTML =
          `<div class="ops-info-title">ℹ Expected gaps — not an outage</div>` +
          `<ul>${infoIssues.map(i => `<li>${i}</li>`).join("")}</ul>`;
        infoBanner.style.display = "block";
      }
    }

    if (window.ADMIN_PAGE === "hub") {
      renderHubBriefStatus(issues, infoIssues);
    }
  }

  // Cache the most recent /health/quotas response so individual probes
  // can read from it. Refreshed on every refreshServiceStatus() call.
  let quotaCache = null;

  /** Convert a raw used/limit pair to a state + the meter's display
   *  color. Thresholds: <60% green, 60–85% yellow, >85% red. */
  function stateFromPercent(pct) {
    if (pct < 0.60) return "green";
    if (pct < 0.85) return "yellow";
    return "red";
  }

  /** Compact number formatter: 1234 → "1.23K", 1500000 → "1.5M". */
  function fmtNum(n) {
    if (n == null || isNaN(n)) return "—";
    if (Math.abs(n) >= 1e6) return (n / 1e6).toFixed(1).replace(/\.0$/, "") + "M";
    if (Math.abs(n) >= 1e3) return (n / 1e3).toFixed(1).replace(/\.0$/, "") + "K";
    if (Math.abs(n) >= 1)   return n.toLocaleString("en-US", { maximumFractionDigits: 2 });
    return n.toFixed(2); // currency-like sub-dollar
  }

  /** Build a probe that reads its data from the cached /health/quotas
   *  response. Used for services where the Worker tracks the count. */
  function quotaProbe(quotaKey) {
    return async () => {
      const q = quotaCache?.[quotaKey];
      if (!q || typeof q.used !== "number" || typeof q.limit !== "number") {
        return { state: "unknown" };
      }
      const pct = q.limit > 0 ? q.used / q.limit : 0;
      return {
        state: stateFromPercent(pct),
        used:  q.used,
        limit: q.limit,
        unit:  q.unit || "",
      };
    };
  }

  // ─── Anthropic balance tracker ────────────────────────────
  // Manual log of credit balance. Joe checks platform.claude.com/settings/billing,
  // taps "Record balance" here, types what he saw. We persist a short history in
  // localStorage so we can compute a rough burn-rate from consecutive readings.
  // Data is per-browser; not synced. Single-admin dashboard, that's fine.
  const ANT_HISTORY_KEY = "jt_anthropic_balance_history";
  const ANT_HISTORY_MAX = 12;

  function antGetHistory() {
    try {
      const arr = JSON.parse(localStorage.getItem(ANT_HISTORY_KEY) || "[]");
      return Array.isArray(arr) ? arr : [];
    } catch { return []; }
  }
  function antSetHistory(arr) {
    try { localStorage.setItem(ANT_HISTORY_KEY, JSON.stringify(arr)); }
    catch (e) { console.warn("ant: localStorage write failed", e); }
  }
  function antLogBalance() {
    const v = window.prompt(
      "Enter the credit balance you see on platform.claude.com (in dollars).\n" +
      "Example: 9.85"
    );
    if (v === null) return; // cancelled
    const num = parseFloat(String(v).replace(/[^0-9.]/g, ""));
    if (!isFinite(num) || num < 0) {
      alert("Couldn't read that as a number. Try again — just digits and a decimal point, like 9.85");
      return;
    }
    const history = antGetHistory();
    history.push({ amount: num, at: new Date().toISOString() });
    while (history.length > ANT_HISTORY_MAX) history.shift();
    antSetHistory(history);
    // Re-render the Services panel so the card updates immediately.
    renderServices(window.__lastServiceResults || {});
  }
  function antResetHistory() {
    if (!confirm("Clear all recorded Anthropic balance readings? This can't be undone.")) return;
    antSetHistory([]);
    renderServices(window.__lastServiceResults || {});
  }

  // Returns the most recent burn-rate window: a strictly-decreasing pair of
  // readings (so we don't treat a top-up as "negative burn"). Returns null
  // if we don't have one. Walks backward from the latest reading until it
  // finds the most recent prior reading where amount > latest.amount; that
  // window is the user's spend trajectory.
  function antBurnWindow() {
    const h = antGetHistory();
    if (h.length < 2) return null;
    const last = h[h.length - 1];
    for (let i = h.length - 2; i >= 0; i--) {
      const prev = h[i];
      if (prev.amount > last.amount) {
        const dt = (new Date(last.at) - new Date(prev.at)) / 86400000; // days
        if (dt <= 0) continue;
        const dv = prev.amount - last.amount;
        return { burnPerDay: dv / dt, days: dt, from: prev, to: last };
      }
    }
    return null;
  }

  // Card-state for the Anthropic service card — escalates if balance is low
  // OR the last reading is stale. "Don't know" is treated as a soft warning.
  function antDeriveState() {
    const h = antGetHistory();
    if (h.length === 0) return { state: "unknown" };
    const last = h[h.length - 1];
    const ageDays = (Date.now() - new Date(last.at)) / 86400000;
    if (last.amount < 5)  return { state: "red" };
    if (ageDays > 30)     return { state: "red" };  // truly stale
    if (last.amount < 10) return { state: "yellow" };
    if (ageDays > 14)     return { state: "yellow" };
    return { state: "green" };
  }

  // Render the tracker block. Inserted into the Anthropic card via SERVICES[i].extra.
  function antRenderTracker() {
    const h = antGetHistory();
    if (h.length === 0) {
      return `
        <div class="ant-tracker">
          <div class="ant-empty">No balance recorded yet — Anthropic API is not down. After you check the billing page, tap below to log what you see (manual tracker; stale by design until you record again).</div>
          <div class="ant-actions">
            <button class="ant-btn primary" onclick="antLogBalance()">Record balance</button>
            <a class="ant-btn" href="https://platform.claude.com/settings/billing" target="_blank" rel="noopener noreferrer">Open billing ↗</a>
          </div>
        </div>`;
    }
    const last = h[h.length - 1];
    const ageMs = Date.now() - new Date(last.at);
    const ageDays = Math.floor(ageMs / 86400000);
    const ageHours = Math.floor(ageMs / 3600000);
    let ageText;
    if (ageHours < 1)        ageText = "just now";
    else if (ageHours < 24)  ageText = `${ageHours} hour${ageHours === 1 ? "" : "s"} ago`;
    else if (ageDays === 1)  ageText = "yesterday";
    else                     ageText = `${ageDays} days ago`;
    let staleClass = "";
    if (ageDays > 30) staleClass = "stale-red";
    else if (ageDays > 14) staleClass = "stale-yellow";

    let balanceClass = "ok";
    if (last.amount < 5) balanceClass = "crit";
    else if (last.amount < 10) balanceClass = "warn";

    const burn = antBurnWindow();
    let burnHTML = "";
    if (burn) {
      const daysLeft = burn.burnPerDay > 0 ? last.amount / burn.burnPerDay : Infinity;
      const projection = isFinite(daysLeft)
        ? `≈ ${Math.floor(daysLeft)} day${Math.floor(daysLeft) === 1 ? "" : "s"} of runway at this pace`
        : "burn rate ~0";
      burnHTML = `
        <div class="ant-row">
          <span class="ant-label">Burn rate:</span>
          <span class="ant-value">$${burn.burnPerDay.toFixed(2)}/day</span>
          <span class="ant-aux">${projection}</span>
        </div>`;
    } else if (h.length >= 2) {
      burnHTML = `
        <div class="ant-row">
          <span class="ant-label">Burn rate:</span>
          <span class="ant-aux">— last change was a top-up; record again after some usage</span>
        </div>`;
    } else {
      burnHTML = `
        <div class="ant-row">
          <span class="ant-label">Burn rate:</span>
          <span class="ant-aux">— need a second reading to estimate</span>
        </div>`;
    }

    // Compact history (last 4) — collapsed by default would be nice but
    // we'll just show inline for simplicity.
    const histRows = h.slice(-4).reverse().map(r => {
      const d = new Date(r.at);
      const stamp = `${d.getFullYear()}-${String(d.getMonth()+1).padStart(2,"0")}-${String(d.getDate()).padStart(2,"0")} ${String(d.getHours()).padStart(2,"0")}:${String(d.getMinutes()).padStart(2,"0")}`;
      return `<div class="ant-history-row"><span>${stamp}</span><span>$${r.amount.toFixed(2)}</span></div>`;
    }).join("");

    return `
      <div class="ant-tracker">
        <div class="ant-row">
          <span class="ant-label">Last known balance:</span>
          <span class="ant-value ant-balance ${balanceClass}">$${last.amount.toFixed(2)}</span>
          <span class="ant-aux ${staleClass}">checked ${ageText}</span>
        </div>
        ${burnHTML}
        <div class="ant-actions">
          <button class="ant-btn primary" onclick="antLogBalance()">Record balance</button>
          <a class="ant-btn" href="https://platform.claude.com/settings/billing" target="_blank" rel="noopener noreferrer">Top up ↗</a>
          <button class="ant-btn" onclick="antResetHistory()" title="Clear recorded readings">Reset</button>
        </div>
        <div class="ant-history" title="Recent readings">${histRows}</div>
      </div>`;
  }

  const SERVICES = [
    {
      name: "Cloudflare Worker — pbj-import-worker",
      tier: "free",
      desc: "AI/OCR proxy for receipts, PDFs, and HHH/CVC identification. Hosts /vision/*, /identify/*, /ask, /anthropic-proxy.",
      quota: "Free: 100K req/day, 10ms CPU. Paid ($5/mo): 10M req/month + 50ms.",
      probe: async () => {
        // Try the /health/quotas endpoint first — gives us numeric usage.
        // Falls back to the basic / health check if /health/quotas isn't
        // deployed yet (tomorrow's Worker redeploy ships it).
        const q = quotaCache?.cloudflare_worker;
        if (q && typeof q.used === "number" && typeof q.limit === "number") {
          return { state: stateFromPercent(q.used / q.limit), used: q.used, limit: q.limit, unit: "req/day" };
        }
        try {
          const r = await fetch(WORKER_BASE + "/", { cache: "no-store", signal: AbortSignal.timeout(5000) });
          if (!r.ok) return { state: "red" };
          const j = await r.json();
          return { state: j.ok ? "green" : "yellow" };
        } catch { return { state: "red" }; }
      },
      buy: "cloudflare",
      links: [
        { label: "Health endpoint",   url: "https://pbj-import-worker.morning-star-b5e0.workers.dev/", primary: true },
        { label: "Cloudflare dash",   url: "https://dash.cloudflare.com/" },
        { label: "Worker limits",     url: "https://developers.cloudflare.com/workers/platform/limits/" },
      ],
    },
    {
      name: "PocketBase — josspatech instance",
      tier: "paid",
      desc: "Crowd-data backend. Shared by PBJ + HHH + CVC. FTPS quirk: use curl, not WinSCP (Session 68 notes).",
      quota: "PocketHost smart tier: 5GB DB. Migration runbook in ClaudeFiles/HETZNER_MIGRATION_RUNBOOK.md.",
      buy: "pockethost",
      probe: async () => {
        const q = quotaCache?.pocketbase_db;
        if (q && typeof q.used === "number" && typeof q.limit === "number") {
          return { state: stateFromPercent(q.used / q.limit), used: q.used, limit: q.limit, unit: "MB" };
        }
        try {
          const r = await fetch("https://josspatech.pockethost.io/api/health", { cache: "no-store", signal: AbortSignal.timeout(8000) });
          if (!r.ok) return { state: r.status === 429 ? "yellow" : "red" };
          const j = await r.json();
          return { state: j.code === 200 ? "green" : "yellow" };
        } catch {
          return { state: "yellow" }; // slow/timeout — not proven down
        }
      },
      links: [
        { label: "PocketBase admin",   url: "https://josspatech.pockethost.io/_/", primary: true },
        { label: "PocketHost dash",    url: "https://pockethost.io/dashboard" },
        { label: "Status page",        url: "https://status.pockethost.io/" },
      ],
    },
    {
      name: "Gemini Flash (Google AI Studio)",
      tier: "free",
      desc: "Vision parser for receipts (/vision/receipt) and bank statements (/vision/pdf). Worker secret: GEMINI_API_KEY.",
      quota: "Free: 1,500 req/day. Paid: ~$0.0002 per receipt-vision call → ~$450/mo at 75K calls/day.",
      buy: "gemini",
      probe: quotaProbe("gemini"),
      links: [
        { label: "Usage dashboard",    url: "https://aistudio.google.com/app/usage", primary: true },
        { label: "Manage keys",        url: "https://aistudio.google.com/app/apikey" },
        { label: "Add billing/alerts", url: "https://console.cloud.google.com/billing" },
      ],
    },
    {
      name: "Anthropic Claude",
      tier: "paid",
      desc: "Identification (HHH/CVC) and general AI calls (/ask, /identify/*, /anthropic-proxy). Worker secret ANTHROPIC_API_KEY is deployed.",
      quota: "Pre-paid credits, manual top-up (auto-reload off). ~$0.003–0.005 per identify call. Track balance via the panel below — record what you see when you check the billing page.",
      probe: quotaProbe("anthropic_credit"),
      // Custom widget renders inside the card. Lets Joe log the balance he
      // sees on platform.claude.com without integrating Anthropic's Admin API
      // (which would need yet another key + a Worker proxy). Stores readings
      // in localStorage so each browser keeps its own log; that's fine for a
      // single-admin dashboard. Stays one click away from the billing page
      // and surfaces stale or low balances back into the card's status light.
      extra: () => antRenderTracker(),
      stateOverride: () => antDeriveState(),
      buy: "anthropic",
      links: [
        { label: "Buy credits / billing", url: "https://platform.claude.com/settings/billing", primary: true },
        { label: "Usage",                 url: "https://platform.claude.com/settings/usage" },
        { label: "Manage keys",           url: "https://platform.claude.com/settings/keys" },
      ],
    },
    {
      name: "OCR.Space",
      tier: "free",
      desc: "Stage 2 OCR cloud fallback when on-device OCR returns thin results. Used by receipt scan and PDF import.",
      quota: "Free: 25K/month + 500/day per IP + 1MB. PRO ($30/mo): 300K + 5MB.",
      buy: "ocr_space",
      probe: quotaProbe("ocr_space"),
      links: [
        { label: "Account dashboard",  url: "https://ocr.space/ocrapi", primary: true },
        { label: "Get / view key",     url: "https://ocr.space/ocrapikey" },
        { label: "Upgrade to PRO",     url: "https://ocr.space/ocrapi#price" },
      ],
    },
    {
      name: "RevenueCat",
      tier: "free",
      desc: "Subscription management. Anonymous app-user IDs, IAP receipt validation, churn analytics. Used by PBJ; HHH/CVC will adopt.",
      quota: "Free up to $10K MTR. Past that: 1% of MTR. At ~$30K MTR (3K subscribers × $9.99) → ~$200/mo.",
      buy: "revenuecat",
      probe: quotaProbe("revenuecat_mtr"),
      links: [
        { label: "Dashboard",          url: "https://app.revenuecat.com/", primary: true },
        { label: "Projects",           url: "https://app.revenuecat.com/projects" },
        { label: "Pricing",            url: "https://www.revenuecat.com/pricing/" },
      ],
    },
    {
      name: "Firebase / Crashlytics",
      tier: "free",
      desc: "Crash reporting + analytics for PBJ. google-services.json + GoogleService-Info.plist baked into Builds.",
      quota: "Spark plan: generous for solo-dev volume. No action needed unless usage exceeds Spark caps.",
      probe: null,
      links: [
        { label: "PBJ Firebase",       url: "https://console.firebase.google.com/project/pocketbudjet-b70f3", primary: true },
        { label: "All projects",       url: "https://console.firebase.google.com/" },
      ],
    },
    {
      name: "Apple App Store Connect",
      tier: "paid",
      desc: "PBJ live listing + TestFlight. iOS submission, pricing, screenshots, In-App Purchases.",
      quota: "$99/year Apple Developer fee, auto-renew. Set calendar reminder if turning off auto-renew.",
      probe: null,
      links: [
        { label: "App Store Connect",  url: "https://appstoreconnect.apple.com/", primary: true },
        { label: "Apple Developer",    url: "https://developer.apple.com/account/" },
        { label: "Users / access",     url: "https://appstoreconnect.apple.com/access/users" },
      ],
    },
    {
      name: "Google Play Console",
      tier: "paid",
      desc: "PBJ Play Store listing + closed testing. Android submission, rollout, billing.",
      quota: "$25 one-time Google Dev fee. 12-tester gate: use BetaFamily ($30–50, 14 days).",
      probe: null,
      links: [
        { label: "Play Console",       url: "https://play.google.com/console/", primary: true },
        { label: "Closed testing",     url: "https://play.google.com/console/u/0/developers/closed-testing" },
        { label: "BetaFamily",         url: "https://betafamily.com/" },
      ],
    },
    {
      name: "Expo / EAS",
      tier: "free",
      desc: "iOS cloud builds + submission. (Android builds are local Gradle from C:\\PBJ\\android.)",
      quota: "Free: 30 builds/month. Paid tiers from $19/mo if needed.",
      buy: "expo",
      probe: null,
      links: [
        { label: "Expo dashboard",     url: "https://expo.dev/", primary: true },
        { label: "Projects",           url: "https://expo.dev/accounts/josspatech/projects" },
        { label: "Billing",            url: "https://expo.dev/accounts/josspatech/settings/billing" },
      ],
    },
    {
      name: "GitHub",
      tier: "free",
      desc: "Source control (private app repos) + GitHub Pages hosting for josspatech.com.",
      quota: "Free: private repos, GitHub Pages, sufficient for solo dev.",
      probe: async () => {
        // GitHub status API is CORS-friendly. Status-only — no usage meter.
        try {
          const r = await fetch("https://www.githubstatus.com/api/v2/status.json", {
            cache: "no-store",
            signal: AbortSignal.timeout(5000),
          });
          if (!r.ok) return { state: "yellow" };
          const j = await r.json();
          if (j?.status?.indicator === "none")  return { state: "green" };
          if (j?.status?.indicator === "minor") return { state: "yellow" };
          return { state: "red" };
        } catch { return { state: "unknown" }; }
      },
      links: [
        { label: "Profile",            url: "https://github.com/josspatech", primary: true },
        { label: "Status page",        url: "https://www.githubstatus.com/" },
      ],
    },
  ];

  function svcLightHTML(state) {
    const labels = {
      green:    "Online",
      yellow:   "Degraded",
      red:      "Down",
      checking: "Checking…",
      unknown:  "Manual check",
    };
    const cls = state || "unknown";
    return `<span class="svc-light ${cls}"><span class="dot"></span>${labels[cls] || labels.unknown}</span>`;
  }

  function svcStatusMeaning(state, result, service) {
    const pct = (result && typeof result.used === "number" && typeof result.limit === "number" && result.limit > 0)
      ? result.used / result.limit
      : null;
    if (pct != null && pct >= 0.9) {
      const buy = service?.buy ? (Array.isArray(service.buy) ? service.buy[0] : service.buy) : null;
      const link = buy && VENDOR_BUY[buy] ? ` Use the buy button below — ${VENDOR_BUY[buy].label}.` : " Use the buy button below.";
      return `Usage at ${(pct * 100).toFixed(0)}% of tracked cap — near limit.${link}`;
    }
    if (pct != null && pct >= 0.75) {
      return `Usage at ${(pct * 100).toFixed(0)}% of tracked cap — watch trend; buy link below if you're making money and need headroom.`;
    }
    if (state === "green") return "Last automatic check succeeded. Click a link below to confirm in the vendor UI.";
    if (state === "yellow") return "Reachable but slow, rate-limited, or missing config — verify in vendor dashboard.";
    if (state === "red") return "Probe failed — service may be down or keys misconfigured. Open dashboard link.";
    if (state === "checking") return "Probe in flight…";
    if (service && typeof service.stateOverride === "function") {
      return "Status from manual balance log in this card — record credits after checking billing.";
    }
    if (!service?.probe) return "No browser probe — open the dashboard link to check health and quotas.";
    return "Could not determine status — use dashboard link.";
  }

  /** Format a numeric meter "used / limit unit · NN%" with the same
   *  green/yellow/red coloring as the status light. Only renders when
   *  the probe returned numeric usage data; status-only results show
   *  nothing here. */
  function svcBuyRowHtml(s, cardState) {
    if (!s.buy) return "";
    const keys = Array.isArray(s.buy) ? s.buy : [s.buy];
    const primary = VENDOR_BUY[keys[0]];
    if (!primary) return "";
    const tgt = primary.internal ? "" : ' target="_blank" rel="noopener noreferrer"';
    const anchor = `<a href="${primary.url}"${tgt}>${primary.label} ↗</a>`;
    if (cardState === "crit" || cardState === "warn" || cardState === "red") {
      return `<div class="svc-buy-row">${anchor}</div>`;
    }
    return `<div class="svc-upgrade"><strong>Need more later?</strong> ${anchor}</div>`;
  }

  function svcMeterHTML(result) {
    if (!result || typeof result.used !== "number" || typeof result.limit !== "number") return "";
    const pct = result.limit > 0 ? Math.min(1, result.used / result.limit) : 0;
    const cls = stateFromPercent(pct);
    const unit = result.unit ? ` ${result.unit}` : "";
    const usedFmt  = fmtNum(result.used);
    const limitFmt = fmtNum(result.limit);
    const pctFmt   = (pct * 100).toFixed(pct < 0.10 ? 1 : 0);
    return `<span class="svc-meter ${cls}">${usedFmt} / ${limitFmt}${unit}<span class="pct">${pctFmt}%</span></span>`;
  }

  function renderServices(results /* { name → result | string } */) {
    // Cache the last results so card-internal widgets (e.g. the Anthropic
    // balance tracker) can trigger a re-render after a state change without
    // losing the most recent probe data.
    window.__lastServiceResults = results || {};

    const grid = document.getElementById("servicesGrid");
    if (!grid) return;
    grid.innerHTML = SERVICES.map(s => {
      // Normalize: results may carry the legacy plain-string state,
      // or the new { state, used?, limit?, unit? } object. Old probes
      // are dead, but the migration leaves this defensive.
      let r = results[s.name];
      if (typeof r === "string") r = { state: r };
      if (!r) r = { state: s.probe ? "checking" : "unknown" };

      // A service can supply `stateOverride()` to compute its own state
      // from local data (the Anthropic tracker does this — its state comes
      // from a manual balance log, not a network probe).
      if (typeof s.stateOverride === "function") {
        try {
          const o = s.stateOverride();
          if (o && o.state) r = { ...r, ...o };
        } catch (e) { console.warn("svc stateOverride failed for", s.name, e); }
      }
      const state = r.state;

      // Card border accent — meter percent overrides status when available
      // so capacity warnings dominate the visual hierarchy.
      let cardState = state;
      if (typeof r.used === "number" && typeof r.limit === "number" && r.limit > 0) {
        cardState = stateFromPercent(r.used / r.limit);
      }
      const cardCls = cardState === "red" ? "crit"
                    : cardState === "yellow" ? "warn"
                    : cardState === "green" ? "ok"
                    : s.tier === "todo" ? "todo" : "";

      const tierBadge = `<span class="svc-tier ${s.tier}">${s.tier}</span>`;
      const meter     = svcMeterHTML(r);
      const links = s.links.map(l =>
        `<a href="${l.url}" target="_blank" rel="noopener noreferrer" ${l.primary ? 'class="primary"' : ""}>${l.label} ↗</a>`
      ).join("");
      const extraHTML = (typeof s.extra === "function") ? (s.extra() || "") : "";
      return `
        <div class="svc-card ${cardCls}">
          <div class="svc-head">
            <div class="svc-name">${s.name}</div>
            ${svcLightHTML(state)}
          </div>
          <div class="svc-meter-row">
            ${tierBadge}
            ${meter}
          </div>
          <div class="svc-status-meaning">${svcStatusMeaning(state, r, s)}</div>
          <div class="svc-desc">${s.desc}</div>
          <div class="svc-links">${links}</div>
          <div class="svc-quota"><strong>Limits:</strong> ${s.quota}</div>
          ${svcBuyRowHtml(s, cardState)}
          ${extraHTML}
        </div>`;
    }).join("");
  }

  async function refreshServiceStatus() {
    // Step 1 — render placeholders so the UI snaps in immediately.
    const results = {};
    for (const s of SERVICES) results[s.name] = { state: s.probe ? "checking" : "unknown" };
    renderServices(results);
    document.getElementById("svcLastChecked").textContent = "Checking…";

    // Step 2 — bulk-fetch the Worker's /health/quotas snapshot. This
    // gives us the numeric usage for every auth-gated service in a
    // single network call. If it fails (Worker hasn't been redeployed
    // with the endpoint yet), individual probes fall back gracefully.
    try {
      const r = await fetch(WORKER_BASE + "/health/quotas", {
        cache: "no-store",
        signal: AbortSignal.timeout(7000),
      });
      if (r.ok) {
        quotaCache = await r.json();
      } else {
        quotaCache = null;
      }
    } catch {
      quotaCache = null;
    }

    // Step 3 — run individual probes in parallel; update each card as
    // it resolves. quota-driven probes pull from quotaCache.
    await Promise.all(SERVICES.map(async (s) => {
      if (!s.probe) { return; }
      try {
        results[s.name] = await s.probe();
      } catch {
        results[s.name] = { state: "red" };
      }
      renderServices(results);
    }));

    document.getElementById("svcLastChecked").textContent =
      `Last checked: ${new Date().toLocaleTimeString()}` +
      (quotaCache ? "" : "  ·  capacity numbers unavailable (Worker /health/quotas not deployed)");
  }

  // Auto-run once after the dashboard finishes loading. The existing
  // dashboard's grid renderer fires on login success — we hook off the
  // same window load to keep startup ordering predictable.
  window.addEventListener("DOMContentLoaded", () => {
    injectAdminNav();
    wireLoginEnterKey();

    if (token) {
      showDashboard();
    } else {
      document.getElementById("login").style.display = "block";
    }
  });

  function initAdminPage() {
    const page = window.ADMIN_PAGE || "flywheel";

    // Synchronous renders — no network
    if (document.getElementById("appVersionsTable")) renderAppVersions();
    if (document.getElementById("quickLinksGrid")) renderQuickLinks();
    if (document.getElementById("founderBreakeven")) renderFounderCostTable();
    if (document.getElementById("thresholdsPanel")) renderThresholdsBaselines();
    if (document.getElementById("upgradePlaybookGrid")) renderUpgradePlaybook();
    if (document.getElementById("vendorOnlyCapGrid")) renderVendorOnlyCapReminders();

    if (page === "hub") {
      updateOpsAlertBanner().catch(() => {});
      return;
    }

    setTimeout(() => {
      if (page === "flywheel") {
        refreshServiceStatus();
        loadCronHealth();
        loadQuarantineWatch();
        loadRecentCommits();
        loadCapacityControl();
        loadSubscriptionUsers();
        renderBreakevenPanel();
        loadCommercialProofFromWorker();
        loadRuntimeTruthFromGithub();
        loadRevenueFromWorker();
        updateOpsAlertBanner().catch(() => {});
      }
      if (page === "workers") {
        wmShowIdle();
        loadThresholdsSharedStats();
        updateOpsAlertBanner().catch(() => {});
      }
      if (page === "referrals") {
        refRender();
        updateOpsAlertBanner().catch(() => {});
      }
      if (page === "ocr") {
        loadOcrQuotaPanel();
        loadTellerStatusPanel();
        loadOpenCellIdPanel();
        updateOpsAlertBanner().catch(() => {});
      }
    }, 600);
  }