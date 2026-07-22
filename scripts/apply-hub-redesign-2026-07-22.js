#!/usr/bin/env node
/**
 * Company hub redesign + product-page theming.
 * Hub = JosspaTech navy/gold. App pages = product palettes (Core→Product).
 */
'use strict';

const fs = require('fs');
const path = require('path');

const ROOT = path.resolve(__dirname, '..');
const FILE = path.join(ROOT, 'index.html');
let html = fs.readFileSync(FILE, 'utf8');

const THEME_CSS = `
/* ══ Multi-brand tokens (Core → Product) ═════════════════
   Hub uses company navy/gold. App pages override --brand-* .
═════════════════════════════════════════════════════════ */
:root {
  --brand: var(--navy);
  --brand-dk: var(--navy-dk);
  --brand-md: var(--navy-md);
  --brand-accent: var(--gold);
  --brand-accent-dk: var(--gold-dk);
  --brand-soft: rgba(240,192,64,0.12);
  --brand-ink: #fff;
  --brand-muted: rgba(255,255,255,0.55);
  --surface-deep: #071828;
  --mesh-a: rgba(46,111,163,0.45);
  --mesh-b: rgba(240,192,64,0.18);
}
#page-hhh {
  --brand: #5B2333;
  --brand-dk: #3D1522;
  --brand-md: #7A3A4F;
  --brand-accent: #C8AA6E;
  --brand-accent-dk: #A8884A;
  --brand-soft: rgba(200,170,110,0.12);
  --surface-deep: #241018;
  --mesh-a: rgba(122,58,79,0.55);
  --mesh-b: rgba(200,170,110,0.22);
}
#page-cvc {
  --brand: #1B4D3E;
  --brand-dk: #0F2E25;
  --brand-md: #2A6B57;
  --brand-accent: #D4A853;
  --brand-accent-dk: #B8893A;
  --brand-soft: rgba(212,168,83,0.12);
  --surface-deep: #0A1F18;
  --mesh-a: rgba(42,107,87,0.5);
  --mesh-b: rgba(212,168,83,0.2);
}
#page-pal {
  --brand: #2F4A3A;
  --brand-dk: #1A2E22;
  --brand-md: #4A6B55;
  --brand-accent: #E8B84A;
  --brand-accent-dk: #C99A2E;
  --brand-soft: rgba(232,184,74,0.12);
  --surface-deep: #122018;
  --mesh-a: rgba(74,107,85,0.5);
  --mesh-b: rgba(232,184,74,0.2);
}
#page-pbj {
  --brand: var(--navy);
  --brand-dk: var(--navy-dk);
  --brand-md: var(--navy-md);
  --brand-accent: var(--gold);
  --brand-accent-dk: var(--gold-dk);
  --brand-soft: rgba(240,192,64,0.12);
  --surface-deep: #071828;
}

/* Hub hero — atmospheric company composition */
.hero.hub-hero{
  position:relative;
  background:
    radial-gradient(ellipse 80% 60% at 15% 20%, var(--mesh-a), transparent 55%),
    radial-gradient(ellipse 70% 50% at 85% 75%, var(--mesh-b), transparent 50%),
    linear-gradient(165deg, var(--navy-dk) 0%, #0a2740 45%, var(--navy) 100%);
  padding:112px 48px 100px;
  overflow:hidden;
}
.hero.hub-hero::after{
  content:'';position:absolute;inset:0;pointer-events:none;opacity:0.035;
  background-image:url("data:image/svg+xml,%3Csvg viewBox='0 0 200 200' xmlns='http://www.w3.org/2000/svg'%3E%3Cfilter id='n'%3E%3CfeTurbulence type='fractalNoise' baseFrequency='0.9' numOctaves='4' stitchTiles='stitch'/%3E%3C/filter%3E%3Crect width='100%25' height='100%25' filter='url(%23n)'/%3E%3C/svg%3E");
}
.hub-hero .hero-inner{position:relative;z-index:1;max-width:820px;margin:0 auto;}
.hub-hero .hero-h1{
  font-size:clamp(40px,6.5vw,64px);
  letter-spacing:-1.5px;
  line-height:1.05;
  margin:18px 0 20px;
  animation:hubFadeUp .9s var(--ease) both;
}
.hub-hero .hero-sub{
  font-size:18px;color:rgba(255,255,255,0.62);
  max-width:520px;margin:0 auto 32px;
  animation:hubFadeUp 1s var(--ease) .08s both;
}
.hub-hero .hero-actions{animation:hubFadeUp 1.05s var(--ease) .14s both;justify-content:center;}
@keyframes hubFadeUp{from{opacity:0;transform:translateY(18px)}to{opacity:1;transform:none}}

/* Unified hub product gateways — company chrome + accent stripe */
.hub-grid{
  display:grid;grid-template-columns:1fr 1fr;gap:22px;margin-top:48px;
}
.hub-card{
  background:linear-gradient(145deg, var(--navy-dk) 0%, #123a5c 100%);
  border-radius:22px;padding:40px 36px 36px;
  display:flex;flex-direction:column;position:relative;overflow:hidden;
  border:1px solid rgba(255,255,255,0.06);
  box-shadow:0 12px 40px rgba(7,24,40,0.35);
  cursor:pointer;text-align:left;
  transition:transform .28s var(--ease), box-shadow .28s var(--ease), border-color .28s;
}
.hub-card:focus-visible{outline:2px solid var(--gold);outline-offset:4px;}
.hub-card:hover{
  transform:translateY(-6px);
  box-shadow:0 22px 56px rgba(7,24,40,0.45);
  border-color:rgba(240,192,64,0.28);
}
.hub-card::before{
  content:'';position:absolute;left:0;top:0;bottom:0;width:4px;
  background:var(--hub-accent, var(--gold));
}
.hub-card[data-app="pbj"]{--hub-accent:#F0C040;}
.hub-card[data-app="hhh"]{--hub-accent:#C8AA6E;}
.hub-card[data-app="pal"]{--hub-accent:#E8B84A;}
.hub-card[data-app="cvc"]{--hub-accent:#D4A853;}
.hub-card::after{
  content:'';position:absolute;right:-40px;top:-40px;width:160px;height:160px;
  border-radius:50%;background:radial-gradient(circle,var(--hub-accent),transparent 70%);
  opacity:0.08;pointer-events:none;transition:opacity .28s;
}
.hub-card:hover::after{opacity:0.16;}
.hub-badge{
  display:inline-flex;align-items:center;gap:7px;
  font-size:10px;font-weight:700;letter-spacing:2px;text-transform:uppercase;
  color:var(--hub-accent, var(--gold));margin-bottom:16px;
}
.hub-badge-dot{width:6px;height:6px;border-radius:50%;background:var(--hub-accent, var(--gold));}
.hub-name{
  font-family:'Playfair Display',serif;font-size:30px;font-weight:900;color:#fff;
  letter-spacing:-0.6px;line-height:1.12;margin-bottom:10px;
}
.hub-name em{font-style:normal;color:var(--hub-accent, var(--gold));}
.hub-tagline{
  font-size:15px;color:rgba(255,255,255,0.52);line-height:1.55;flex:1;margin-bottom:28px;
}
.hub-cta{
  display:inline-flex;align-items:center;gap:8px;
  font-size:14px;font-weight:700;color:var(--navy-dk);
  background:var(--gold);padding:12px 20px;border-radius:10px;width:fit-content;
  transition:transform .18s, background .18s;
}
.hub-card:hover .hub-cta{background:#f5d060;transform:translateX(2px);}
.hub-cta span{transition:transform .18s;}
.hub-card:hover .hub-cta span{transform:translateX(3px);}
.hub-meta{display:flex;flex-wrap:wrap;gap:8px;margin-top:16px;}
.hub-pill{
  font-size:11px;font-weight:600;color:rgba(255,255,255,0.45);
  border:1px solid rgba(255,255,255,0.12);border-radius:999px;padding:4px 10px;
}

/* App pages — use product brand tokens on heroes / strips */
#page-hhh .hero,
#page-cvc .hero,
#page-pal .hero{
  background:
    radial-gradient(ellipse 70% 55% at 20% 30%, var(--mesh-a), transparent 55%),
    radial-gradient(ellipse 60% 45% at 90% 80%, var(--mesh-b), transparent 50%),
    linear-gradient(160deg, var(--brand-dk) 0%, var(--brand) 100%);
}
#page-hhh .hero-bc a,
#page-cvc .hero-bc a,
#page-pal .hero-bc a{color:var(--brand-accent);}
#page-hhh .btn-primary,
#page-cvc .btn-primary,
#page-pal .btn-primary{
  background:var(--brand-accent);color:var(--brand-dk);
}
#page-hhh .pstrip,
#page-cvc .pstrip,
#page-pal .pstrip{
  background:var(--brand-dk);border-color:rgba(255,255,255,0.06);
}

@media (max-width:820px){
  .hub-grid{grid-template-columns:1fr;}
  .hero.hub-hero{padding:72px 24px 64px;}
}
`;

// Inject theme CSS after :root block's first closing — after --spring line area
if (!html.includes('Multi-brand tokens (Core → Product)')) {
  html = html.replace(
    /(--spring:cubic-bezier\(0\.34,1\.56,0\.64,1\);\s*\})/,
    `$1\n${THEME_CSS}`,
  );
}

const PRODUCTS_HTML = `
    <div class="hub-grid">

      <div role="button" tabindex="0" data-app="pbj" onclick="showPage('pbj');" onkeydown="if(event.key==='Enter'||event.key===' '){event.preventDefault();showPage('pbj');}" class="hub-card rv d1">
        <div class="hub-badge"><div class="hub-badge-dot"></div>Internal testing</div>
        <div class="hub-name">Pocket<em>BudJet</em>™</div>
        <p class="hub-tagline">Private budgeting that stays on your device — import, plan, and coach without ads or data games.</p>
        <div class="hub-cta">Open PocketBudJet <span>→</span></div>
        <div class="hub-meta">
          <span class="hub-pill">iOS</span>
          <span class="hub-pill">Android</span>
          <span class="hub-pill">15-day trial</span>
        </div>
      </div>

      <div role="button" tabindex="0" data-app="hhh" onclick="showPage('hhh');" onkeydown="if(event.key==='Enter'||event.key===' '){event.preventDefault();showPage('hhh');}" class="hub-card rv d2">
        <div class="hub-badge"><div class="hub-badge-dot"></div>Open testing · v1.0.86</div>
        <div class="hub-name">Handy Horology<br><em>Helper</em>™</div>
        <p class="hub-tagline">Identify timepieces, run your museum, repair clocks, and sync to a PC on your Wi‑Fi — built for collectors.</p>
        <div class="hub-cta">Open Handy Horology Helper <span>→</span></div>
        <div class="hub-meta">
          <span class="hub-pill">Android Open</span>
          <span class="hub-pill">iOS TestFlight</span>
        </div>
      </div>

      <div role="button" tabindex="0" data-app="pal" onclick="showPage('pal');" onkeydown="if(event.key==='Enter'||event.key===' '){event.preventDefault();showPage('pal');}" class="hub-card rv d3">
        <div class="hub-badge"><div class="hub-badge-dot"></div>Parent app · ages 6+</div>
        <div class="hub-name">Pocket Allowance<br><em>Ledger</em>™</div>
        <p class="hub-tagline">A home token economy for families — parent-led rewards, not kid banking.</p>
        <div class="hub-cta">Open Pocket Allowance Ledger <span>→</span></div>
        <div class="hub-meta">
          <span class="hub-pill">Android</span>
        </div>
      </div>

      <div role="button" tabindex="0" data-app="cvc" onclick="showPage('cvc');" onkeydown="if(event.key==='Enter'||event.key===' '){event.preventDefault();showPage('cvc');}" class="hub-card rv d4">
        <div class="hub-badge"><div class="hub-badge-dot"></div>Internal testing</div>
        <div class="hub-name">Curator's Vault:<br><em>Classics</em>™</div>
        <p class="hub-tagline">AI-assisted collecting for coins, paper money, stamps, cards, and more — your vault, your rules.</p>
        <div class="hub-cta">Open Curator's Vault <span>→</span></div>
        <div class="hub-meta">
          <span class="hub-pill">iOS</span>
          <span class="hub-pill">Android</span>
        </div>
      </div>

    </div>
`;

// Replace products-grid block (company hub only — first occurrence)
{
  const start = html.indexOf('<div class="products-grid">');
  const endMarker = '<!-- ══ QUOTE BAR ══ -->';
  const end = html.indexOf(endMarker, start);
  if (start === -1 || end === -1) throw new Error('products-grid block not found');
  const before = html.slice(0, start);
  const after = html.slice(end);
  // Keep closing wrappers: products-grid closes, then section-inner, then section
  html = before + PRODUCTS_HTML.trim() + '\n  </div>\n</section>\n\n' + after;
}

// Hub hero class + brand-forward copy (company page only)
html = html.replace(
  'Mobile Software, Built Right',
  'JosspaTech',
);
html = html.replace(
  `We make the apps<br>
      <em>we'd want to buy.</em>`,
  `Fewer apps.<br>
      <em>Better apps.</em>`,
);
html = html.replace(
  'Mobile software for the things that actually matter to you.',
  'A small studio building private, useful mobile tools — then getting out of your way.',
);

// Add hub-hero class to company hero (first .hero before page-pbj)
{
  const companyStart = html.indexOf('id="page-company"');
  const heroIdx = html.indexOf('<section class="hero"', companyStart);
  if (heroIdx !== -1 && heroIdx < html.indexOf('id="page-pbj"')) {
    html = html.slice(0, heroIdx) + '<section class="hero hub-hero"' + html.slice(heroIdx + '<section class="hero"'.length);
  }
}

// Company footer: keep Products + Company; move PBJ legal/guides off hub
{
  const marker = '<h4>PocketBudJet Legal</h4>';
  const i = html.indexOf(marker);
  if (i !== -1) {
    // Only first footer (company page)
    const colStart = html.lastIndexOf('<div class="footer-col">', i);
    const guidesStart = html.indexOf('<h4>Guides</h4>', i);
    const companyH4 = html.indexOf('<h4>Company</h4>', guidesStart);
    const companyColStart = html.lastIndexOf('<div class="footer-col">', companyH4);
    if (colStart !== -1 && companyColStart > colStart) {
      html = html.slice(0, colStart) + html.slice(companyColStart);
    }
  }
}

// HHH version + hero copy refresh
html = html.replace(
  /Open testing · v1\.0\.68 \(build 94\) &middot; Android Open &amp; iOS TestFlight/,
  'Open testing · v1.0.86 (build 112) &middot; Android Open &amp; iOS TestFlight',
);

html = html.replace(
  /AI identification, collection manager &amp; offline Demand Rolodex/,
  'Identify · Museum · Clock DIY · Web Companion',
);

html = html.replace(
  /Point your camera at any watch or clock and get an instant AI identification with brand, model, era, and estimated market value\. Manage your collection with gains tracking, Clockworks parts help, eBay Hunts, and a Demand Rolodex for flea-market want lists &mdash; even with no cell signal\. Full UI in <strong>8 languages<\/strong>\./,
  'Snap a photo to identify watches and clocks, keep a private museum with honest confidence scores, fix clocks with Clockworks-ready guidance, and open a live Web Companion on your home Wi‑Fi with a short pairing code. Full UI in <strong>8 languages</strong>.',
);

// Photo Studio → Photo Coach on HHH page
html = html.replace(
  /<h3 style="color:#fff;font-family:'Playfair Display',serif;font-size:20px;margin-bottom:8px;">Photo Studio<\/h3>\s*<p style="color:rgba\(255,255,255,0\.55\);font-size:14px;line-height:1\.7;">Build a professional photo gallery for each piece with guided shot positions\. Perfect photos for insurance claims, resale listings, or just showing off\.<\/p>/,
  `<h3 style="color:#fff;font-family:'Playfair Display',serif;font-size:20px;margin-bottom:8px;">Photo Coach</h3>
        <p style="color:rgba(255,255,255,0.55);font-size:14px;line-height:1.7;">Guided dial, caseback, and movement shots for listing-ready photos — a coach for the angles that matter, not a generic camera.</p>`,
);

// Web Companion copy — pairing code
html = html.replace(
  /Browse and manage your collection from any computer on your home network\. In the app, open <strong>Tools → Web Companion<\/strong>, start the server on your phone, then scan the QR or paste the link on your PC\. Live data from your phone — not a public website\./,
  'On the same Wi‑Fi, open Tools → Web Companion → Start. Your phone shows an address like <strong>http://10.0.0.50:8771</strong> and a large <strong>4-digit pairing code</strong>. Type that code on the PC to unlock the live dashboard — no public cloud site.',
);

// Swap Community Feed for Device Sync (honest product)
html = html.replace(
  /<h3 style="color:#fff;font-family:'Playfair Display',serif;font-size:20px;margin-bottom:8px;">Community Feed<\/h3>\s*<p style="color:rgba\(255,255,255,0\.55\);font-size:14px;line-height:1\.7;">Share wrist shots, discuss new finds, and connect with collectors who share your passion\. A community built around the love of timepieces\.<\/p>/,
  `<h3 style="color:#fff;font-family:'Playfair Display',serif;font-size:20px;margin-bottom:8px;">Device Sync</h3>
        <p style="color:rgba(255,255,255,0.55);font-size:14px;line-height:1.7;">Move pieces between your own phones or tablets on the same Wi‑Fi — a private LAN sync for your museum, not a social network.</p>`,
);

// Soften Cloud Sync claim
html = html.replace(
  /Add a watch on your phone, see it on your tablet\. Your collection stays in sync across devices, protected with biometric security\./,
  'Optional Pro cloud sync when you want it — your museum still lives on the device first. Prefer LAN Device Sync or a .hhh file backup when you want full control.',
);

// Collector's Network naming
html = html.replace(
  /Collector's Network/g,
  'Collector Network',
);

fs.writeFileSync(FILE, html);
console.log('Updated', FILE, 'bytes', fs.statSync(FILE).size);
