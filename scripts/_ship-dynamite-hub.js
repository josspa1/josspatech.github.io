/**
 * Best-in-class company hub for JosspaTech.
 * Synthesis: Stripe manifesto+bento, Apple product atmospheres,
 * Linear product proof, Codrops-level grain/motion (without WebGL bloat).
 * Fresh ad copy — not restored from git.
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

const NEW_CSS = `/* ══ Dynamite family hub ════════════════════════════════════════════════════
   Stripe: manifesto hero, all products visible, size=hierarchy, visual-first.
   Apple: each tile owns a product atmosphere + real UI.
   Craft: film grain, specular hover, phone proof, paced motion. */
#page-company.catalog-hub .hub-mark{display:block;opacity:0.92;}
#page-company.catalog-hub .hero.hub-hero{
  min-height:min(92vh,880px);
  display:flex;align-items:center;
  background:
    radial-gradient(ellipse 90% 70% at 50% -15%, rgba(240,192,64,0.16), transparent 55%),
    radial-gradient(ellipse 45% 50% at 95% 70%, rgba(93,173,226,0.12), transparent 50%),
    radial-gradient(ellipse 40% 40% at 5% 90%, rgba(240,192,64,0.06), transparent 45%),
    linear-gradient(168deg, #040b14 0%, #0a2740 42%, #0e3a5c 100%);
  position:relative;overflow:hidden;
}
#page-company.catalog-hub .hero.hub-hero::before{
  background:linear-gradient(180deg, transparent 35%, rgba(3,10,18,0.72) 100%);
}
#page-company.catalog-hub .hero.hub-hero::after{
  content:'';position:absolute;inset:0;pointer-events:none;opacity:0.06;mix-blend-mode:overlay;z-index:1;
  background-image:url("data:image/svg+xml,%3Csvg viewBox='0 0 256 256' xmlns='http://www.w3.org/2000/svg'%3E%3Cfilter id='n'%3E%3CfeTurbulence type='fractalNoise' baseFrequency='0.85' numOctaves='4' stitchTiles='stitch'/%3E%3C/filter%3E%3Crect width='100%25' height='100%25' filter='url(%23n)'/%3E%3C/svg%3E");
  background-size:160px 160px;
}
#page-company.catalog-hub .hub-hero .hero-inner{position:relative;z-index:2;}
#page-company.catalog-hub .hub-hero .hero-brand{
  font-size:clamp(60px,11vw,120px);
  margin-bottom:16px;
  letter-spacing:-0.045em;
  line-height:0.92;
}
#page-company.catalog-hub .hub-hero .hero-h1{
  font-size:clamp(30px,4.4vw,48px);
  font-weight:700;
  color:#fff;
  max-width:16ch;
  letter-spacing:-0.035em;
  line-height:1.08;
  margin-bottom:18px;
}
#page-company.catalog-hub .hub-hero .hero-sub{
  font-size:clamp(17px,1.6vw,19px);
  max-width:36rem;
  margin:0 auto 40px;
  color:rgba(255,255,255,0.64);
  line-height:1.7;
}
#page-company.catalog-hub .hub-hero .hero-actions .btn-primary{
  box-shadow:0 14px 44px rgba(240,192,64,0.36);
  padding:16px 28px;
  font-size:15px;
}
#page-company.catalog-hub .hub-hero .hero-actions .btn-ghost{
  background:rgba(255,255,255,0.05);
  border-color:rgba(255,255,255,0.2);
  color:rgba(255,255,255,0.88);
  backdrop-filter:blur(8px);
}
#page-company.catalog-hub .hub-hero .hero-actions .btn-ghost:hover{
  border-color:rgba(240,192,64,0.5);
  color:#fff;
  background:rgba(240,192,64,0.08);
}
#page-company.catalog-hub .hub-rule{
  width:72px;height:2px;background:linear-gradient(90deg,var(--gold),transparent);
  margin:0 auto 28px;border-radius:2px;
}
#page-company.catalog-hub .section.content{
  background:#060d16;
  padding:110px 48px 130px;
  position:relative;
}
#page-company.catalog-hub .section.content::before{display:none;}
#page-company.catalog-hub .section.content::after{
  content:'';position:absolute;inset:0;pointer-events:none;opacity:0.035;mix-blend-mode:overlay;
  background-image:url("data:image/svg+xml,%3Csvg viewBox='0 0 256 256' xmlns='http://www.w3.org/2000/svg'%3E%3Cfilter id='n'%3E%3CfeTurbulence type='fractalNoise' baseFrequency='0.9' numOctaves='3' stitchTiles='stitch'/%3E%3C/filter%3E%3Crect width='100%25' height='100%25' filter='url(%23n)'/%3E%3C/svg%3E");
  background-size:200px 200px;
}
#page-company.catalog-hub .section-inner{max-width:1180px;position:relative;z-index:1;}
#page-company.catalog-hub .section-eyebrow{
  font-family:var(--mono,'IBM Plex Mono',monospace);
  color:rgba(240,192,64,0.88);
  letter-spacing:0.24em;
  font-size:12px;
}
#page-company.catalog-hub .section-title{color:#fff;}
#page-company.catalog-hub .section-title em{color:var(--gold);}
#page-company.catalog-hub .section-sub{color:rgba(255,255,255,0.55);font-size:17px;line-height:1.7;}
#page-company .section-lead{display:flex;align-items:flex-start;gap:28px;}
#page-company .section-num{
  font-family:var(--mono,'IBM Plex Mono',monospace);
  font-size:12px;font-weight:600;letter-spacing:0.22em;color:var(--gold);
  flex-shrink:0;border-top:1px solid var(--gold);width:52px;text-align:center;
  line-height:1;padding-top:14px;
}
#page-company .section-lead .section-title{
  font-size:clamp(44px,6vw,64px);letter-spacing:-2px;line-height:1.02;
}
#page-company .hub-grid{
  display:grid;
  grid-template-columns:repeat(12,minmax(0,1fr));
  gap:20px;
  margin-top:60px;
}
#page-company .hub-card[data-app="pbj"]{grid-column:span 7;min-height:380px;}
#page-company .hub-card[data-app="hhh"]{grid-column:span 5;min-height:380px;}
#page-company .hub-card[data-app="pal"]{grid-column:span 5;min-height:340px;}
#page-company .hub-card[data-app="cvc"]{grid-column:span 7;min-height:340px;}
#page-company .hub-card{
  display:grid;
  grid-template-columns:1fr minmax(118px,172px);
  gap:12px 18px;
  align-items:end;
  border-radius:28px;
  padding:40px 34px 30px;
  border:1px solid rgba(255,255,255,0.11);
  box-shadow:0 32px 72px rgba(0,0,0,0.45);
  position:relative;overflow:hidden;cursor:pointer;text-align:left;
  background:
    radial-gradient(ellipse 75% 95% at 95% 0%, var(--hub-glow), transparent 55%),
    linear-gradient(158deg, var(--hub-dk) 0%, var(--hub-md) 100%);
  transition:transform .34s var(--ease), border-color .34s, box-shadow .34s;
}
#page-company .hub-card[data-app="pbj"]{
  --hub-dk:#0A2A4A;--hub-md:#1A4F7A;--hub-glow:rgba(240,192,64,0.32);--hub-accent:#F0C040;
}
#page-company .hub-card[data-app="hhh"]{
  --hub-dk:#2E101A;--hub-md:#5B2333;--hub-glow:rgba(200,170,110,0.32);--hub-accent:#C8AA6E;
}
#page-company .hub-card[data-app="pal"]{
  --hub-dk:#14241B;--hub-md:#2F4A3A;--hub-glow:rgba(232,184,74,0.3);--hub-accent:#E8B84A;
}
#page-company .hub-card[data-app="cvc"]{
  --hub-dk:#0C241C;--hub-md:#1B4D3E;--hub-glow:rgba(212,168,83,0.3);--hub-accent:#D4A853;
}
#page-company .hub-card:hover{
  transform:translateY(-8px) scale(1.012);
  border-color:rgba(255,255,255,0.3);
  box-shadow:0 48px 96px rgba(0,0,0,0.55);
}
#page-company .hub-card::before{
  content:'';position:absolute;left:0;top:0;bottom:0;width:3px;
  background:linear-gradient(180deg,var(--hub-accent),transparent 85%);
  opacity:1;border-radius:0;
}
#page-company .hub-card::after{
  content:'';position:absolute;inset:0;pointer-events:none;
  background:linear-gradient(125deg, transparent 35%, rgba(255,255,255,0.07) 100%);
  opacity:0;transition:opacity .34s;
}
#page-company .hub-card:hover::after{opacity:1;}
#page-company .hub-badge{display:none;}
#page-company .hub-meta{display:none;}
#page-company .hub-index{
  position:static;display:block;margin-bottom:14px;
  font-family:var(--mono,'IBM Plex Mono',monospace);
  font-size:11px;letter-spacing:0.26em;color:var(--hub-accent);font-weight:600;
}
#page-company .hub-name{
  font-size:clamp(30px,3.2vw,40px);margin-bottom:14px;line-height:1.05;color:#fff;
  letter-spacing:-0.03em;
}
#page-company .hub-name em{color:var(--hub-accent);font-style:italic;}
#page-company .hub-tagline{
  font-size:15.5px;line-height:1.58;color:rgba(255,255,255,0.64);
  margin-bottom:26px;max-width:36ch;
}
#page-company .hub-cta{
  font-family:'Manrope',sans-serif !important;
  display:inline-flex;align-items:center;gap:8px;
  background:var(--hub-accent);color:var(--hub-dk);
  border-radius:12px;padding:14px 22px;
  font-size:14px;font-weight:800;letter-spacing:0.01em;text-transform:none;
  box-shadow:0 12px 32px rgba(0,0,0,0.32);width:fit-content;
  transition:transform .22s, background .22s, color .22s, box-shadow .22s;
}
#page-company .hub-card:hover .hub-cta{
  background:#fff;color:var(--hub-dk);transform:translateX(4px);
  box-shadow:0 16px 36px rgba(0,0,0,0.35);
}
#page-company .hub-card-body{position:relative;z-index:1;min-width:0;grid-column:1;}
#page-company .hub-card-shot{
  position:relative;z-index:1;width:100%;max-width:172px;margin:0;justify-self:end;
  padding:10px 10px 16px;border-radius:26px;align-self:end;grid-column:2;grid-row:1 / span 2;
  background:linear-gradient(165deg,#2a2a2e 0%, #0c0c0e 100%);
  border:1px solid rgba(255,255,255,0.18);
  box-shadow:
    0 24px 56px rgba(0,0,0,0.55),
    inset 0 1px 0 rgba(255,255,255,0.12);
  transition:transform .4s var(--ease);
}
#page-company .hub-card:hover .hub-card-shot{transform:translateY(-12px) rotate(-2deg);}
#page-company .hub-card-shot::before{
  content:'';position:absolute;top:5px;left:50%;transform:translateX(-50%);
  width:48px;height:5px;border-radius:999px;background:rgba(0,0,0,0.6);
}
#page-company .hub-card-shot img{
  display:block;width:100%;height:auto;border-radius:18px;aspect-ratio:9/19.5;object-fit:cover;
}
#page-company .hub-card[data-app="pal"] .hub-card-shot img{
  aspect-ratio:1;object-fit:contain;padding:22px;background:rgba(232,184,74,0.1);
}
#page-company .privacy-strip{
  background:#030910;border-color:rgba(255,255,255,0.06);
}
#page-company .privacy-strip .ps-item{color:rgba(255,255,255,0.58);font-weight:500;}
#page-company .privacy-strip .ps-dot{background:var(--gold);}
#page-company .quote-bar{
  background:#02070e;padding:130px 48px;text-align:center;position:relative;
}
#page-company .quote-bar blockquote{
  margin:0 auto;font-size:clamp(34px,4.6vw,56px);color:#fff;max-width:16ch;
  letter-spacing:-0.03em;line-height:1.15;
}
#page-company .quote-bar::before{
  content:'';position:absolute;left:50%;top:52px;transform:translateX(-50%);
  width:48px;height:2px;background:linear-gradient(90deg,transparent,var(--gold),transparent);
}
#page-company .principles{background:#fafbfc;}
#page-company .refuse-line{
  margin-top:48px;padding-top:28px;border-top:1px solid rgba(26,79,122,0.12);
  font-family:var(--mono,'IBM Plex Mono',monospace);
  font-size:11px;font-weight:600;letter-spacing:0.16em;text-transform:uppercase;color:#6a8499;
}
@media (max-width:900px){
  #page-company.catalog-hub .hero.hub-hero{min-height:auto;padding-top:120px;padding-bottom:72px;}
  #page-company .hub-grid{grid-template-columns:1fr;gap:14px;}
  #page-company .hub-card[data-app="pbj"],
  #page-company .hub-card[data-app="hhh"],
  #page-company .hub-card[data-app="pal"],
  #page-company .hub-card[data-app="cvc"]{grid-column:auto;min-height:0;}
  #page-company .hub-card{
    grid-template-columns:1fr 108px;padding:28px 22px;border-radius:22px;
  }
  #page-company .hub-card-shot{max-width:108px;}
  #page-company .hub-card:hover{transform:none;}
  #page-company .hub-card:hover .hub-card-shot{transform:none;}
  #page-company .section-lead{flex-direction:column;gap:16px;}
  #page-company.catalog-hub .section.content{padding:80px 22px 100px;}
  #page-company .quote-bar{padding:96px 24px;}
}

`;

s = s.slice(0, start) + NEW_CSS + s.slice(end);

// Fresh hub copy
s = s.replace(
  /<p class="hero-h1">Fewer apps\.<br><em>Better apps\.<\/em><\/p>\s*<p class="hero-sub">\s*[\s\S]*?<\/p>/,
  `<p class="hero-h1">Fewer apps.<br><em>Better apps.</em></p>
    <p class="hero-sub">
      Four private tools. Built small on purpose. Yours to keep — not to farm.
    </p>`
);

s = s.replace(
  /<div class="hero-actions">\s*<a href="#products" class="btn-primary">\s*[\s\S]*?<\/a>\s*<a href="#principles" class="btn-ghost">[\s\S]*?<\/a>\s*<\/div>/,
  `<div class="hero-actions">
      <a href="#products" class="btn-primary">
        Explore the lineup
        <svg width="16" height="16" viewBox="0 0 16 16" fill="none" aria-hidden="true"><path d="M3 8h10M9 4l4 4-4 4" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round"/></svg>
      </a>
      <a href="#principles" class="btn-ghost">How we build</a>
    </div>`
);

s = s.replace(
  /<div class="privacy-strip" role="complementary">\s*[\s\S]*?<\/div>\s*\n\n<!-- ══ PRODUCTS/,
  `<div class="privacy-strip" role="complementary">
  <div class="ps-item"><div class="ps-dot"></div>No ads. Ever.</div>
  <div class="ps-item"><div class="ps-dot"></div>Fair pricing</div>
  <div class="ps-item"><div class="ps-dot"></div>Built for real people</div>
  <div class="ps-item"><div class="ps-dot"></div>iOS &amp; Android</div>
</div>

<!-- ══ PRODUCTS`
);

s = s.replace(
  /<span class="section-eyebrow">Our Products<\/span>\s*<h2 class="section-title">[\s\S]*?<\/h2>\s*<p class="section-sub">[\s\S]*?<\/p>/,
  `<span class="section-eyebrow">The lineup</span>
        <h2 class="section-title">Software that<br><em>feels finished.</em></h2>
        <p class="section-sub">Each app is its own world — features, guides, and downloads live there. Start anywhere.</p>`
);

const productsOldStart = s.indexOf('<div class="hub-grid">');
const productsOldEnd = s.indexOf('</div>\n  </div>\n</section>\n\n<!-- ══ QUOTE BAR');
if (productsOldStart < 0 || productsOldEnd < 0) {
  // try CRLF
  const altEnd = s.indexOf('</div>\r\n  </div>\r\n</section>\r\n\r\n<!-- ══ QUOTE BAR');
  if (productsOldStart < 0 || altEnd < 0) {
    console.error('products markers', productsOldStart, productsOldEnd, altEnd);
    process.exit(1);
  }
}

function findProductsEnd(html) {
  const markers = [
    '</div>\n  </div>\n</section>\n\n<!-- ══ QUOTE BAR',
    '</div>\r\n  </div>\r\n</section>\r\n\r\n<!-- ══ QUOTE BAR',
  ];
  for (const m of markers) {
    const i = html.indexOf(m);
    if (i >= 0) return { i, m };
  }
  // fallback: find QUOTE BAR and walk back
  const q = html.indexOf('<!-- ══ QUOTE BAR');
  if (q < 0) return null;
  return { i: html.lastIndexOf('<div class="hub-grid">') >= 0 ? html.indexOf('</section>', html.indexOf('<div class="hub-grid">')) : -1, m: null, q };
}

const endInfo = findProductsEnd(s);
if (!endInfo || endInfo.i < 0) {
  console.error('Could not find products end', endInfo);
  process.exit(1);
}

const PRODUCTS = `<div class="hub-grid">

      <div role="button" tabindex="0" data-app="pbj" onclick="showPage('pbj');" onkeydown="if(event.key==='Enter'||event.key===' '){event.preventDefault();showPage('pbj');}" class="hub-card hub-card-featured rv d1">
        <div class="hub-card-body">
          <span class="hub-index" aria-hidden="true">Vol. 01</span>
          <div class="hub-name">Pocket<em>BudJet</em>™</div>
          <p class="hub-tagline">Budgeting that never leaves your phone. Import. Plan. Coach. Zero ads. Zero data games.</p>
          <div class="hub-cta">Open PocketBudJet <span>→</span></div>
        </div>
        <figure class="hub-card-shot" aria-hidden="true">
          <img src="videos/pocketbudjet/partner-showcase/screens/home-concierge.jpg" alt="" width="168" height="364" loading="lazy">
        </figure>
      </div>

      <div role="button" tabindex="0" data-app="hhh" onclick="showPage('hhh');" onkeydown="if(event.key==='Enter'||event.key===' '){event.preventDefault();showPage('hhh');}" class="hub-card hub-card-featured rv d2">
        <div class="hub-card-body">
          <span class="hub-index" aria-hidden="true">Vol. 02</span>
          <div class="hub-name">Handy Horology<br><em>Helper</em>™</div>
          <p class="hub-tagline">Snap a timepiece. Build a museum. Repair with confidence. Live companion on home Wi‑Fi.</p>
          <div class="hub-cta">Open HHH <span>→</span></div>
        </div>
        <figure class="hub-card-shot" aria-hidden="true">
          <img src="assets/screenshots/hhh/intro/02-my-museum.png" alt="" width="148" height="322" loading="lazy">
        </figure>
      </div>

      <div role="button" tabindex="0" data-app="pal" onclick="showPage('pal');" onkeydown="if(event.key==='Enter'||event.key===' '){event.preventDefault();showPage('pal');}" class="hub-card rv d3">
        <div class="hub-card-body">
          <span class="hub-index" aria-hidden="true">Vol. 03</span>
          <div class="hub-name">Pocket Allowance<br><em>Ledger</em>™</div>
          <p class="hub-tagline">Gold tokens. Parent-approved rewards. A family economy that is not a bank.</p>
          <div class="hub-cta">Open PAL <span>→</span></div>
        </div>
        <figure class="hub-card-shot" aria-hidden="true">
          <img src="assets/brand/pal-coin.svg" alt="" width="120" height="120" loading="lazy">
        </figure>
      </div>

      <div role="button" tabindex="0" data-app="cvc" onclick="showPage('cvc');" onkeydown="if(event.key==='Enter'||event.key===' '){event.preventDefault();showPage('cvc');}" class="hub-card rv d4">
        <div class="hub-card-body">
          <span class="hub-index" aria-hidden="true">Vol. 04</span>
          <div class="hub-name">Curator's Vault:<br><em>Classics</em>™</div>
          <p class="hub-tagline">Coins, cards, stamps, paper, lighters — photograph, organize, value. Your vault. Your rules.</p>
          <div class="hub-cta">Open Curator's Vault <span>→</span></div>
        </div>
        <figure class="hub-card-shot" aria-hidden="true">
          <img src="assets/screenshots/cvc/02-collection.png" alt="" width="168" height="298" loading="lazy">
        </figure>
      </div>

    `;

if (endInfo.m) {
  s = s.slice(0, productsOldStart) + PRODUCTS + s.slice(endInfo.i);
} else {
  console.error('unexpected end marker shape');
  process.exit(1);
}

s = s.replace(
  /<blockquote>Quality is the only growth strategy that ages well\.<\/blockquote>/,
  '<blockquote>Make it excellent — or don&rsquo;t ship it.</blockquote>'
);

// Product page heroes — sharp commercial copy
function replaceHeroSub(html, pageId, newInner) {
  const marker = `id="${pageId}"`;
  const start = html.indexOf(marker);
  if (start < 0) return html;
  const chunkEnd = html.indexOf('</section>', start);
  const chunk = html.slice(start, chunkEnd);
  const re = /<p class="hero-sub"[^>]*>[\s\S]*?<\/p>/;
  if (!re.test(chunk)) {
    console.warn('no hero-sub for', pageId);
    return html;
  }
  const newChunk = chunk.replace(re, `<p class="hero-sub">${newInner}</p>`);
  return html.slice(0, start) + newChunk + html.slice(chunkEnd);
}

s = replaceHeroSub(
  s,
  'page-pbj',
  '<strong>15 days of Premium. No card.</strong> Import statements, plan spending, and coach yourself without ads or account games. Then $9.99/mo or $74.99/yr — or keep import &amp; manual budgeting free. Bank sync is Premium. <strong>Cancel anytime.</strong>'
);
s = replaceHeroSub(
  s,
  'page-hhh',
  'Photograph a watch or clock — get an ID with an honest confidence score. Run a private museum, follow Clockworks-ready repair, and open a live Web Companion on home Wi‑Fi with a short pairing code. Full UI in <strong>8 languages</strong>.'
);
s = replaceHeroSub(
  s,
  'page-pal',
  'A home token economy: gold tokens, parent-approved rewards, habits that stick. <strong>Not</strong> kid banking — no debit card, no custodial account. Kids join on home Wi‑Fi.'
);
s = replaceHeroSub(
  s,
  'page-cvc',
  'Five categories. AI ID for coins, cards, stamps, and paper money — lighters by hand. Pens, knives, and watches live in other JosspaTech apps. Full UI in <strong>7 languages</strong>. <strong>15-day trial</strong>, then Pro at <strong>$9.99/mo · $74.99/yr</strong>.'
);

fs.writeFileSync(file, s);
console.log('OK: dynamite hub shipped');
