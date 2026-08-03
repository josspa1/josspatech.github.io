const fs = require('fs');
const path = require('path');
const file = path.join(__dirname, '..', 'index.html');
let s = fs.readFileSync(file, 'utf8');

const hubFig = `<figure class="hub-card-shot hub-card-shot-token" aria-hidden="true">
          <img src="assets/brand/pal-coin.svg" alt="Gold Spanish doubloon" width="120" height="120" loading="lazy">
          <p class="token-caption">Gold doubloon</p>
        </figure>`;

const hubRe = /<figure class="hub-card-shot hub-card-shot-token"[\s\S]*?<\/figure>/;
if (!hubRe.test(s)) {
  console.error('hub figure missing');
  process.exit(1);
}
s = s.replace(hubRe, hubFig);

const stackRe = /<div class="pal-brand-stack">[\s\S]*?<p class="pal-brand-stack-title">/;
if (!stackRe.test(s)) {
  console.error('stack missing');
  process.exit(1);
}
s = s.replace(
  stackRe,
  `<div class="pal-brand-stack">
        <img class="pal-coin-sm pal-coin-a" src="assets/brand/pal-coin.svg" alt="" aria-hidden="true" width="48" height="48">
        <img class="pal-coin-sm pal-coin-b" src="assets/brand/pal-coin.svg" alt="" aria-hidden="true" width="48" height="48">
        <img class="pal-coin-lg" src="assets/brand/pal-coin.svg" alt="Gold Spanish doubloon token" width="120" height="120">
        <p class="pal-brand-stack-title">`
);

// Make token frame show more of the detailed coin
if (!s.includes('hub-card-shot-token img')) {
  s = s.replace(
    '.hub-card-shot-token .token-caption{',
    `#page-company .hub-card-shot-token img{
  width:92%;height:auto;display:block;margin:0 auto;
  filter:drop-shadow(0 10px 22px rgba(201,162,39,0.55));
  aspect-ratio:auto !important;object-fit:contain;padding:0;background:transparent;border-radius:0;
}
.hub-card-shot-token .token-caption{`
  );
}

fs.writeFileSync(file, s);
console.log('OK: doubloon applied');
