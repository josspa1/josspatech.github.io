/**
 * Apply research-backed family lineup to company hub.
 * Sources: Apple product tiles, Stripe bento (visual-first), Linear product proof.
 * Cohesive with existing product-page brand atmospheres + device frames.
 */
const fs = require('fs');
const path = require('path');
const file = path.join(__dirname, '..', 'index.html');
let s = fs.readFileSync(file, 'utf8');

const start = s.indexOf('/* ══ Editorial Studio Catalog');
const end = s.indexOf('/* ══ Top-5 craft system');
if (start < 0 || end < 0) {
  console.error('CSS markers not found', start, end);
  process.exit(1);
}

const NEW_CSS = `/* ══ Family lineup hub — winning elements applied ═══════════════════════════
   Apple: full-bleed product tiles, product visual owns the cell, short copy.
   Stripe bento: show all products at once, visuals over text walls.
   Linear: real product UI as proof. Cohesive with volume brand atmospheres. */
#page-company.catalog-hub .hub-mark{display:block;}
#page-company.catalog-hub .hub-hero .hero-brand{font-size:clamp(52px,9vw,96px);}
#page-company.catalog-hub .hub-hero .hero-actions .btn-primary{
  box-shadow:0 10px 32px rgba(240,192,64,0.28);
}
#page-company.catalog-hub .section.content{
  background:#070f18;
  padding:96px 48px 110px;
}
#page-company.catalog-hub .section.content::before{display:none;}
#page-company.catalog-hub .section-inner{max-width:1120px;}
#page-company.catalog-hub .section-eyebrow{
  font-family:var(--mono,'IBM Plex Mono',monospace);
  color:rgba(240,192,64,0.8);
  letter-spacing:0.22em;
}
#page-company.catalog-hub .section-title{color:#fff;}
#page-company.catalog-hub .section-title em{color:var(--gold);}
#page-company.catalog-hub .section-sub{color:rgba(255,255,255,0.52);}
#page-company .section-lead{display:flex;align-items:flex-start;gap:28px;}
#page-company .section-num{
  font-family:var(--mono,'IBM Plex Mono',monospace);
  font-size:12px;font-weight:600;letter-spacing:0.22em;color:var(--gold);
  flex-shrink:0;border-top:1px solid var(--gold);width:52px;text-align:center;
  line-height:1;padding-top:14px;
}
#page-company .section-lead .section-title{
  font-size:clamp(40px,5.5vw,56px);letter-spacing:-1.6px;
}
#page-company .hub-grid{
  display:grid;
  grid-template-columns:repeat(12,minmax(0,1fr));
  gap:16px;
  margin-top:52px;
}
/* Size = hierarchy (Stripe bento / Apple lineup) */
#page-company .hub-card[data-app="pbj"]{grid-column:span 7;min-height:340px;}
#page-company .hub-card[data-app="hhh"]{grid-column:span 5;min-height:340px;}
#page-company .hub-card[data-app="pal"]{grid-column:span 5;min-height:300px;}
#page-company .hub-card[data-app="cvc"]{grid-column:span 7;min-height:300px;}
#page-company .hub-card{
  display:grid;
  grid-template-columns:1fr auto;
  gap:20px;
  align-items:end;
  border-radius:24px;
  padding:36px 32px 32px;
  border:1px solid rgba(255,255,255,0.1);
  box-shadow:0 24px 56px rgba(0,0,0,0.35);
  position:relative;overflow:hidden;cursor:pointer;text-align:left;
  background:
    radial-gradient(ellipse 60% 80% at 85% 15%, var(--hub-glow), transparent 55%),
    linear-gradient(155deg, var(--hub-dk) 0%, var(--hub-md) 100%);
  transition:transform .28s var(--ease), border-color .28s, box-shadow .28s;
}
#page-company .hub-card[data-app="pbj"]{
  --hub-dk:#0C3358;--hub-md:#1A4F7A;--hub-glow:rgba(240,192,64,0.22);--hub-accent:#F0C040;
}
#page-company .hub-card[data-app="hhh"]{
  --hub-dk:#3D1522;--hub-md:#5B2333;--hub-glow:rgba(200,170,110,0.24);--hub-accent:#C8AA6E;
}
#page-company .hub-card[data-app="pal"]{
  --hub-dk:#1A2E22;--hub-md:#2F4A3A;--hub-glow:rgba(232,184,74,0.22);--hub-accent:#E8B84A;
}
#page-company .hub-card[data-app="cvc"]{
  --hub-dk:#0F2E25;--hub-md:#1B4D3E;--hub-glow:rgba(212,168,83,0.22);--hub-accent:#D4A853;
}
#page-company .hub-card:hover{
  transform:translateY(-5px);
  border-color:rgba(255,255,255,0.22);
  box-shadow:0 32px 72px rgba(0,0,0,0.45);
}
#page-company .hub-card::before{
  content:'';position:absolute;left:0;top:0;bottom:0;width:3px;
  background:var(--hub-accent);opacity:1;
}
#page-company .hub-card::after{display:none;}
#page-company .hub-badge{display:none;}
#page-company .hub-meta{display:none;}
#page-company .hub-index{
  position:static;display:block;margin-bottom:12px;
  font-family:var(--mono,'IBM Plex Mono',monospace);
  font-size:11px;letter-spacing:0.22em;color:var(--hub-accent);
}
#page-company .hub-name{
  font-size:clamp(26px,2.8vw,36px);margin-bottom:10px;line-height:1.1;
}
#page-company .hub-name em{color:var(--hub-accent);}
#page-company .hub-tagline{
  font-size:15px;line-height:1.55;color:rgba(255,255,255,0.58);
  margin-bottom:22px;max-width:32ch;
}
#page-company .hub-cta{
  font-family:'Manrope',sans-serif !important;
  display:inline-flex;align-items:center;gap:8px;
  background:var(--hub-accent);color:var(--hub-dk);
  border-radius:10px;padding:12px 20px;
  font-size:14px;font-weight:700;letter-spacing:0.01em;text-transform:none;
  box-shadow:0 8px 24px rgba(0,0,0,0.25);width:fit-content;
}
#page-company .hub-card:hover .hub-cta{
  background:#fff;color:var(--hub-dk);transform:translateX(2px);
}
#page-company .hub-card-body{position:relative;z-index:1;min-width:0;}
#page-company .hub-card-shot{
  position:relative;z-index:1;width:148px;flex-shrink:0;margin:0;
  padding:8px 8px 12px;border-radius:22px;align-self:end;
  background:linear-gradient(160deg,#1a1a1c,#0d0d0f);
  border:1px solid rgba(255,255,255,0.14);
  box-shadow:0 18px 40px rgba(0,0,0,0.45);
}
#page-company .hub-card-shot::before{
  content:'';position:absolute;top:3px;left:50%;transform:translateX(-50%);
  width:42px;height:4px;border-radius:999px;background:rgba(0,0,0,0.55);
}
#page-company .hub-card-shot img{
  display:block;width:100%;height:auto;border-radius:14px;
}
#page-company .hub-card[data-app="pbj"] .hub-card-shot,
#page-company .hub-card[data-app="cvc"] .hub-card-shot{width:168px;}
#page-company .quote-bar{
  background:#050c14;padding:110px 48px;text-align:center;
}
#page-company .quote-bar blockquote{
  margin:0 auto;font-size:clamp(30px,4vw,48px);color:#fff;
}
#page-company .quote-bar::before{
  content:'';position:absolute;left:50%;top:44px;transform:translateX(-50%);
  width:40px;height:1px;background:rgba(240,192,64,0.45);
}
#page-company .principles{background:#fff;}
#page-company .refuse-line{
  margin-top:48px;padding-top:28px;border-top:1px solid rgba(26,79,122,0.12);
  font-family:var(--mono,'IBM Plex Mono',monospace);
  font-size:11px;font-weight:600;letter-spacing:0.16em;text-transform:uppercase;color:#6a8499;
}
@media (max-width:900px){
  #page-company .hub-grid{grid-template-columns:1fr;}
  #page-company .hub-card[data-app="pbj"],
  #page-company .hub-card[data-app="hhh"],
  #page-company .hub-card[data-app="pal"],
  #page-company .hub-card[data-app="cvc"]{grid-column:auto;min-height:0;}
  #page-company .hub-card{grid-template-columns:1fr auto;padding:28px 24px;}
  #page-company .hub-card-shot{width:120px !important;}
  #page-company .section-lead{flex-direction:column;gap:16px;}
  #page-company.catalog-hub .section.content{padding:72px 24px 88px;}
  #page-company .quote-bar{padding:88px 24px;}
}

`;

s = s.slice(0, start) + NEW_CSS + s.slice(end);

// Hero CTA copy — clear primary action (Linear/Apple)
s = s.replace(
  />Open the catalog</,
  '>See Our Apps<'
);

// Rebuild product cards HTML with screenshots (show, don't tell)
const productsOldStart = s.indexOf('<div class="hub-grid">');
const productsOldEnd = s.indexOf('</div>\n  </div>\n</section>\n\n<!-- ══ QUOTE BAR');
if (productsOldStart < 0 || productsOldEnd < 0) {
  console.error('products markers', productsOldStart, productsOldEnd);
  process.exit(1);
}

const PRODUCTS = `<div class="hub-grid">

      <div role="button" tabindex="0" data-app="pbj" onclick="showPage('pbj');" onkeydown="if(event.key==='Enter'||event.key===' '){event.preventDefault();showPage('pbj');}" class="hub-card hub-card-featured rv d1">
        <div class="hub-card-body">
          <span class="hub-index" aria-hidden="true">Vol. 01</span>
          <div class="hub-name">Pocket<em>BudJet</em>™</div>
          <p class="hub-tagline">Private budgeting on your device — import, plan, and coach without ads or data games.</p>
          <div class="hub-cta">Learn more <span>→</span></div>
        </div>
        <figure class="hub-card-shot" aria-hidden="true">
          <img src="videos/pocketbudjet/partner-showcase/screens/home-concierge.jpg" alt="" width="168" height="364" loading="lazy">
        </figure>
      </div>

      <div role="button" tabindex="0" data-app="hhh" onclick="showPage('hhh');" onkeydown="if(event.key==='Enter'||event.key===' '){event.preventDefault();showPage('hhh');}" class="hub-card hub-card-featured rv d2">
        <div class="hub-card-body">
          <span class="hub-index" aria-hidden="true">Vol. 02</span>
          <div class="hub-name">Handy Horology<br><em>Helper</em>™</div>
          <p class="hub-tagline">Identify timepieces, run your museum, and open a live companion on home Wi‑Fi.</p>
          <div class="hub-cta">Learn more <span>→</span></div>
        </div>
        <figure class="hub-card-shot" aria-hidden="true">
          <img src="assets/screenshots/hhh/intro/02-my-museum.png" alt="" width="148" height="322" loading="lazy">
        </figure>
      </div>

      <div role="button" tabindex="0" data-app="pal" onclick="showPage('pal');" onkeydown="if(event.key==='Enter'||event.key===' '){event.preventDefault();showPage('pal');}" class="hub-card rv d3">
        <div class="hub-card-body">
          <span class="hub-index" aria-hidden="true">Vol. 03</span>
          <div class="hub-name">Pocket Allowance<br><em>Ledger</em>™</div>
          <p class="hub-tagline">A home token economy — parent-led rewards, not kid banking.</p>
          <div class="hub-cta">Learn more <span>→</span></div>
        </div>
        <figure class="hub-card-shot" aria-hidden="true">
          <img src="assets/brand/pal-coin.svg" alt="" width="120" height="120" loading="lazy" style="padding:24px;background:rgba(232,184,74,0.08);border-radius:14px;">
        </figure>
      </div>

      <div role="button" tabindex="0" data-app="cvc" onclick="showPage('cvc');" onkeydown="if(event.key==='Enter'||event.key===' '){event.preventDefault();showPage('cvc');}" class="hub-card rv d4">
        <div class="hub-card-body">
          <span class="hub-index" aria-hidden="true">Vol. 04</span>
          <div class="hub-name">Curator's Vault:<br><em>Classics</em>™</div>
          <p class="hub-tagline">Coins, cards, stamps, paper, lighters — catalog and value in one private vault.</p>
          <div class="hub-cta">Learn more <span>→</span></div>
        </div>
        <figure class="hub-card-shot" aria-hidden="true">
          <img src="assets/screenshots/cvc/02-collection.png" alt="" width="168" height="298" loading="lazy">
        </figure>
      </div>

    `;

s = s.slice(0, productsOldStart) + PRODUCTS + s.slice(productsOldEnd);

// Section copy — scan-first, not catalog lecture
s = s.replace(
  /Pick a product to open its own area — features, guides, and downloads live there, not on this hub\./,
  'Four private tools. Tap any one to open its world.'
);

// Mission ghost should stay secondary but visible as ghost button (not naked text)
s = s.replace(
  /<a href="#principles" class="btn-ghost">Mission<\/a>/,
  '<a href="#principles" class="btn-ghost">Our Mission</a>'
);

fs.writeFileSync(file, s);
console.log('OK: family lineup hub applied');
