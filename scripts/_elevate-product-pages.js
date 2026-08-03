/**
 * Elevate product pages to hub craft level:
 * film grain, richer atmospheres, glowing CTAs, premium device frames,
 * trust-strip polish, PAL token panel upgrade.
 */
const fs = require('fs');
const path = require('path');
const file = path.join(__dirname, '..', 'index.html');
let s = fs.readFileSync(file, 'utf8');

const MARKER = '/* ══ PRODUCT PAGE DYNAMITE';
if (s.includes(MARKER)) {
  console.log('Already elevated — replacing block');
  const start = s.indexOf(MARKER);
  const end = s.indexOf('/* ══ END PRODUCT PAGE DYNAMITE');
  if (end < 0) {
    console.error('end marker missing');
    process.exit(1);
  }
  const endClose = s.indexOf('*/', end) + 2;
  s = s.slice(0, start) + s.slice(endClose);
}

const INSERT_AFTER = `@media (max-width:960px){
  #page-pbj .hero-inner,
  #page-hhh .hero-inner,
  #page-cvc .hero-inner{
    grid-template-columns:1fr;
    text-align:center;
  }`;

// Find a unique stable insertion point: right before HOMEPAGE STYLES or after volumes media block end
const insertAt = s.indexOf('/* ═══════════════════════════════════\n     HOMEPAGE STYLES');
const altInsert = s.indexOf('.hero-inner{position:relative;z-index:1;max-width:760px;margin:0 auto;}');

let point = -1;
// Insert after the volume @media block that ends with min-height:auto
const volEnd = s.indexOf('#page-cvc .hero{min-height:auto;padding:56px 24px 48px;}');
if (volEnd > 0) {
  const close = s.indexOf('}', volEnd);
  // find closing of media query
  let i = close + 1;
  // skip whitespace and find next }
  const mqClose = s.indexOf('\n}', volEnd);
  // better: search for pattern after volumes section
  const afterVol = s.indexOf('\n\n/* ', volEnd);
  if (afterVol > 0) point = afterVol + 2;
}
if (point < 0 && insertAt > 0) point = insertAt;
if (point < 0) {
  console.error('insert point not found');
  process.exit(1);
}

const CSS = `/* ══ PRODUCT PAGE DYNAMITE — match hub craft ═══════════════════════════════ */
#page-pbj .hero,
#page-hhh .hero,
#page-pal .hero,
#page-cvc .hero{
  position:relative;overflow:hidden;
  min-height:min(92vh,900px);
  padding:88px 48px 72px;
  background:
    radial-gradient(ellipse 85% 65% at 80% -10%, var(--mesh-b), transparent 55%),
    radial-gradient(ellipse 50% 45% at 5% 95%, var(--mesh-a), transparent 50%),
    radial-gradient(ellipse 40% 35% at 95% 70%, rgba(255,255,255,0.04), transparent 45%),
    linear-gradient(168deg, var(--brand-dk) 0%, var(--brand) 48%, var(--surface-deep) 100%);
}
#page-pbj .hero::before,
#page-hhh .hero::before,
#page-pal .hero::before,
#page-cvc .hero::before{
  display:block !important;
  content:'';position:absolute;inset:0;pointer-events:none;z-index:0;
  background:linear-gradient(180deg, transparent 40%, rgba(0,0,0,0.35) 100%);
}
#page-pbj .hero::after,
#page-hhh .hero::after,
#page-pal .hero::after,
#page-cvc .hero::after{
  content:'';position:absolute;inset:0;pointer-events:none;z-index:1;opacity:0.055;mix-blend-mode:overlay;
  background-image:url("data:image/svg+xml,%3Csvg viewBox='0 0 256 256' xmlns='http://www.w3.org/2000/svg'%3E%3Cfilter id='n'%3E%3CfeTurbulence type='fractalNoise' baseFrequency='0.85' numOctaves='4' stitchTiles='stitch'/%3E%3C/filter%3E%3Crect width='100%25' height='100%25' filter='url(%23n)'/%3E%3C/svg%3E");
  background-size:160px 160px;
}
#page-pbj .hero-inner,
#page-hhh .hero-inner,
#page-pal .hero-inner,
#page-cvc .hero-inner{
  position:relative;z-index:2;
}
#page-pbj .vol-num,
#page-hhh .vol-num,
#page-pal .vol-num,
#page-cvc .vol-num{
  font-family:var(--mono,'IBM Plex Mono',monospace) !important;
  font-size:11px;font-weight:600;letter-spacing:0.26em;
  border-top:1px solid var(--brand-accent);
  padding-top:12px;
}
#page-pbj .vol-name,
#page-hhh .vol-name,
#page-pal .vol-name,
#page-cvc .vol-name{
  font-size:clamp(30px,3.6vw,44px);
  letter-spacing:-0.03em;
}
#page-pbj .vol-rule,
#page-hhh .vol-rule,
#page-pal .vol-rule,
#page-cvc .vol-rule{
  width:64px;height:2px;border-radius:2px;opacity:1;
  background:linear-gradient(90deg,var(--brand-accent),transparent);
}
#page-pbj .hero-h1,
#page-hhh .hero-h1,
#page-pal .hero-h1,
#page-cvc .hero-h1{
  font-size:clamp(38px,5.2vw,60px);
  letter-spacing:-0.035em;line-height:1.05;
  max-width:14ch;margin-bottom:18px;
}
#page-pbj .hero-tagline,
#page-hhh .hero-tagline,
#page-pal .hero-tagline,
#page-cvc .hero-tagline{
  font-family:var(--mono,'IBM Plex Mono',monospace) !important;
  font-size:12px;letter-spacing:0.18em;
  color:rgba(255,255,255,0.45);
}
#page-pbj .hero-sub,
#page-hhh .hero-sub,
#page-pal .hero-sub,
#page-cvc .hero-sub{
  font-size:17px;line-height:1.7;
  color:rgba(255,255,255,0.64);
  max-width:38rem;margin-bottom:32px;
}
#page-pbj .btn-primary,
#page-hhh .btn-primary,
#page-pal .btn-primary,
#page-cvc .btn-primary{
  border-radius:12px;padding:15px 26px;font-size:15px;font-weight:800;
  box-shadow:0 14px 40px color-mix(in srgb, var(--brand-accent) 38%, transparent);
}
#page-pbj .btn-ghost,
#page-hhh .btn-ghost,
#page-pal .btn-ghost,
#page-cvc .btn-ghost{
  font-family:'Manrope',sans-serif !important;
  background:rgba(255,255,255,0.05);
  border:1px solid rgba(255,255,255,0.18) !important;
  border-radius:12px;padding:12px 18px;
  color:rgba(255,255,255,0.85);
  font-size:13px;font-weight:700;letter-spacing:0.02em;text-transform:none;
  backdrop-filter:blur(8px);
}
#page-pbj .btn-ghost:hover,
#page-hhh .btn-ghost:hover,
#page-pal .btn-ghost:hover,
#page-cvc .btn-ghost:hover{
  border-color:color-mix(in srgb, var(--brand-accent) 55%, transparent) !important;
  color:#fff;background:color-mix(in srgb, var(--brand-accent) 10%, transparent);
}
/* Premium device frames — match hub phone tiles */
#page-pbj .pbj-hero-shots,
#page-hhh .pbj-hero-shots,
#page-cvc .pbj-hero-shots{
  gap:14px;perspective:900px;
}
#page-pbj .pbj-shot,
#page-hhh .pbj-shot,
#page-cvc .pbj-shot{
  border-radius:28px !important;
  padding:11px 11px 16px !important;
  background:linear-gradient(165deg,#2a2a2e 0%, #0c0c0e 100%) !important;
  border:1px solid rgba(255,255,255,0.18) !important;
  box-shadow:
    0 28px 64px rgba(0,0,0,0.55),
    inset 0 1px 0 rgba(255,255,255,0.12) !important;
  transition:transform .4s var(--ease), box-shadow .4s;
}
#page-pbj .pbj-shot::before,
#page-hhh .pbj-shot::before,
#page-cvc .pbj-shot::before{
  top:5px;width:48px;height:5px;background:rgba(0,0,0,0.6);
}
#page-pbj .pbj-shot img,
#page-hhh .pbj-shot img,
#page-cvc .pbj-shot img{
  border-radius:18px !important;display:block;width:100%;height:auto;
}
#page-pbj .pbj-shot-center,
#page-hhh .pbj-shot-center,
#page-cvc .pbj-shot-center{
  transform:translateY(-8px) scale(1.04);
  z-index:2;
}
#page-pbj .pbj-shot-side,
#page-hhh .pbj-shot-side,
#page-cvc .pbj-shot-side{
  transform:scale(0.9);opacity:0.9;
}
#page-pbj .hero:hover .pbj-shot-center,
#page-hhh .hero:hover .pbj-shot-center,
#page-cvc .hero:hover .pbj-shot-center{
  transform:translateY(-14px) scale(1.05);
}
#page-pbj .hero:hover .pbj-shot-side:first-child,
#page-hhh .hero:hover .pbj-shot-side:first-child,
#page-cvc .hero:hover .pbj-shot-side:first-child{
  transform:scale(0.92) rotate(-3deg) translateY(-4px);
}
#page-pbj .hero:hover .pbj-shot-side:last-child,
#page-hhh .hero:hover .pbj-shot-side:last-child,
#page-cvc .hero:hover .pbj-shot-side:last-child{
  transform:scale(0.92) rotate(3deg) translateY(-4px);
}
/* Full-bleed trust strip under hero */
#page-pbj .pstrip,
#page-hhh .pstrip,
#page-pal .pstrip,
#page-cvc .pstrip{
  max-width:none;margin:0;box-sizing:border-box;
  width:100%;
  justify-content:center;
  gap:clamp(18px,3vw,36px);
  padding:18px 48px;
  background:color-mix(in srgb, var(--brand-dk) 92%, #000);
  border-top:1px solid rgba(255,255,255,0.06);
  border-bottom:1px solid rgba(255,255,255,0.04);
  position:relative;z-index:2;
}
#page-pbj .psi,
#page-hhh .psi,
#page-pal .psi,
#page-cvc .psi{
  color:rgba(255,255,255,0.58);font-weight:500;font-size:13px;
}
/* Feature / how sections — darker studio atmosphere */
#page-pbj .hhh-how-it-works,
#page-hhh .hhh-how-it-works,
#page-pal .hhh-how-it-works,
#page-cvc .hhh-how-it-works,
#page-pbj .hhh-app-tour,
#page-hhh .hhh-app-tour,
#page-pal .hhh-app-tour,
#page-cvc .hhh-app-tour{
  background:#060d16 !important;
  border-color:rgba(255,255,255,0.06) !important;
}
#page-pbj .hhh-how-title,
#page-hhh .hhh-how-title,
#page-pal .hhh-how-title,
#page-cvc .hhh-how-title,
#page-pbj .hhh-feature-headline,
#page-hhh .hhh-feature-headline,
#page-pal .hhh-feature-headline,
#page-cvc .hhh-feature-headline{
  letter-spacing:-0.03em;
}
#page-pbj .hhh-step,
#page-hhh .hhh-step,
#page-pal .hhh-step,
#page-cvc .hhh-step{
  border-radius:20px !important;
  background:rgba(255,255,255,0.03) !important;
  border:1px solid rgba(255,255,255,0.1) !important;
  box-shadow:0 16px 40px rgba(0,0,0,0.25);
  transition:transform .28s var(--ease), border-color .28s;
}
#page-pbj .hhh-step:hover,
#page-hhh .hhh-step:hover,
#page-pal .hhh-step:hover,
#page-cvc .hhh-step:hover{
  transform:translateY(-4px);
  border-color:color-mix(in srgb, var(--brand-accent) 45%, transparent) !important;
}
#page-pbj .hhh-feature-band,
#page-hhh .hhh-feature-band,
#page-pal .hhh-feature-band,
#page-cvc .hhh-feature-band{
  border-color:rgba(255,255,255,0.06) !important;
}
#page-pbj .hhh-feature-band:nth-child(even),
#page-hhh .hhh-feature-band:nth-child(even),
#page-pal .hhh-feature-band:nth-child(even),
#page-cvc .hhh-feature-band:nth-child(even){
  background:rgba(255,255,255,0.02) !important;
}
#page-pbj .vol-pin,
#page-hhh .vol-pin,
#page-cvc .vol-pin{
  background:
    radial-gradient(ellipse 60% 80% at 80% 20%, var(--mesh-b), transparent 55%),
    var(--brand-dk);
  position:relative;
}
#page-pbj .vol-pin::after,
#page-hhh .vol-pin::after,
#page-cvc .vol-pin::after{
  content:'';position:absolute;inset:0;pointer-events:none;opacity:0.04;mix-blend-mode:overlay;
  background-image:url("data:image/svg+xml,%3Csvg viewBox='0 0 256 256' xmlns='http://www.w3.org/2000/svg'%3E%3Cfilter id='n'%3E%3CfeTurbulence type='fractalNoise' baseFrequency='0.9' numOctaves='3' stitchTiles='stitch'/%3E%3C/filter%3E%3Crect width='100%25' height='100%25' filter='url(%23n)'/%3E%3C/svg%3E");
}
#page-pbj .vol-pin-visual img,
#page-hhh .vol-pin-visual img,
#page-cvc .vol-pin-visual img{
  padding:10px 10px 14px;border-radius:26px;
  background:linear-gradient(165deg,#2a2a2e,#0c0c0e);
  border:1px solid rgba(255,255,255,0.16);
  box-shadow:0 28px 64px rgba(0,0,0,0.5);
}
/* PAL hero panel — same weight as hub token tile */
#page-pal .pal-hero-visual{justify-self:end;width:100%;max-width:400px;}
#page-pal .pal-brand-stack{
  padding:56px 36px 48px;border-radius:28px;
  background:
    radial-gradient(ellipse 70% 60% at 70% 10%, rgba(232,184,74,0.22), transparent 55%),
    linear-gradient(158deg, #24352c 0%, #0e1712 100%);
  border:1px solid rgba(255,255,255,0.12);
  box-shadow:0 32px 72px rgba(0,0,0,0.5);
  position:relative;overflow:hidden;
}
#page-pal .pal-brand-stack::after{
  content:'';position:absolute;inset:0;pointer-events:none;opacity:0.05;mix-blend-mode:overlay;
  background-image:url("data:image/svg+xml,%3Csvg viewBox='0 0 256 256' xmlns='http://www.w3.org/2000/svg'%3E%3Cfilter id='n'%3E%3CfeTurbulence type='fractalNoise' baseFrequency='0.85' numOctaves='3' stitchTiles='stitch'/%3E%3C/filter%3E%3Crect width='100%25' height='100%25' filter='url(%23n)'/%3E%3C/svg%3E");
}
#page-pal .pal-brand-stack-title{
  font-size:clamp(24px,3vw,30px);letter-spacing:-0.03em;color:#fff;
}
#page-pal .pal-brand-stack img.pal-coin-lg{
  width:112px;height:112px;
  filter:drop-shadow(0 12px 28px rgba(201,162,39,0.5));
}
#page-pal .catalog-cell,
#page-pbj .catalog-cell,
#page-hhh .catalog-cell,
#page-cvc .catalog-cell{
  border-radius:18px !important;
  background:rgba(255,255,255,0.03) !important;
  border:1px solid rgba(255,255,255,0.1) !important;
  transition:transform .28s, border-color .28s;
}
#page-pal .catalog-cell:hover,
#page-pbj .catalog-cell:hover,
#page-hhh .catalog-cell:hover,
#page-cvc .catalog-cell:hover{
  transform:translateY(-3px);
  border-color:color-mix(in srgb, var(--brand-accent) 40%, transparent) !important;
}
@media (max-width:960px){
  #page-pbj .hero,
  #page-hhh .hero,
  #page-pal .hero,
  #page-cvc .hero{min-height:auto;padding:72px 22px 56px;}
  #page-pbj .hero:hover .pbj-shot-center,
  #page-hhh .hero:hover .pbj-shot-center,
  #page-cvc .hero:hover .pbj-shot-center,
  #page-pbj .hero:hover .pbj-shot-side:first-child,
  #page-hhh .hero:hover .pbj-shot-side:first-child,
  #page-cvc .hero:hover .pbj-shot-side:first-child,
  #page-pbj .hero:hover .pbj-shot-side:last-child,
  #page-hhh .hero:hover .pbj-shot-side:last-child,
  #page-cvc .hero:hover .pbj-shot-side:last-child{transform:none;}
  #page-pbj .pbj-shot-center,
  #page-hhh .pbj-shot-center,
  #page-cvc .pbj-shot-center{transform:none;}
  #page-pbj .pstrip,
  #page-hhh .pstrip,
  #page-pal .pstrip,
  #page-cvc .pstrip{padding:16px 20px;justify-content:flex-start;}
}
@media (prefers-reduced-motion:reduce){
  #page-pbj .pbj-shot,
  #page-hhh .pbj-shot,
  #page-cvc .pbj-shot,
  #page-pbj .hhh-step,
  #page-hhh .hhh-step,
  #page-pal .hhh-step,
  #page-cvc .hhh-step{transition:none;}
}
/* ══ END PRODUCT PAGE DYNAMITE ══════════════════════════════════════════════ */

`;

s = s.slice(0, point) + CSS + s.slice(point);

// Upgrade PAL hero coins to inline SVG (no broken img risk)
const palStackOld = `<div class="pal-brand-stack">
        <img class="pal-coin-sm pal-coin-a" src="assets/brand/pal-coin.svg" alt="" aria-hidden="true" width="48" height="48">
        <img class="pal-coin-sm pal-coin-b" src="assets/brand/pal-coin.svg" alt="" aria-hidden="true" width="48" height="48">
        <img class="pal-coin-lg" src="assets/brand/pal-coin.svg" alt="PAL gold token" width="96" height="96">
        <p class="pal-brand-stack-title">Tokens for behavior.<br>Rewards you approve.</p>
        <p class="pal-brand-stack-sub">Parents manage in the app. Kids use the companion from any browser on home Wi&#8209;Fi.</p>
      </div>`;

const coinSvg = (cls, w) => `<svg class="${cls}" viewBox="0 0 64 64" width="${w}" height="${w}" xmlns="http://www.w3.org/2000/svg" aria-hidden="true">
          <defs>
            <radialGradient id="${cls}-face" cx="0.38" cy="0.32" r="0.72">
              <stop offset="0%" stop-color="#E8C547"/><stop offset="45%" stop-color="#C9A227"/><stop offset="100%" stop-color="#9A7A1A"/>
            </radialGradient>
            <linearGradient id="${cls}-rim" x1="0" y1="0" x2="1" y2="1">
              <stop offset="0%" stop-color="#B8921F"/><stop offset="100%" stop-color="#7A6112"/>
            </linearGradient>
          </defs>
          <circle cx="32" cy="32" r="30" fill="url(#${cls}-rim)"/>
          <circle cx="32" cy="32" r="26" fill="url(#${cls}-face)"/>
          <circle cx="32" cy="32" r="22" fill="none" stroke="#B8921F" stroke-width="1.5" opacity="0.45"/>
          <path d="M 18 22 Q 32 12 46 22" fill="none" stroke="#FFF8E0" stroke-width="2.5" stroke-linecap="round" opacity="0.55"/>
        </svg>`;

const palStackNew = `<div class="pal-brand-stack">
        ${coinSvg('pal-coin-sm pal-coin-a', 48)}
        ${coinSvg('pal-coin-sm pal-coin-b', 48)}
        ${coinSvg('pal-coin-lg', 112)}
        <p class="pal-brand-stack-title">Tokens for behavior.<br>Rewards you approve.</p>
        <p class="pal-brand-stack-sub">Parents manage in the app. Kids use the companion from any browser on home Wi&#8209;Fi.</p>
      </div>`;

if (s.includes(palStackOld)) {
  s = s.replace(palStackOld, palStackNew);
  console.log('PAL hero stack upgraded to inline SVG');
} else {
  console.warn('PAL stack HTML not exact-matched — CSS still applied');
}

// CSS for svg.pal-coin-* (was img)
s = s.replace(
  /\.pal-brand-stack img\.pal-coin-lg \{/g,
  '.pal-brand-stack img.pal-coin-lg, .pal-brand-stack svg.pal-coin-lg {'
);
s = s.replace(
  /\.pal-brand-stack img\.pal-coin-sm \{/g,
  '.pal-brand-stack img.pal-coin-sm, .pal-brand-stack svg.pal-coin-sm {'
);

fs.writeFileSync(file, s);
console.log('OK: product pages elevated at', point);
