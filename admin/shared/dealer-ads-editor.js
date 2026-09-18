/* ─── Dealer Ads editor — HHH + CVC, client-only, no write API ───
   Pick the app, edit slots, Remove, postedAt date+time.
   Publish is still Copy / Download → commit the JSON to josspatech.github.io. */
(function () {
  var APPS = {
    hhh: {
      id: "hhh",
      label: "Handy Horology Helper",
      liveUrl: "../hhh/dealer-ads.json",
      commitPath: "hhh/dealer-ads.json",
      publicUrl: "https://josspatech.com/hhh/dealer-ads.json",
      trade: ["", "clocks", "watches", "both"],
    },
    cvc: {
      id: "cvc",
      label: "Curator's Vault: Classics",
      liveUrl: "../cvc/dealer-ads.json",
      commitPath: "cvc/dealer-ads.json",
      publicUrl: "https://josspatech.com/cvc/dealer-ads.json",
      trade: ["", "coins", "cards", "stamps", "currency", "lighters", "all"],
    },
  };
  var CAPS = { headline: 120, note: 200, businessName: 80, tagline: 120, cityRegion: 60, contactEmail: 120, contactPhone: 40 };

  var appId = window.ADMIN_PAGE === "cvc-dealer-ads" ? "cvc" : "hhh";
  var app = APPS[appId];
  var dirty = false;
  var state = blankState();

  function blankState() {
    return {
      enabled: true, comingSoon: false, hideForPro: false,
      headline: "", note: "", updatedAt: "",
      slots: [],
    };
  }

  function el(id) { return document.getElementById(id); }
  function esc(s) {
    return String(s == null ? "" : s)
      .replace(/&/g, "&amp;").replace(/</g, "&lt;").replace(/>/g, "&gt;")
      .replace(/"/g, "&quot;");
  }
  function isHttps(u) { return typeof u === "string" && /^https:\/\//i.test(u.trim()); }
  function cap(s, n) { return String(s == null ? "" : s).trim().slice(0, n); }
  function newId() { return "slot-" + Math.random().toString(36).slice(2, 8); }

  function nowIso() { return new Date().toISOString(); }

  function toLocalInput(iso) {
    if (!iso) return "";
    if (/^\d{4}-\d{2}-\d{2}$/.test(iso)) return iso + "T00:00";
    var ms = Date.parse(iso);
    if (!Number.isFinite(ms)) return "";
    var d = new Date(ms);
    function pad(n) { return String(n).padStart(2, "0"); }
    return d.getFullYear() + "-" + pad(d.getMonth() + 1) + "-" + pad(d.getDate()) +
      "T" + pad(d.getHours()) + ":" + pad(d.getMinutes());
  }

  function fromLocalInput(v) {
    if (!v) return "";
    var d = new Date(v);
    return Number.isFinite(d.getTime()) ? d.toISOString() : v;
  }

  function formatPosted(iso) {
    if (!iso) return "Not on the app yet";
    var ms = Date.parse(iso);
    if (!Number.isFinite(ms)) return iso;
    return new Date(ms).toLocaleString(undefined, { dateStyle: "medium", timeStyle: "short" });
  }

  function setStatus(msg, cls) {
    var s = el("daStatus");
    if (!s) return;
    s.textContent = msg;
    s.className = "da-status" + (cls ? " " + cls : "");
  }

  function currentApp() {
    var sel = el("daApp");
    if (sel && APPS[sel.value]) {
      appId = sel.value;
      app = APPS[appId];
    }
    return app;
  }

  function injectPicker() {
    var section = el("dealerAds");
    if (!section || el("daApp")) return;
    var box = document.createElement("div");
    box.className = "da-app-picker";
    box.innerHTML =
      '<label class="da-field" style="margin-bottom:12px">' +
        "App this ad goes on" +
        '<span class="da-hint">HHH and CVC are separate files. Switching reloads that app\'s live ads.</span>' +
        '<select id="daApp">' +
          '<option value="hhh">Handy Horology Helper</option>' +
          '<option value="cvc">Curator\'s Vault: Classics</option>' +
        "</select>" +
      "</label>";
    var explainer = section.querySelector(".da-explainer");
    section.insertBefore(box, explainer || section.firstChild);
    el("daApp").value = appId;
    el("daApp").onchange = onAppChange;
  }

  function updateExplainer() {
    var p = document.querySelector("#dealerAds .da-explainer");
    if (!p) return;
    p.innerHTML =
      "Edits the <strong>one remote file</strong> " + esc(currentApp().label) + " reads at " +
      "<code>" + esc(currentApp().publicUrl) + "</code>. " +
      "This is a <strong>static, no-write-API editor</strong>: load, edit, then " +
      "<strong>Copy JSON</strong> / <strong>Download</strong> and commit " +
      "<code>" + esc(currentApp().commitPath) + "</code> to the site repo to publish. " +
      "Each slot shows the date and time it was put on the app. Remove a slot here, then publish, to take it off. " +
      "Contact: <strong>support@josspatech.com</strong>.";
    var commit = document.querySelector("#dealerAds .da-commit");
    if (commit) {
      commit.innerHTML =
        "<strong>To publish:</strong> replace <code>" + esc(currentApp().commitPath) + "</code> in the " +
        "<code>josspatech.github.io</code> repo with this JSON and commit + push to <code>main</code>. " +
        "GitHub Pages serves it within ~1 minute. The app re-fetches at most every 6 hours.";
    }
  }

  function onAppChange() {
    if (dirty && !window.confirm("Switch app? Unsaved edits on this page will be dropped.")) {
      el("daApp").value = appId;
      return;
    }
    currentApp();
    dirty = false;
    updateExplainer();
    loadLive();
  }

  async function loadLive() {
    currentApp();
    updateExplainer();
    setStatus("Loading " + app.label + " dealer-ads.json…");
    try {
      var r = await fetch(app.liveUrl + "?t=" + Date.now(), { cache: "no-store" });
      if (!r.ok) throw new Error("HTTP " + r.status);
      var j = await r.json();
      adopt(j);
      dirty = false;
      setStatus("Loaded " + app.label + " (" + state.slots.length + " slot(s)). Edit, then Copy / Download.", "ok");
    } catch (e) {
      adopt(null);
      dirty = false;
      setStatus("Couldn't load live JSON (" + (e.message || e) + "). Starting from a blank template.", "err");
    }
    renderAll();
  }

  function adopt(raw) {
    raw = raw && typeof raw === "object" ? raw : {};
    state.enabled = raw.enabled === true;
    state.comingSoon = raw.comingSoon === true;
    state.hideForPro = raw.hideForPro === true;
    state.headline = typeof raw.headline === "string" ? raw.headline : "";
    state.note = typeof raw.note === "string" ? raw.note : "";
    state.updatedAt = typeof raw.updatedAt === "string" ? raw.updatedAt : "";
    var slotsIn = Array.isArray(raw.slots) ? raw.slots : [];
    state.slots = slotsIn.map(function (s) {
      s = s && typeof s === "object" ? s : {};
      return {
        _uid: newId(),
        id: typeof s.id === "string" ? s.id : "",
        businessName: typeof s.businessName === "string" ? s.businessName : "",
        tagline: typeof s.tagline === "string" ? s.tagline : "",
        tradeFocus: typeof s.tradeFocus === "string" ? s.tradeFocus : "",
        cityRegion: typeof s.cityRegion === "string" ? s.cityRegion : "",
        url: typeof s.url === "string" ? s.url : "",
        contactEmail: typeof s.contactEmail === "string" ? s.contactEmail : "",
        contactPhone: typeof s.contactPhone === "string" ? s.contactPhone : "",
        sponsored: s.sponsored === true,
        postedAt: typeof s.postedAt === "string" ? s.postedAt : "",
        startsAt: typeof s.startsAt === "string" ? s.startsAt : "",
        expiresAt: typeof s.expiresAt === "string" ? s.expiresAt : "",
      };
    });
  }

  function syncTopFromDom() {
    state.enabled = el("daEnabled").checked;
    state.comingSoon = el("daComingSoon").checked;
    state.hideForPro = el("daHideForPro").checked;
    state.headline = el("daHeadline").value;
    state.note = el("daNote").value;
    var updatedEl = el("daUpdatedAt");
    if (updatedEl) {
      state.updatedAt = updatedEl.type === "datetime-local"
        ? fromLocalInput(updatedEl.value)
        : updatedEl.value;
    }
  }

  function syncSlotsFromDom() {
    state.slots.forEach(function (slot) {
      var root = document.querySelector('[data-uid="' + slot._uid + '"]');
      if (!root) return;
      slot.businessName = root.querySelector('[data-f="businessName"]').value;
      slot.tagline = root.querySelector('[data-f="tagline"]').value;
      slot.tradeFocus = root.querySelector('[data-f="tradeFocus"]').value;
      slot.cityRegion = root.querySelector('[data-f="cityRegion"]').value;
      slot.url = root.querySelector('[data-f="url"]').value;
      slot.contactEmail = root.querySelector('[data-f="contactEmail"]').value;
      slot.contactPhone = root.querySelector('[data-f="contactPhone"]').value;
      slot.id = root.querySelector('[data-f="id"]').value;
      slot.sponsored = root.querySelector('[data-f="sponsored"]').checked;
      var posted = root.querySelector('[data-f="postedAt"]');
      if (posted) slot.postedAt = fromLocalInput(posted.value);
    });
  }

  window.daOnChange = function () {
    dirty = true;
    syncTopFromDom();
    syncSlotsFromDom();
    renderDerived();
  };

  function buildPayload(forDownload) {
    var stamp = nowIso();
    var slots = state.slots
      .filter(function (s) { return s.businessName && s.businessName.trim(); })
      .slice(0, 20)
      .map(function (s, i) {
        var postedAt = s.postedAt && s.postedAt.trim() ? s.postedAt.trim() : (forDownload ? stamp : "");
        var out = {
          id: s.id && s.id.trim() ? s.id.trim() : "slot_" + i,
          businessName: cap(s.businessName, CAPS.businessName),
        };
        if (s.tagline && s.tagline.trim()) out.tagline = cap(s.tagline, CAPS.tagline);
        if (s.tradeFocus) out.tradeFocus = s.tradeFocus;
        if (s.cityRegion && s.cityRegion.trim()) out.cityRegion = cap(s.cityRegion, CAPS.cityRegion);
        if (isHttps(s.url)) out.url = s.url.trim();
        if (s.contactEmail && s.contactEmail.trim()) out.contactEmail = cap(s.contactEmail, CAPS.contactEmail);
        if (s.contactPhone && s.contactPhone.trim()) out.contactPhone = cap(s.contactPhone, CAPS.contactPhone);
        if (s.sponsored) out.sponsored = true;
        if (postedAt) out.postedAt = postedAt;
        if (s.startsAt && s.startsAt.trim()) out.startsAt = s.startsAt.trim();
        if (s.expiresAt && s.expiresAt.trim()) out.expiresAt = s.expiresAt.trim();
        return out;
      });
    var payload = { enabled: !!state.enabled };
    if (state.comingSoon) payload.comingSoon = true;
    if (state.hideForPro) payload.hideForPro = true;
    if (state.headline && state.headline.trim()) payload.headline = cap(state.headline, CAPS.headline);
    if (state.note && state.note.trim()) payload.note = cap(state.note, CAPS.note);
    payload.updatedAt = forDownload ? stamp : (state.updatedAt || stamp);
    payload.slots = slots;
    return payload;
  }

  function validate() {
    var errs = [];
    var warns = [];
    if (state.headline && state.headline.length > CAPS.headline) warns.push("Headline over " + CAPS.headline + " chars — will be truncated.");
    if (state.note && state.note.length > CAPS.note) warns.push("Note over " + CAPS.note + " chars — will be truncated.");
    var kept = 0;
    state.slots.forEach(function (s, i) {
      var n = i + 1;
      if (!s.businessName || !s.businessName.trim()) {
        errs.push("Slot " + n + ": missing Business name — this slot will be DROPPED by the app.");
        return;
      }
      kept++;
      if (s.url && s.url.trim() && !isHttps(s.url)) warns.push("Slot " + n + " (" + s.businessName.trim() + "): URL is not https:// — it will be ignored.");
      if (s.businessName.length > CAPS.businessName) warns.push("Slot " + n + ": Business name over " + CAPS.businessName + " chars — truncated.");
    });
    if (kept > 20) warns.push("More than 20 valid slots — only the first 20 are rendered by the app.");
    if (state.enabled && kept === 0) warns.push('Enabled but no valid slots — the app shows the honest "coming soon" screen (no fake inventory).');
    return { errs: errs, warns: warns, kept: kept };
  }

  function renderValidation() {
    var v = validate();
    var box = el("daValidation");
    if (!box) return v;
    if (!v.errs.length && !v.warns.length) {
      box.style.display = "block";
      box.className = "da-validation ok";
      box.innerHTML = "Valid — " + v.kept + " slot(s) will render on " + esc(currentApp().label) + ". Ready to Copy / Download.";
      return v;
    }
    box.style.display = "block";
    box.className = "da-validation" + (v.errs.length ? "" : " ok");
    var html = "";
    if (v.errs.length) html += "<strong>Issues:</strong><ul>" + v.errs.map(function (e) { return "<li>" + esc(e) + "</li>"; }).join("") + "</ul>";
    if (v.warns.length) html += "<strong>Heads up:</strong><ul>" + v.warns.map(function (w) { return "<li>" + esc(w) + "</li>"; }).join("") + "</ul>";
    box.innerHTML = html;
    return v;
  }

  function slotRow(slot, i) {
    var opts = currentApp().trade.map(function (t) {
      var label = t === "" ? "— (unspecified)" : t;
      return '<option value="' + t + '"' + (slot.tradeFocus === t ? " selected" : "") + ">" + label + "</option>";
    }).join("");
    return "" +
      '<div class="da-slot" data-uid="' + slot._uid + '">' +
        '<div class="da-slot-head">' +
          "<strong>Slot " + (i + 1) + "</strong>" +
          "<span>" +
            '<button type="button" class="da-btn ghost tiny" onclick="daMoveSlot(\'' + slot._uid + '\',-1)" title="Move up">↑</button> ' +
            '<button type="button" class="da-btn ghost tiny" onclick="daMoveSlot(\'' + slot._uid + '\',1)" title="Move down">↓</button> ' +
            '<button type="button" class="da-btn danger" onclick="daRemoveSlot(\'' + slot._uid + '\')">Remove</button>' +
          "</span>" +
        "</div>" +
        '<div class="da-posted">On the app: <strong>' + esc(formatPosted(slot.postedAt)) + "</strong></div>" +
        '<label class="da-field">Posted date and time' +
          '<span class="da-hint">When this ad was put on the app. Blank until you Copy / Download. Do not clear an existing time unless you mean to.</span>' +
          '<input type="datetime-local" data-f="postedAt" value="' + esc(toLocalInput(slot.postedAt)) + '" oninput="daOnChange()">' +
        "</label>" +
        '<label class="da-field">Business name <span class="da-hint">Required. ≤80 chars. Slots without it are dropped.</span>' +
          '<input type="text" data-f="businessName" maxlength="80" value="' + esc(slot.businessName) + '" oninput="daOnChange()">' +
        "</label>" +
        '<label class="da-field">Tagline <span class="da-hint">≤120 chars.</span>' +
          '<input type="text" data-f="tagline" maxlength="120" value="' + esc(slot.tagline) + '" oninput="daOnChange()">' +
        "</label>" +
        '<div class="da-slot-2col">' +
          '<label class="da-field">Trade focus' +
            '<select data-f="tradeFocus" onchange="daOnChange()">' + opts + "</select>" +
          "</label>" +
          '<label class="da-field">City / region <span class="da-hint">≤60 chars.</span>' +
            '<input type="text" data-f="cityRegion" maxlength="60" value="' + esc(slot.cityRegion) + '" oninput="daOnChange()">' +
          "</label>" +
        "</div>" +
        '<label class="da-field">Website URL <span class="da-hint">Must start with https:// or it is ignored.</span>' +
          '<input type="url" data-f="url" value="' + esc(slot.url) + '" placeholder="https://" oninput="daOnChange()">' +
        "</label>" +
        '<div class="da-slot-2col">' +
          '<label class="da-field">Contact email' +
            '<input type="email" data-f="contactEmail" maxlength="120" value="' + esc(slot.contactEmail) + '" oninput="daOnChange()">' +
          "</label>" +
          '<label class="da-field">Contact phone <span class="da-hint">Optional. ≤40 chars.</span>' +
            '<input type="text" data-f="contactPhone" maxlength="40" value="' + esc(slot.contactPhone) + '" oninput="daOnChange()">' +
          "</label>" +
        "</div>" +
        '<div class="da-slot-2col">' +
          '<label class="da-field">Slot id <span class="da-hint">Stable unique id (optional; auto if blank).</span>' +
            '<input type="text" data-f="id" value="' + esc(slot.id) + '" placeholder="' + esc("slot_" + i) + '" oninput="daOnChange()">' +
          "</label>" +
          '<label class="da-field" style="display:flex;align-items:center;gap:8px;margin-top:22px;">' +
            '<input type="checkbox" data-f="sponsored" style="width:auto;margin:0;"' + (slot.sponsored ? " checked" : "") + ' onchange="daOnChange()"> Sponsored (shows "Ad" label)' +
          "</label>" +
        "</div>" +
      "</div>";
  }

  function renderSlots() {
    var host = el("daSlots");
    if (!host) return;
    host.innerHTML = state.slots.map(slotRow).join("");
    var cnt = el("daSlotCount");
    if (cnt) cnt.textContent = "· " + state.slots.length + " total";
  }

  function renderPreview() {
    var host = el("daPreview");
    if (!host) return;
    var payload = buildPayload(false);
    var parts = [];
    if (!payload.enabled) {
      parts.push('<div class="da-empty-preview">Unit <strong>disabled</strong> — nothing renders.</div>');
    } else if (!payload.slots.length) {
      parts.push('<div class="da-empty-preview">Enabled but no valid slots — app shows the honest "Coming soon" screen.</div>');
    } else {
      if (payload.headline) parts.push('<div style="font-weight:700;color:var(--primary);font-size:14px;">' + esc(payload.headline) + "</div>");
      payload.slots.forEach(function (s) {
        var contact = s.url ? s.url : (s.contactEmail ? "mailto:" + s.contactEmail : (s.contactPhone ? "tel:" + s.contactPhone : ""));
        var meta = [s.tradeFocus, s.cityRegion].filter(Boolean).join(" · ");
        parts.push("" +
          '<div class="da-card">' +
            '<div class="da-card-top">' +
              '<span class="da-card-name">' + esc(s.businessName) + "</span>" +
              (s.sponsored ? '<span class="da-badge">Ad</span>' : "") +
            "</div>" +
            (s.tagline ? '<div class="da-card-line">' + esc(s.tagline) + "</div>" : "") +
            (meta ? '<div class="da-card-line">' + esc(meta) + "</div>" : "") +
            '<div class="da-card-line">On the app: ' + esc(formatPosted(s.postedAt)) + "</div>" +
            (contact ? '<div class="da-card-cta">' + esc(contact) + "</div>" : "") +
          "</div>");
      });
      if (payload.note) parts.push('<div class="da-preview-note">' + esc(payload.note) + "</div>");
    }
    host.innerHTML = '<div class="da-preview-wrap">' + parts.join("") + "</div>";
  }

  function renderJson() {
    var out = el("daJsonOut");
    if (out) out.textContent = JSON.stringify(buildPayload(false), null, 2);
  }

  function renderDerived() {
    renderValidation();
    renderPreview();
    renderJson();
  }

  function renderTop() {
    el("daEnabled").checked = state.enabled;
    el("daComingSoon").checked = state.comingSoon;
    el("daHideForPro").checked = state.hideForPro;
    el("daHeadline").value = state.headline || "";
    el("daNote").value = state.note || "";
    var updated = el("daUpdatedAt");
    if (updated) {
      if (updated.type !== "datetime-local") updated.type = "datetime-local";
      updated.value = toLocalInput(state.updatedAt);
    }
  }

  function renderAll() {
    if (!el("daSlots")) return;
    renderTop();
    renderSlots();
    renderDerived();
  }

  window.daReload = function () {
    if (dirty && !window.confirm("Reload live JSON? Unsaved edits will be dropped.")) return;
    dirty = false;
    loadLive();
  };

  window.daAddSlot = function () {
    syncTopFromDom(); syncSlotsFromDom();
    dirty = true;
    state.slots.push({
      _uid: newId(), id: "", businessName: "", tagline: "", tradeFocus: "",
      cityRegion: "", url: "", contactEmail: "support@josspatech.com",
      contactPhone: "", sponsored: true, postedAt: "", startsAt: "", expiresAt: "",
    });
    renderSlots();
    renderDerived();
  };

  window.daRemoveSlot = function (uid) {
    syncTopFromDom(); syncSlotsFromDom();
    dirty = true;
    state.slots = state.slots.filter(function (s) { return s._uid !== uid; });
    renderSlots();
    renderDerived();
  };

  window.daMoveSlot = function (uid, dir) {
    syncTopFromDom(); syncSlotsFromDom();
    dirty = true;
    var i = state.slots.findIndex(function (s) { return s._uid === uid; });
    if (i < 0) return;
    var j = i + dir;
    if (j < 0 || j >= state.slots.length) return;
    var tmp = state.slots[i];
    state.slots[i] = state.slots[j];
    state.slots[j] = tmp;
    renderSlots();
    renderDerived();
  };

  function publishedStatus(jsonLen) {
    currentApp();
    setStatus(
      "Ready — " + jsonLen + " chars for " + app.label +
        ". Paste into " + app.commitPath + " and commit to put it on the app. postedAt stamped on new slots.",
      "ok"
    );
    dirty = false;
  }

  window.daCopyJson = function () {
    syncTopFromDom(); syncSlotsFromDom();
    var json = JSON.stringify(buildPayload(true), null, 2);
    adopt(JSON.parse(json));
    renderAll();
    var done = function () { publishedStatus(json.length); };
    var fail = function () {
      var ta = document.createElement("textarea");
      ta.value = json; document.body.appendChild(ta); ta.select();
      try { document.execCommand("copy"); done(); }
      catch (e) { setStatus("Copy failed — select the Output JSON manually.", "err"); }
      document.body.removeChild(ta);
    };
    if (navigator.clipboard && navigator.clipboard.writeText) {
      navigator.clipboard.writeText(json).then(done).catch(fail);
    } else { fail(); }
  };

  window.daDownloadJson = function () {
    syncTopFromDom(); syncSlotsFromDom();
    var json = JSON.stringify(buildPayload(true), null, 2);
    adopt(JSON.parse(json));
    renderAll();
    var blob = new Blob([json], { type: "application/json" });
    var url = URL.createObjectURL(blob);
    var a = document.createElement("a");
    a.href = url;
    a.download = "dealer-ads.json";
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
    setTimeout(function () { URL.revokeObjectURL(url); }, 1000);
    publishedStatus(json.length);
  };

  window.addEventListener("DOMContentLoaded", function () {
    injectPicker();
    currentApp();
    updateExplainer();
    loadLive();
  });
})();
