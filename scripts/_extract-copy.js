const fs = require('fs');
const { execSync } = require('child_process');

function show(ref) {
  return execSync(`git show ${ref}:index.html`, { encoding: 'utf8', maxBuffer: 20 * 1024 * 1024 });
}

function between(html, startMarker, endMarker) {
  const i = html.indexOf(startMarker);
  if (i < 0) return null;
  const j = html.indexOf(endMarker, i);
  if (j < 0) return null;
  return html.slice(i, j);
}

function firstMatch(html, re) {
  const m = html.match(re);
  return m ? m[0] : null;
}

const liked = show('655858b'); // hub copy Joe likely liked
const preVolume = show('53d8ea7'); // product heroes before volume rewrite shortened them

const out = {
  hubHeroActions: firstMatch(
    liked,
    /<div class="hero-actions">[\s\S]*?<\/div>\s*<\/div>\s*<\/section>/
  ),
  hubHeroSub: firstMatch(liked, /<p class="hero-sub">\s*[\s\S]*?<\/p>/),
  hubCtaPbj: firstMatch(liked, /Open PocketBudJet[\s\S]*?<\/div>/),
  sectionLead: firstMatch(liked, /<div class="section-lead">[\s\S]*?<\/div>/),
  productsBlock: between(liked, '<!-- ══ PRODUCTS ══ -->', '<!-- ══ QUOTE BAR ══ -->'),
  pbjHeroSub: firstMatch(preVolume, /id="page-pbj"[\s\S]*?<p class="hero-sub">[\s\S]*?<\/p>/),
};

// Cleaner product hero-sub extraction
function heroSubOnPage(html, pageId) {
  const start = html.indexOf(`id="${pageId}"`);
  if (start < 0) return null;
  const chunk = html.slice(start, start + 8000);
  const m = chunk.match(/<p class="hero-sub"[^>]*>[\s\S]*?<\/p>/);
  return m ? m[0] : null;
}

function heroActsOnPage(html, pageId) {
  const start = html.indexOf(`id="${pageId}"`);
  if (start < 0) return null;
  const chunk = html.slice(start, start + 12000);
  const m = chunk.match(/<div class="hero-acts"[^>]*>[\s\S]*?<\/div>/);
  return m ? m[0] : null;
}

['page-pbj', 'page-hhh', 'page-pal', 'page-cvc'].forEach((id) => {
  out[id + '-sub'] = heroSubOnPage(preVolume, id);
  out[id + '-acts'] = heroActsOnPage(preVolume, id);
});

// Hub CTAs / taglines from liked
function hubCardBits(html) {
  const start = html.indexOf('<!-- ══ PRODUCTS ══ -->');
  const end = html.indexOf('<!-- ══ QUOTE BAR ══ -->');
  return html.slice(start, end);
}

out.productsLiked = hubCardBits(liked);
out.hubOpenCatalog = firstMatch(
  fs.readFileSync('index.html', 'utf8'),
  /Open the catalog[\s\S]{0,200}/
);

fs.writeFileSync('scripts/_copy-snapshot.json', JSON.stringify({
  hubHeroSub: out.hubHeroSub,
  'page-pbj-sub': out['page-pbj-sub'],
  'page-hhh-sub': out['page-hhh-sub'],
  'page-pal-sub': out['page-pal-sub'],
  'page-cvc-sub': out['page-cvc-sub'],
  'page-pbj-acts': out['page-pbj-acts'],
  'page-hhh-acts': out['page-hhh-acts'],
  productsLen: out.productsLiked && out.productsLiked.length,
}, null, 2));

console.log(JSON.stringify({
  hubHeroSub: out.hubHeroSub,
  pbj: out['page-pbj-sub'],
  hhh: out['page-hhh-sub'],
  pal: out['page-pal-sub'],
  cvc: out['page-cvc-sub'],
  hhhActs: out['page-hhh-acts'] && out['page-hhh-acts'].slice(0, 400),
}, null, 2));
