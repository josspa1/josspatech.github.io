#!/usr/bin/env node
'use strict';
/**
 * Award-caliber elevation pass for JosspaTech hub.
 * Patterns: Cartier/Brunello-level editorial calm — breath, type hierarchy,
 * atmospheric depth, gateway cards as the only interactive cards.
 */
const fs = require('fs');
const path = require('path');
const FILE = path.join(__dirname, '..', 'index.html');
let html = fs.readFileSync(FILE, 'utf8');

// Richer type pairing: Playfair (display) + Manrope (UI) — not Inter/Roboto
html = html.replace(
  /family=Playfair\+Display:[^"]+/,
  'family=Playfair+Display:ital,wght@0,400;0,700;0,900;1,400;1,700&family=Manrope:wght@400;500;600;700;800',
);
html = html.replace(
  /body\{font-family:'Source Sans 3',sans-serif;/,
  "body{font-family:'Manrope',sans-serif;",
);
// Second body rule if duplicated later in file
html = html.replace(
  /body\{font-family:'Source Sans 3',sans-serif;/g,
  "body{font-family:'Manrope',sans-serif;",
);

html = html.replace(
  /content="JosspaTech — Mobile software built to last\. PocketBudJet: the budget app that keeps your data on your device\."/,
  'content="JosspaTech — Fewer apps. Better apps. Private mobile tools for budgeting, horology, family rewards, and collecting."',
);

const ELEVATION = `
/* ══ Award-caliber elevation (editorial luxury hub) ═══════ */
::selection{background:rgba(240,192,64,0.35);color:var(--navy-dk);}
.site-nav{
  backdrop-filter:blur(18px) saturate(1.2);
  -webkit-backdrop-filter:blur(18px) saturate(1.2);
  border-bottom:1px solid rgba(240,192,64,0.1);
}
.hero.hub-hero{
  min-height:min(88vh,820px);
  display:flex;align-items:center;justify-content:center;
  padding:120px 48px 110px;
}
.hero.hub-hero::before{
  content:'';position:absolute;inset:0;pointer-events:none;
  background:
    radial-gradient(ellipse 50% 40% at 50% 0%, rgba(240,192,64,0.08), transparent 70%),
    linear-gradient(180deg, transparent 55%, rgba(7,24,40,0.55) 100%);
  z-index:0;
}
.hub-hero .hero-inner{text-align:center;}
.hub-hero .hero-h1{
  font-size:clamp(48px,8vw,76px);
  font-weight:900;
  letter-spacing:-2px;
  line-height:0.98;
  max-width:14ch;
  margin-left:auto;margin-right:auto;
}
.hub-hero .hero-sub{
  font-size:17px;font-weight:400;letter-spacing:0.01em;
  color:rgba(255,255,255,0.58);
  max-width:34rem;
}
.hub-hero .hero-eyebrow{
  margin-bottom:22px;
  letter-spacing:3px;
}
.hub-rule{
  width:48px;height:1px;margin:0 auto 28px;
  background:linear-gradient(90deg,transparent,var(--gold),transparent);
  animation:hubFadeUp .9s var(--ease) .05s both;
}
#page-company .section.content{
  background:
    linear-gradient(180deg,#f7f9fc 0%, #edf2f7 100%);
  position:relative;
}
#page-company .section.content::before{
  content:'';position:absolute;top:0;left:10%;right:10%;height:1px;
  background:linear-gradient(90deg,transparent,rgba(26,79,122,0.12),transparent);
}
#page-company .section-title{
  font-size:clamp(36px,5vw,52px);
  letter-spacing:-1.2px;
  line-height:1.05;
}
#page-company .section-sub{
  font-size:16px;color:var(--slate);line-height:1.65;
}
.hub-card{
  border-radius:26px;
  padding:44px 40px 38px;
  background:
    linear-gradient(155deg, #0e3558 0%, #123f68 42%, #0c2d4a 100%);
  box-shadow:
    0 1px 0 rgba(255,255,255,0.06) inset,
    0 18px 50px rgba(7,24,40,0.28);
}
.hub-card:hover{
  transform:translateY(-8px) scale(1.01);
}
.hub-index{
  position:absolute;top:28px;right:32px;
  font-family:'Playfair Display',serif;
  font-size:13px;font-weight:700;letter-spacing:2px;
  color:rgba(255,255,255,0.18);
}
.hub-name{font-size:clamp(26px,2.6vw,32px);}
.hub-tagline{font-size:15.5px;line-height:1.6;color:rgba(255,255,255,0.55);}
.hub-cta{
  border-radius:999px;padding:13px 22px;
  letter-spacing:0.02em;
  box-shadow:0 8px 24px rgba(240,192,64,0.22);
}
.quote-bar{
  position:relative;overflow:hidden;
  padding:88px 48px;
  background:
    radial-gradient(ellipse 60% 80% at 20% 50%, rgba(46,111,163,0.35), transparent 60%),
    radial-gradient(ellipse 50% 70% at 90% 40%, rgba(240,192,64,0.12), transparent 55%),
    var(--navy-dk);
}
.quote-bar blockquote{
  font-size:clamp(26px,3.4vw,40px);
  font-weight:700;
  max-width:780px;
  letter-spacing:-0.6px;
  position:relative;z-index:1;
}
#page-company .principles{
  background:
    linear-gradient(180deg,#fff 0%, #f8fafc 100%);
}
#page-company .principles-grid{
  gap:0;margin-top:56px;
  border-top:1px solid rgba(26,79,122,0.1);
}
#page-company .principle{
  border:none;border-radius:0;padding:40px 32px 40px 0;
  border-right:1px solid rgba(26,79,122,0.1);
  box-shadow:none;background:transparent;
}
#page-company .principle:last-child{border-right:none;padding-right:0;}
#page-company .principle:hover{
  transform:none;box-shadow:none;border-color:rgba(26,79,122,0.1);
}
#page-company .principle-icon{
  background:transparent;border:1px solid rgba(26,79,122,0.14);
  width:48px;height:48px;border-radius:50%;
}
#page-company .principle-title{font-size:22px;margin-bottom:12px;}
#page-company .principle-body{font-size:15px;color:#4a6680;max-width:32ch;}
#page-hhh .hero .hero-h1{font-size:clamp(38px,5.5vw,56px);letter-spacing:-1.4px;}
#page-hhh .hero .hero-sub{font-size:16px;line-height:1.7;color:rgba(255,255,255,0.62);}
@media (max-width:820px){
  #page-company .principle{border-right:none;border-bottom:1px solid rgba(26,79,122,0.1);padding:32px 0;}
  #page-company .principle:last-child{border-bottom:none;}
  .hero.hub-hero{min-height:auto;padding:88px 24px 72px;}
}
@media (prefers-reduced-motion:reduce){
  .hub-hero .hero-h1,.hub-hero .hero-sub,.hub-hero .hero-actions,.hub-rule{animation:none;}
  .hub-card{transition:none;}
}
`;

if (!html.includes('Award-caliber elevation')) {
  html = html.replace(
    /@media \(max-width:820px\)\{\s*\.hub-grid\{grid-template-columns:1fr;\}\s*\.hero\.hub-hero\{padding:72px 24px 64px;\}\s*\}/,
    `@media (max-width:820px){
  .hub-grid{grid-template-columns:1fr;}
  .hero.hub-hero{padding:72px 24px 64px;}
}
${ELEVATION}`,
  );
}

// Hero: add gold rule under eyebrow
if (!html.includes('hub-rule')) {
  html = html.replace(
    `<div class="hero-eyebrow">
      <div class="hero-eyebrow-dot"></div>
      JosspaTech
    </div>
    <h1 class="hero-h1">`,
    `<div class="hero-eyebrow">
      <div class="hero-eyebrow-dot"></div>
      JosspaTech
    </div>
    <div class="hub-rule" aria-hidden="true"></div>
    <h1 class="hero-h1">`,
  );
}

// Numbered hub cards
const indexes = ['01', '02', '03', '04'];
let idx = 0;
html = html.replace(/class="hub-card rv d(\d)"/g, (m, d) => {
  const n = indexes[idx++] || '0' + d;
  return `class="hub-card rv d${d}"><span class="hub-index" aria-hidden="true">${n}</span`;
});
// Fix accidental double-open: hub-card"><span...><div  — need closing after span self-contained
// Current replace produces: class="hub-card rv d1"><span class="hub-index"...></span  MISSING >
// Actually I produced: `class="hub-card rv d1"><span class="hub-index" aria-hidden="true">01</span`
// then next char is still `>` from original? Original was `class="hub-card rv d1">` so replace removes the closing >
// Result: class="hub-card rv d1"><span...>01</span<div class="hub-badge"
// That's valid HTML if span is closed. Good - but we lost the `>` after class... wait:
// Original: class="hub-card rv d1">
// Replace match: class="hub-card rv d1"
// Replacement: class="hub-card rv d1"><span...>01</span
// Remaining after match: >
// So: class="hub-card rv d1"><span...>01</span>
// Perfect.

fs.writeFileSync(FILE, html);
console.log('Elevated design written', fs.statSync(FILE).size);
