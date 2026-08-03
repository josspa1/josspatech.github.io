/**
 * 1) Restore missing HHH/PAL feature-band layout CSS (was dropped; breaks phone)
 * 2) Add aggressive product-page mobile fixes
 * 3) Refresh brand board copy for Signature JT mark
 */
const fs = require('fs');
const path = require('path');
const root = path.join(__dirname, '..');
const file = path.join(root, 'index.html');
let s = fs.readFileSync(file, 'utf8');

const layoutCss = fs.readFileSync(path.join(__dirname, '_hhh-layout-extract.css'), 'utf8');

const MOBILE = `
/* ══ Product pages — phone layout rescue ═══════════════════════════════════ */
#page-pbj, #page-hhh, #page-pal, #page-cvc { overflow-x: clip; }
@media (max-width: 720px) {
  #page-pbj .hero,
  #page-hhh .hero,
  #page-pal .hero,
  #page-cvc .hero {
    min-height: 0 !important;
    padding: 88px 18px 36px !important;
    overflow: hidden !important;
  }
  #page-pbj .hero-inner,
  #page-hhh .hero-inner,
  #page-pal .hero-inner,
  #page-cvc .hero-inner {
    display: flex !important;
    flex-direction: column !important;
    grid-template-columns: none !important;
    gap: 28px !important;
    width: 100% !important;
    max-width: 100% !important;
    text-align: left !important;
    align-items: stretch !important;
  }
  #page-pbj .hero-text,
  #page-hhh .hero-text,
  #page-pal .hero-text,
  #page-cvc .hero-text { text-align: left !important; width: 100%; }
  #page-pbj .hero-bc,
  #page-hhh .hero-bc,
  #page-pal .hero-bc,
  #page-cvc .hero-bc,
  #page-pbj .vol-kicker,
  #page-hhh .vol-kicker,
  #page-pal .vol-kicker,
  #page-cvc .vol-kicker { justify-content: flex-start !important; }
  #page-pbj .vol-rule,
  #page-hhh .vol-rule,
  #page-pal .vol-rule,
  #page-cvc .vol-rule { margin-left: 0 !important; margin-right: 0 !important; }
  #page-pbj .hero-h1,
  #page-hhh .hero-h1,
  #page-pal .hero-h1,
  #page-cvc .hero-h1 {
    font-size: clamp(28px, 8.2vw, 36px) !important;
    max-width: 100% !important;
    margin-left: 0 !important;
    margin-right: 0 !important;
    letter-spacing: -0.03em !important;
  }
  #page-pbj .vol-name,
  #page-hhh .vol-name,
  #page-pal .vol-name,
  #page-cvc .vol-name { font-size: clamp(22px, 6.5vw, 28px) !important; }
  #page-pbj .hero-sub,
  #page-hhh .hero-sub,
  #page-pal .hero-sub,
  #page-cvc .hero-sub {
    font-size: 15px !important;
    line-height: 1.65 !important;
    max-width: 100% !important;
  }
  #page-pbj .hero-acts,
  #page-hhh .hero-acts,
  #page-pal .hero-acts,
  #page-cvc .hero-acts {
    display: flex !important;
    flex-direction: column !important;
    align-items: stretch !important;
    justify-content: flex-start !important;
    gap: 10px !important;
    width: 100%;
  }
  #page-pbj .btn-primary,
  #page-hhh .btn-primary,
  #page-pal .btn-primary,
  #page-cvc .btn-primary,
  #page-pbj .btn-ghost,
  #page-hhh .btn-ghost,
  #page-pal .btn-ghost,
  #page-cvc .btn-ghost {
    width: 100%;
    justify-content: center;
    text-align: center;
    box-sizing: border-box;
  }
  #page-pbj .pbj-hero-shots,
  #page-hhh .pbj-hero-shots,
  #page-cvc .pbj-hero-shots {
    width: 100%;
    justify-content: center !important;
    margin: 0 auto !important;
    gap: 0 !important;
    overflow: hidden;
  }
  #page-pbj .pbj-shot-side,
  #page-hhh .pbj-shot-side,
  #page-cvc .pbj-shot-side { display: none !important; }
  #page-pbj .pbj-shot-center,
  #page-hhh .pbj-shot-center,
  #page-cvc .pbj-shot-center {
    width: min(210px, 56vw) !important;
    margin: 0 auto !important;
    transform: none !important;
    padding: 8px 8px 12px !important;
  }
  #page-pbj .pbj-shot-center img,
  #page-hhh .pbj-shot-center img,
  #page-cvc .pbj-shot-center img,
  .pbj-shot-center img {
    width: 100% !important;
    height: auto !important;
    max-width: 100% !important;
  }
  #page-pal .pal-hero-visual {
    justify-self: stretch !important;
    max-width: 100% !important;
    width: 100% !important;
  }
  #page-pal .pal-brand-stack { padding: 36px 22px 32px; }
  #page-pbj .pstrip,
  #page-hhh .pstrip,
  #page-pal .pstrip,
  #page-cvc .pstrip {
    width: 100%;
    max-width: 100%;
    padding: 14px 16px !important;
    gap: 14px !important;
    justify-content: flex-start !important;
    flex-wrap: nowrap !important;
    overflow-x: auto;
    -webkit-overflow-scrolling: touch;
    scrollbar-width: none;
  }
  #page-pbj .pstrip::-webkit-scrollbar,
  #page-hhh .pstrip::-webkit-scrollbar,
  #page-pal .pstrip::-webkit-scrollbar,
  #page-cvc .pstrip::-webkit-scrollbar { display: none; }
  #page-pbj .psi,
  #page-hhh .psi,
  #page-pal .psi,
  #page-cvc .psi { flex: 0 0 auto; white-space: nowrap; font-size: 12px; }
  .hhh-how-it-works,
  .hhh-app-tour,
  .hhh-feature-band { padding-left: 18px !important; padding-right: 18px !important; }
  .hhh-steps { grid-template-columns: 1fr !important; }
  .hhh-feature-band-inner {
    grid-template-columns: 1fr !important;
    gap: 28px !important;
    direction: ltr !important;
  }
  .hhh-feature-band--reverse .hhh-feature-band-inner { direction: ltr !important; }
  .hhh-feature-copy {
    max-width: none !important;
    margin: 0 !important;
    text-align: left !important;
  }
  .hhh-feature-visual,
  .hhh-phone-shot,
  .pal-brand-panel {
    max-width: min(280px, 78vw) !important;
    margin: 0 auto !important;
  }
  .vol-pin {
    grid-template-columns: 1fr !important;
    padding: 48px 18px !important;
    gap: 24px !important;
  }
  .vol-pin-visual { position: relative !important; top: auto !important; }
  .vol-pin-visual img { width: min(220px, 58vw) !important; }
  #page-pbj .section,
  #page-hhh .section,
  #page-pal .section,
  #page-cvc .section,
  #page-pbj .pricing-sec,
  #page-hhh .pricing-sec,
  #page-pbj .priv-sec,
  #page-pbj .comp-sec { padding-left: 18px !important; padding-right: 18px !important; }
  .site-nav { padding: 0 16px !important; }
  .nav-tagline { display: none; }
}
`;

const MARKER = '/* ══ END PRODUCT PAGE DYNAMITE';
if (s.includes('Product pages — phone layout rescue')) {
  console.log('mobile CSS already present — replacing layout restore only if needed');
} else {
  const i = s.indexOf(MARKER);
  if (i < 0) {
    console.error('dynamite end marker missing');
    process.exit(1);
  }
  // Insert restored layout CSS before END marker, then mobile after END block
  const endClose = s.indexOf('*/', i) + 2;
  const restoreBlock = `\n/* ══ Restored product feature-band layout (was missing) ═══════════════════ */\n${layoutCss}\n${MOBILE}\n`;
  s = s.slice(0, endClose) + restoreBlock + s.slice(endClose);
  console.log('Inserted layout + mobile CSS');
}

fs.writeFileSync(file, s);

// Brand board update
const brand = `<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>JosspaTech Brand — Logo System</title>
<link href="https://fonts.googleapis.com/css2?family=Playfair+Display:wght@700;900&family=Manrope:wght@500;700;800&display=swap" rel="stylesheet">
<style>
  :root{--navy:#0C3358;--navy-md:#1A4F7A;--gold:#F0C040;--paper:#f4f7fa;}
  *{box-sizing:border-box;margin:0;padding:0}
  body{font-family:Manrope,system-ui,sans-serif;background:var(--paper);color:var(--navy);line-height:1.5}
  header{background:linear-gradient(165deg,#06111c,#0C3358 55%,#1A4F7A);color:#fff;padding:64px 24px 56px;text-align:center}
  header img.hero{width:min(200px,46vw);height:auto;margin:0 auto 24px;display:block;border-radius:36px;box-shadow:0 24px 48px rgba(0,0,0,.35)}
  header h1{font-family:'Playfair Display',Georgia,serif;font-size:clamp(28px,5vw,44px);letter-spacing:-1px;margin-bottom:10px}
  header p{opacity:.65;max-width:36rem;margin:0 auto;font-size:15px}
  main{max-width:960px;margin:0 auto;padding:40px 18px 80px}
  h2{font-family:'Playfair Display',Georgia,serif;font-size:26px;margin:36px 0 8px}
  .lead{color:#5a7390;margin-bottom:22px}
  .grid{display:grid;grid-template-columns:1fr;gap:14px}
  @media(min-width:700px){.grid{grid-template-columns:1fr 1fr}}
  .card{border-radius:18px;padding:28px 22px;border:1px solid rgba(12,51,88,.1);background:#fff}
  .card.dark{background:linear-gradient(160deg,#0C3358,#1A4F7A);border-color:rgba(255,255,255,.08)}
  .card h3{font-size:12px;font-weight:800;letter-spacing:.14em;text-transform:uppercase;margin-bottom:18px;color:#5a7390}
  .card.dark h3{color:rgba(240,192,64,.85)}
  .card img{display:block;margin:0 auto;max-width:100%;height:auto}
  .card code{display:block;margin-top:16px;font-size:11px;color:#7a93a8;word-break:break-all}
  .card.dark code{color:rgba(255,255,255,.45)}
  a.back{display:inline-block;margin-top:32px;color:var(--navy-md);font-weight:700;text-decoration:none}
</style>
</head>
<body>
<header>
  <img class="hero" src="./josspatech-mark-app.svg" alt="JosspaTech mark">
  <h1>JosspaTech logo system</h1>
  <p>Signature JT — a bold J with a gold T-bar. Clean, app-native, built from scratch (not the old diamond).</p>
</header>
<main>
  <h2>Primary assets</h2>
  <p class="lead">Relative paths on this page. SVGs scale cleanly for store listings and the site.</p>
  <div class="grid">
    <div class="card dark">
      <h3>Mark — dark UI</h3>
      <img src="./josspatech-mark.svg" alt="Mark" width="120" height="120">
      <code>josspatech-mark.svg</code>
    </div>
    <div class="card">
      <h3>App icon / favicon</h3>
      <img src="./josspatech-mark-app.svg" alt="App mark" width="120" height="120" style="border-radius:28px">
      <code>josspatech-mark-app.svg</code>
    </div>
    <div class="card dark">
      <h3>Horizontal lockup</h3>
      <img src="./josspatech-logo.svg" alt="Logo lockup" width="280">
      <code>josspatech-logo.svg</code>
    </div>
    <div class="card">
      <h3>Light lockup</h3>
      <img src="./josspatech-logo-light.svg" alt="Light logo" width="280">
      <code>josspatech-logo-light.svg</code>
    </div>
    <div class="card dark" style="grid-column:1/-1">
      <h3>Stacked</h3>
      <img src="./josspatech-logo-stacked.svg" alt="Stacked logo" width="220">
      <code>josspatech-logo-stacked.svg</code>
    </div>
  </div>
  <a class="back" href="/">← Back to josspatech.com</a>
</main>
</body>
</html>
`;
fs.writeFileSync(path.join(root, 'assets', 'brand', 'index.html'), brand);
console.log('Brand board updated');
console.log('OK');
