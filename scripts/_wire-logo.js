const fs = require('fs');
const path = require('path');
const file = path.join(__dirname, '..', 'index.html');
let s = fs.readFileSync(file, 'utf8');

// Favicon + apple touch
if (!s.includes('josspatech-mark-app.svg')) {
  s = s.replace(
    '<title>JosspaTech — Mobile Software</title>',
    `<title>JosspaTech — Mobile Software</title>
<link rel="icon" href="assets/brand/josspatech-mark-app.svg" type="image/svg+xml">
<link rel="apple-touch-icon" href="assets/brand/josspatech-mark-app.svg">`
  );
}

// Nav mark → production logo mark
const navSvgRe = /<svg class="nav-spade"[\s\S]*?<\/svg>/;
if (!navSvgRe.test(s)) {
  console.error('nav svg missing');
  process.exit(1);
}
s = s.replace(
  navSvgRe,
  `<img class="nav-spade" src="assets/brand/josspatech-mark.svg" width="36" height="36" alt="" aria-hidden="true">`
);

// Hub hero mark → stacked logo mark (icon only, brand type stays as hero-brand)
const hubMarkRe = /<div class="hub-mark" aria-hidden="true">\s*<svg[\s\S]*?<\/svg>\s*<\/div>/;
if (!hubMarkRe.test(s)) {
  console.error('hub mark missing');
  process.exit(1);
}
s = s.replace(
  hubMarkRe,
  `<div class="hub-mark" aria-hidden="true">
      <img src="assets/brand/josspatech-mark.svg" width="96" height="96" alt="">
    </div>`
);

// CSS polish for img-based marks
if (!s.includes('/* logo system wire */')) {
  s = s.replace(
    '.hub-mark svg{width:100%;height:100%;display:block;filter:drop-shadow(0 8px 28px rgba(93,173,226,0.25));}',
    `.hub-mark svg,.hub-mark img{width:100%;height:100%;display:block;filter:drop-shadow(0 8px 28px rgba(93,173,226,0.25));}
img.nav-spade{width:36px;height:36px;display:block;flex-shrink:0;filter:drop-shadow(0 2px 8px rgba(93,173,226,0.25));}
/* logo system wire */`
  );
}

fs.writeFileSync(file, s);
console.log('OK: logo wired into site');
