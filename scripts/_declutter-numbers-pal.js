/**
 * Remove catalog volume numbering; replace abstract PAL disc with a readable gold token.
 */
const fs = require('fs');
const path = require('path');
const file = path.join(__dirname, '..', 'index.html');
let s = fs.readFileSync(file, 'utf8');

// Hub volume labels
s = s.replace(/\s*<span class="hub-index"[^>]*>Vol\.\s*0\d<\/span>\n?/g, '\n');

// Section numbers on company home
s = s.replace(/\s*<span class="section-num"[^>]*>0\d<\/span>\n?/g, '\n');

// Product breadcrumbs: Catalog · 0N → product short name
s = s.replace(
  /<span>Catalog · 01<\/span>/g,
  '<span>PocketBudJet</span>'
);
s = s.replace(
  /<span>Catalog · 02<\/span>/g,
  '<span>Handy Horology Helper</span>'
);
s = s.replace(
  /<span>Catalog · 03<\/span>/g,
  '<span>Pocket Allowance Ledger</span>'
);
s = s.replace(
  /<span>Catalog · 04<\/span>/g,
  '<span>Curator\'s Vault</span>'
);

// Drop Vol. NN from kickers — keep product name only
s = s.replace(
  /<div class="vol-kicker"><span class="vol-num">Vol\.\s*0\d<\/span><span class="vol-name">/g,
  '<div class="vol-kicker"><span class="vol-name">'
);

// Stop auto-numbering feature cells
s = s.replace(
  /if \(!el\.querySelector\('\.cell-num'\)\) \{\s*n \+= 1;\s*var num = document\.createElement\('span'\);\s*num\.className = 'cell-num';\s*num\.setAttribute\('aria-hidden', 'true'\);\s*num\.textContent = \(n < 10 \? '0' : ''\) \+ n;\s*el\.insertBefore\(num, el\.firstChild\);\s*\}/m,
  '/* catalog cell numbers removed — product pages are not a numbered catalog */'
);

// Hide any leftover numbers via CSS
const cssHook = '/* ══ PRODUCT PAGE DYNAMITE';
const hideCSS = `/* ══ Declutter catalog numbering ═══════════════════════════════════════════ */
.hub-index,.section-num,.vol-num,.catalog-cell .cell-num{display:none !important;}
#page-company .section-lead{gap:0;}
.vol-kicker{margin-bottom:14px;}
.hub-card-shot-token{flex-direction:column;gap:10px;}
.hub-card-shot-token .token-caption{
  font-family:var(--mono,'IBM Plex Mono',monospace);
  font-size:10px;font-weight:600;letter-spacing:0.18em;text-transform:uppercase;
  color:rgba(232,184,74,0.85);text-align:center;margin:0;
}
`;
if (!s.includes('Declutter catalog numbering')) {
  const i = s.indexOf(cssHook);
  if (i < 0) {
    console.error('CSS hook missing');
    process.exit(1);
  }
  s = s.slice(0, i) + hideCSS + s.slice(i);
}

// Clearer gold token for hub PAL card
const clearToken = `<figure class="hub-card-shot hub-card-shot-token" aria-hidden="true">
          <svg viewBox="0 0 120 120" width="120" height="120" xmlns="http://www.w3.org/2000/svg" role="img" aria-label="Gold token">
            <defs>
              <radialGradient id="hub-pal-face" cx="0.35" cy="0.3" r="0.75">
                <stop offset="0%" stop-color="#FFE08A"/>
                <stop offset="40%" stop-color="#E8B84A"/>
                <stop offset="100%" stop-color="#9A7A1A"/>
              </radialGradient>
              <linearGradient id="hub-pal-rim" x1="0" y1="0" x2="1" y2="1">
                <stop offset="0%" stop-color="#F0D070"/>
                <stop offset="100%" stop-color="#7A6112"/>
              </linearGradient>
            </defs>
            <circle cx="60" cy="60" r="56" fill="url(#hub-pal-rim)"/>
            <circle cx="60" cy="60" r="48" fill="url(#hub-pal-face)"/>
            <circle cx="60" cy="60" r="42" fill="none" stroke="#B8921F" stroke-width="2" opacity="0.55"/>
            <path d="M38 40 Q60 28 82 40" fill="none" stroke="#FFF8E0" stroke-width="3" stroke-linecap="round" opacity="0.65"/>
            <!-- star = reward token -->
            <path d="M60 42l5.2 10.6 11.7 1.7-8.45 8.2 2 11.6L60 68.6l-10.45 5.5 2-11.6-8.45-8.2 11.7-1.7z" fill="#6B5210" opacity="0.85"/>
            <text x="60" y="92" text-anchor="middle" font-family="Manrope,Arial,sans-serif" font-size="11" font-weight="800" letter-spacing="2" fill="#6B5210">TOKEN</text>
          </svg>
          <p class="token-caption">Gold token</p>
        </figure>`;

const tokenRe = /<figure class="hub-card-shot hub-card-shot-token"[\s\S]*?<\/figure>/;
if (!tokenRe.test(s)) {
  console.error('hub PAL token figure not found');
  process.exit(1);
}
s = s.replace(tokenRe, clearToken);

// Update brand SVG asset too
const brandSvg = `<svg xmlns="http://www.w3.org/2000/svg" width="120" height="120" viewBox="0 0 120 120" role="img" aria-label="PAL gold token">
  <defs>
    <radialGradient id="pal-coin-face" cx="0.35" cy="0.3" r="0.75">
      <stop offset="0%" stop-color="#FFE08A"/>
      <stop offset="40%" stop-color="#E8B84A"/>
      <stop offset="100%" stop-color="#9A7A1A"/>
    </radialGradient>
    <linearGradient id="pal-coin-rim" x1="0" y1="0" x2="1" y2="1">
      <stop offset="0%" stop-color="#F0D070"/>
      <stop offset="100%" stop-color="#7A6112"/>
    </linearGradient>
  </defs>
  <circle cx="60" cy="60" r="56" fill="url(#pal-coin-rim)"/>
  <circle cx="60" cy="60" r="48" fill="url(#pal-coin-face)"/>
  <circle cx="60" cy="60" r="42" fill="none" stroke="#B8921F" stroke-width="2" opacity="0.55"/>
  <path d="M38 40 Q60 28 82 40" fill="none" stroke="#FFF8E0" stroke-width="3" stroke-linecap="round" opacity="0.65"/>
  <path d="M60 42l5.2 10.6 11.7 1.7-8.45 8.2 2 11.6L60 68.6l-10.45 5.5 2-11.6-8.45-8.2 11.7-1.7z" fill="#6B5210" opacity="0.85"/>
  <text x="60" y="92" text-anchor="middle" font-family="Manrope,Arial,sans-serif" font-size="11" font-weight="800" letter-spacing="2" fill="#6B5210">TOKEN</text>
</svg>
`;
fs.writeFileSync(path.join(__dirname, '..', 'assets', 'brand', 'pal-coin.svg'), brandSvg);

// Upgrade PAL page hero stack coins to the clearer design (replace the three inline svgs block)
const heroToken = `<svg class="pal-coin-lg" viewBox="0 0 120 120" width="112" height="112" xmlns="http://www.w3.org/2000/svg" aria-hidden="true">
          <defs>
            <radialGradient id="pal-hero-face" cx="0.35" cy="0.3" r="0.75">
              <stop offset="0%" stop-color="#FFE08A"/><stop offset="40%" stop-color="#E8B84A"/><stop offset="100%" stop-color="#9A7A1A"/>
            </radialGradient>
            <linearGradient id="pal-hero-rim" x1="0" y1="0" x2="1" y2="1">
              <stop offset="0%" stop-color="#F0D070"/><stop offset="100%" stop-color="#7A6112"/>
            </linearGradient>
          </defs>
          <circle cx="60" cy="60" r="56" fill="url(#pal-hero-rim)"/>
          <circle cx="60" cy="60" r="48" fill="url(#pal-hero-face)"/>
          <circle cx="60" cy="60" r="42" fill="none" stroke="#B8921F" stroke-width="2" opacity="0.55"/>
          <path d="M38 40 Q60 28 82 40" fill="none" stroke="#FFF8E0" stroke-width="3" stroke-linecap="round" opacity="0.65"/>
          <path d="M60 42l5.2 10.6 11.7 1.7-8.45 8.2 2 11.6L60 68.6l-10.45 5.5 2-11.6-8.45-8.2 11.7-1.7z" fill="#6B5210" opacity="0.85"/>
          <text x="60" y="92" text-anchor="middle" font-family="Manrope,Arial,sans-serif" font-size="11" font-weight="800" letter-spacing="2" fill="#6B5210">TOKEN</text>
        </svg>`;

const heroSmall = (id) => `<svg class="pal-coin-sm ${id}" viewBox="0 0 120 120" width="48" height="48" xmlns="http://www.w3.org/2000/svg" aria-hidden="true">
          <defs>
            <radialGradient id="${id}-face" cx="0.35" cy="0.3" r="0.75">
              <stop offset="0%" stop-color="#FFE08A"/><stop offset="40%" stop-color="#E8B84A"/><stop offset="100%" stop-color="#9A7A1A"/>
            </radialGradient>
            <linearGradient id="${id}-rim" x1="0" y1="0" x2="1" y2="1">
              <stop offset="0%" stop-color="#F0D070"/><stop offset="100%" stop-color="#7A6112"/>
            </linearGradient>
          </defs>
          <circle cx="60" cy="60" r="56" fill="url(#${id}-rim)"/>
          <circle cx="60" cy="60" r="48" fill="url(#${id}-face)"/>
          <path d="M60 42l5.2 10.6 11.7 1.7-8.45 8.2 2 11.6L60 68.6l-10.45 5.5 2-11.6-8.45-8.2 11.7-1.7z" fill="#6B5210" opacity="0.85"/>
        </svg>`;

const stackRe = /<div class="pal-brand-stack">[\s\S]*?<p class="pal-brand-stack-title">/;
if (stackRe.test(s)) {
  s = s.replace(
    stackRe,
    `<div class="pal-brand-stack">
        ${heroSmall('pal-coin-a')}
        ${heroSmall('pal-coin-b')}
        ${heroToken}
        <p class="pal-brand-stack-title">`
  );
  console.log('PAL hero tokens updated');
}

fs.writeFileSync(file, s);
console.log('OK: numbering decluttered + PAL token clarified');
