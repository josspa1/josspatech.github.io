/**
 * Part 3 — home language pills + in-language round-robin with micro-descriptions.
 */
const fs = require('fs');
const path = require('path');

const ROOT = path.join(__dirname, '..');
const LANGS = ['es', 'zh', 'de', 'fr', 'pt', 'it', 'hi'];
const LANG_LABEL = {
  es: 'Español',
  zh: '中文',
  de: 'Deutsch',
  fr: 'Français',
  pt: 'Português',
  it: 'Italiano',
  hi: 'हिन्दी',
};
const APPS = [
  { id: 'pbj', name: 'PocketBudJet', en: 'Budgeting app — know where your money went' },
  { id: 'hhh', name: 'Handy Horology Helper', en: 'Clock and watch app' },
  { id: 'cvc', name: "Curator's Vault: Classics", short: "Curator's Vault", en: 'Collecting app — coins, stamps, cards, paper money, lighters' },
  { id: 'unscribe', name: 'Unscribe', en: 'Keeps track of your subscriptions' },
];

const DESC = {
  en: {
    pbj: 'Budgeting app — know where your money went',
    hhh: 'Clock and watch app',
    cvc: 'Collecting app — coins, stamps, cards, paper money, lighters',
    unscribe: 'Keeps track of your subscriptions',
  },
  es: {
    pbj: 'App de presupuesto — sabe a dónde fue tu dinero',
    hhh: 'App de relojes y clocks',
    cvc: 'App de coleccionismo — monedas, sellos, cartas, billetes, mecheros',
    unscribe: 'Lleva el control de tus suscripciones',
  },
  zh: {
    pbj: '预算应用 — 弄清钱花到哪里',
    hhh: '钟表应用',
    cvc: '收藏应用 — 钱币、邮票、卡牌、纸币、打火机',
    unscribe: '跟踪你的订阅',
  },
  de: {
    pbj: 'Budget-App — wissen, wohin das Geld ging',
    hhh: 'Uhren- und Clock-App',
    cvc: 'Sammler-App — Münzen, Briefmarken, Karten, Papiergeld, Feuerzeuge',
    unscribe: 'Behält deine Abos im Blick',
  },
  fr: {
    pbj: 'App de budget — savoir où est passé l’argent',
    hhh: 'App montres et clocks',
    cvc: 'App de collection — pièces, timbres, cartes, billets, briquets',
    unscribe: 'Suit vos abonnements',
  },
  pt: {
    pbj: 'App de orçamento — saiba para onde foi o dinheiro',
    hhh: 'App de relógios e clocks',
    cvc: 'App de coleção — moedas, selos, cartas, notas, isqueiros',
    unscribe: 'Acompanha as suas subscrições',
  },
  it: {
    pbj: 'App di budget — sappi dove sono andati i soldi',
    hhh: 'App per orologi e clocks',
    cvc: 'App da collezione — monete, francobolli, carte, banconote, accendini',
    unscribe: ' Tiene traccia dei tuoi abbonamenti',
  },
  hi: {
    pbj: 'बजट ऐप — जानें पैसे कहाँ गए',
    hhh: 'घड़ी और क्लॉक ऐप',
    cvc: 'कलेक्टिंग ऐप — सिक्के, टिकट, कार्ड, नोट, लाइटर',
    unscribe: 'आपकी सदस्यताएँ ट्रैक करता है',
  },
};

// Fix Italian typo space
DESC.it.unscribe = 'Tiene traccia dei tuoi abbonamenti';
// Better HHH/CVC short lines without English "clocks" loan where awkward
DESC.es.hhh = 'App de relojes';
DESC.de.hhh = 'Uhren-App';
DESC.fr.hhh = 'App montres et pendules';
DESC.pt.hhh = 'App de relógios';
DESC.it.hhh = 'App per orologi';

const SUMMARY = {
  en: 'More JosspaTech apps',
  es: 'Más apps de JosspaTech',
  zh: '更多 JosspaTech 应用',
  de: 'Weitere JosspaTech-Apps',
  fr: 'Plus d’apps JosspaTech',
  pt: 'Mais apps JosspaTech',
  it: 'Altre app JosspaTech',
  hi: 'और JosspaTech ऐप्स',
};

function pillsHtml() {
  const links = LANGS.map(
    (l) =>
      `<a class="lang-pill" href="/pbj/${l}/" lang="${l === 'zh' ? 'zh-Hans' : l}">${LANG_LABEL[l]}</a>`
  ).join('\n      ');
  return `<nav class="lang-pills" aria-label="Languages">\n      ${links}\n    </nav>`;
}

function buildAppsNav(lang, currentId) {
  const descs = DESC[lang] || DESC.en;
  const items = APPS.map((app) => {
    const href = lang === 'en' ? `/${app.id}/` : `/${app.id}/${lang}/`;
    const cur = app.id === currentId ? ' aria-current="page"' : '';
    const label = app.id === 'cvc' && lang !== 'en' ? (app.short || app.name) : app.name;
    if (lang === 'en') {
      return `        <a href="${href}"${cur}>${label}</a>`;
    }
    return `        <a href="${href}"${cur}><span class="app-name">${label}</span><span class="app-desc">${descs[app.id]}</span></a>`;
  }).join('\n');
  // Keep PAL as English-only escape if present historically — omit from required round-robin (4 products)
  return `<details class="apps-more">
      <summary>${SUMMARY[lang] || SUMMARY.en}</summary>
      <nav class="apps" aria-label="JosspaTech apps">
${items}
      </nav>
    </details>`;
}

const APPS_MORE_RE =
  /<details class="apps-more">[\s\S]*?<\/details>/;

function patchProduct(file, lang, currentId) {
  if (!fs.existsSync(file)) return false;
  let html = fs.readFileSync(file, 'utf8');
  if (!APPS_MORE_RE.test(html)) {
    console.warn('no apps-more:', path.relative(ROOT, file));
    return false;
  }
  const next = html.replace(APPS_MORE_RE, buildAppsNav(lang, currentId));
  if (next === html) return false;
  fs.writeFileSync(file, next, 'utf8');
  return true;
}

// CSS for pills + app-desc
const cssPath = path.join(ROOT, 'assets', 'product-landing.css');
let css = fs.readFileSync(cssPath, 'utf8');
if (!css.includes('.app-desc')) {
  css += `
/* In-language round-robin micro-descriptions */
.apps a {
  display: flex;
  flex-direction: column;
  gap: 0.1rem;
  line-height: 1.25;
}
.apps .app-name { font-weight: 600; }
.apps .app-desc {
  font-size: 0.78em;
  font-weight: 400;
  opacity: 0.8;
  max-width: 18rem;
}
`;
  fs.writeFileSync(cssPath, css, 'utf8');
  console.log('patched product-landing.css');
}

// Home page pills — index.html may use different CSS; add styles inline in head or site CSS
const indexPath = path.join(ROOT, 'index.html');
let index = fs.readFileSync(indexPath, 'utf8');
const pills = pillsHtml();

if (!index.includes('class="lang-pills"')) {
  // Header: after nav-links / before hamburger
  if (index.includes('<div class="nav-links">')) {
    index = index.replace(
      /(<div class="nav-links">[\s\S]*?<\/div>\s*)(<button class="nav-hamburger")/,
      `$1${pills}\n  $2`
    );
  }
  // Footer: before footer-bottom or inside footer-top
  if (index.includes('<div class="footer-bottom">')) {
    index = index.replace(
      '<div class="footer-bottom">',
      `${pills}\n  <div class="footer-bottom">`
    );
  }
  // Quiet pill styles in index
  if (!index.includes('.lang-pills{')) {
    index = index.replace(
      '</style>',
      `.lang-pills{display:flex;flex-wrap:wrap;gap:0.35rem 0.45rem;align-items:center;margin:0.55rem 0 0.25rem;opacity:0.72}
.lang-pills a.lang-pill{font-size:11px;line-height:1.2;padding:0.22rem 0.55rem;border:1px solid rgba(240,192,64,0.28);border-radius:999px;color:rgba(255,255,255,0.72);text-decoration:none;letter-spacing:0.01em}
.lang-pills a.lang-pill:hover{color:var(--gold);border-color:rgba(240,192,64,0.55);opacity:1}
nav.site-nav .lang-pills, .site-nav .lang-pills{margin-left:0.75rem;margin-top:0}
.site-footer .lang-pills{margin:0.75rem 0 0.5rem;opacity:0.55}
.site-footer .lang-pills a.lang-pill{color:rgba(255,255,255,0.45);border-color:rgba(255,255,255,0.18)}
.site-footer .lang-pills a.lang-pill:hover{color:var(--gold);border-color:rgba(240,192,64,0.4)}
</style>`
    );
  }
  fs.writeFileSync(indexPath, index, 'utf8');
  console.log('patched index.html language pills');
} else {
  console.log('index.html already has lang-pills');
}

let n = 0;
for (const app of APPS) {
  const enFile = path.join(ROOT, app.id, 'index.html');
  if (patchProduct(enFile, 'en', app.id)) {
    n++;
    console.log('EN', app.id);
  }
  for (const lang of LANGS) {
    const f = path.join(ROOT, app.id, lang, 'index.html');
    if (patchProduct(f, lang, app.id)) {
      n++;
      console.log(lang, app.id);
    }
  }
}
console.log('patched product pages:', n);
