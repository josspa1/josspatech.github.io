/**
 * Build held localized product pages for PBJ / HHH / CVC / Unscribe.
 * Does not push. Run: node scripts/build-localized-product-pages.mjs
 */
import fs from 'fs';
import path from 'path';
import { fileURLToPath } from 'url';
import { LOCALES, LOCALE_META, STRINGS, FEATURE_FROM_APP } from './localized-product-i18n.mjs';
import { formatVisibleMoneyHtml } from './locale-money-format.mjs';

const __dirname = path.dirname(fileURLToPath(import.meta.url));
const ROOT = path.join(__dirname, '..');

const APPS = {
  pbj: {
    dir: 'pbj',
    clip: 'import-statement',
    howtoId: 'howto-import',
    guideBase: '/videos/pbj/user-guide',
    hasLocaleClips: true,
    primaryChapter: 'import-statement',
  },
  hhh: {
    dir: 'hhh',
    clip: 'identify',
    howtoId: 'howto-identify',
    guideBase: '/videos/hhh/user-guide',
    hasLocaleClips: true,
    primaryChapter: 'identify',
  },
  cvc: {
    dir: 'cvc',
    clip: 'identify',
    howtoId: 'howto-identify',
    guideBase: '/videos/cvc/user-guide',
    hasLocaleClips: true,
    primaryChapter: 'identify',
  },
  unscribe: {
    dir: 'unscribe',
    clip: 'home-monthly',
    howtoId: 'howto-home',
    guideBase: '/videos/unscribe/user-guide',
    hasLocaleClips: false, // only clips/en exists — reported
    primaryChapter: 'home-monthly',
  },
};

const LANG_ORDER = [
  { code: 'en', label: 'English' },
  { code: 'es', label: 'Español' },
  { code: 'zh', label: '中文' },
  { code: 'de', label: 'Deutsch' },
  { code: 'fr', label: 'Français' },
  { code: 'pt', label: 'Português' },
  { code: 'it', label: 'Italiano' },
  { code: 'hi', label: 'हिन्दी' },
];

function productHref(appKey, code) {
  return code === 'en' ? `/${APPS[appKey].dir}/` : `/${APPS[appKey].dir}/${code}/`;
}

function buildLangStrip(appKey, currentCode, ariaLabel) {
  const links = LANG_ORDER.map(({ code, label }) => {
    const href = productHref(appKey, code);
    if (code === currentCode) {
      return `<a href="${href}" aria-current="page">${label}</a>`;
    }
    return `<a href="${href}">${label}</a>`;
  });
  return `<p class="howto-langs" aria-label="${ariaLabel}">\n        ${links.join('\n        ')}\n      </p>`;
}

function escapeRegExp(s) {
  return s.replace(/[.*+?^${}()|[\]\\]/g, '\\$&');
}

// Gaps between EN words: whitespace, entities, any tags, and tiny markers like *
/** Replace only in text nodes (never inside tags / attributes / URLs). */
function mapTextNodes(html, fn) {
  return html.replace(/(^|>)([^<]*)/g, (_, lead, text) => lead + fn(text));
}

const BR_MARK = '\uE010';

/**
 * Unwrap phrasing tags so EN keys match continuous copy.
 * Feature <strong> labels are re-applied after translation.
 */
function unwrapPhrasing(html) {
  let out = html;
  // Drop privacy footnote chrome so "phone. No bank" keys match
  out = out.replace(/<sup><a href="#privacy-note"[^>]*>\*<\/a><\/sup>/g, '');
  out = out.replace(/<sup>\*<\/sup>/g, '');
  out = out.replace(/<\/?(?:strong|em|b)>/gi, '');
  // Keep line breaks as a marker so multi-line headlines still match EN keys
  out = out.replace(/<br\s*\/?>/gi, BR_MARK);
  return out;
}

function restoreBreaks(html) {
  return html.replaceAll(BR_MARK, '<br>');
}

function rewrapPronunciation(html) {
  return html.replace(
    /(pronounced |se pronuncia |ausgesprochen |prononcé |pronuncia-se |读作 |si pronuncia |उच्चारण )(Joss-pah-tech)/gi,
    '$1<em>$2</em>'
  );
}

function rewrapStrongLabels(html, locale) {
  let out = html;
  // Feature bullets: <li>Label — rest  / already translated label before em dash
  out = out.replace(
    /(<li>)([^—–<\n]{1,48})(\s+[—–]\s+)/g,
    '$1<strong>$2</strong>$3'
  );
  // Premium / Pro colon labels at paragraph start
  out = out.replace(
    /(<p>)([^—–<\n:]{3,60}:)(\s+)/g,
    '$1<strong>$2</strong>$3'
  );
  // App locale feature terms if any English strong left
  const feats = FEATURE_FROM_APP?.[locale];
  if (feats) {
    for (const [en, tr] of Object.entries(feats)) {
      if (!tr || tr === en) continue;
      const re = new RegExp(`(<strong>)${escapeRegExp(en)}(</strong>)`, 'g');
      out = out.replace(re, `$1${tr}$2`);
    }
  }
  return out;
}

function applyString(html, en, tr) {
  if (!en || !tr || tr === en) return { html, hit: false };
  // Skip bare single tokens in STRINGS — FEATURE_FROM_APP handles <strong> labels.
  // Prevents Cancel/Start/Import from shredding longer copy.
  if (!/\s/.test(en) && en.length < 28) return { html, hit: false };

  let hit = false;
  const variants = [...new Set([en, en.replace(/'/g, '’'), en.replace(/’/g, "'"), en.replace(/&/g, '&amp;')])];

  let out = html;
  for (const variant of variants) {
    out = mapTextNodes(out, (text) => {
      // Allow BR marker where the EN key has a normal space (headline line breaks)
      const flexible = escapeRegExp(variant).replace(/ /g, `(?: |${BR_MARK})`);
      const re = new RegExp(flexible, 'g');
      if (!re.test(text)) return text;
      hit = true;
      re.lastIndex = 0;
      return text.replace(re, (match) => {
        if (!match.includes(BR_MARK) || tr.includes(BR_MARK) || tr.includes('<br>')) {
          return tr;
        }
        // Preserve a headline line-break near the end (EN often breaks before the last 2 words)
        const parts = tr.trim().split(/\s+/);
        if (parts.length < 3) return tr;
        return `${parts.slice(0, -2).join(' ')}${BR_MARK}${parts.slice(-2).join(' ')}`;
      });
    });
    if (hit) break;
  }
  return { html: out, hit };
}

function translateAttributes(html, locale) {
  const entries = Object.entries(STRINGS)
    .filter(([, map]) => map && map[locale])
    .sort((a, b) => b[0].length - a[0].length);

  return html.replace(/\b(content|aria-label|alt|title)="([^"]*)"/g, (all, attr, val) => {
    if (!val || val.length < 4) return all;
    if (STRINGS[val]?.[locale]) return `${attr}="${STRINGS[val][locale]}"`;
    let v = val;
    for (const [en, map] of entries) {
      const tr = map[locale];
      if (!tr || tr === en) continue;
      if (v.includes(en)) v = v.split(en).join(tr);
    }
    return v === val ? all : `${attr}="${v}"`;
  });
}

function translateHtml(html, locale) {
  // Protect language strip — rewriteHowtoBlock rebuilds it after translate
  const protectedBlocks = [];
  let out = html.replace(/<p class="howto-langs"[\s\S]*?<\/p>/g, (m) => {
    const i = protectedBlocks.length;
    protectedBlocks.push(m);
    return `<!--PROTECT_${i}-->`;
  });

  // Unwrap phrasing only (keep anchors so FAQ/chapter hrefs stay intact)
  out = unwrapPhrasing(out);

  const entries = Object.entries(STRINGS)
    .filter(([, map]) => map && map[locale])
    .sort((a, b) => b[0].length - a[0].length);

  const used = [];
  for (const [en, map] of entries) {
    const tr = map[locale];
    const { html: next, hit } = applyString(out, en, tr);
    if (hit) {
      out = next;
      used.push(en);
    }
  }

  out = translateAttributes(out, locale);
  out = rewrapPronunciation(out);
  out = rewrapStrongLabels(out, locale);
  out = restoreBreaks(out);

  // Collapse any accidental nested howto-all from older builds / partial replaces
  out = out.replace(
    /<a class="howto-all" href="([^"]+)"><a href="[^"]+">([^<]*)<\/a>([^<]*)<\/a>/g,
    '<a class="howto-all" href="$1">$2$3</a>'
  );

  for (let i = 0; i < protectedBlocks.length; i++) {
    out = out.replace(`<!--PROTECT_${i}-->`, protectedBlocks[i]);
  }
  return { html: out, used };
}

function guideEntryChapter(app) {
  if (app.dir === 'pbj' || app.dir === 'unscribe') return 'getting-started';
  return app.primaryChapter;
}

/** Blog posts that have /blog/<slug>/<locale>/ pages (not wave-1 EN-only). */
const LOCALIZED_BLOG_SLUGS = [
  'apps-for-antique-collectors',
  'budget-app-without-bank-login',
  'ynab-alternative-private-budgeting',
  'chrono24-alternative-watch-identification',
  'card-ladder-alternative-collectibles-vault',
  'coin-collection-inventory-software-free',
  'stamp-collection-book-value',
  'watch-service-log-template',
  'document-collection-for-insurance',
];

function retargetGuideLinks(html, app, locale) {
  const base = app.guideBase;
  let out = html;
  if (locale === 'en') return out;
  // FAQ / chapter deep links: /videos/.../user-guide/#chapter → #LOCALE/chapter
  out = out.replace(
    new RegExp(`${escapeRegExp(base)}/#(?![a-z]{2}/)([a-z0-9-]+)`, 'g'),
    `${base}/#${locale}/$1`
  );
  // All chapters root → locale entry hash
  const entry = guideEntryChapter(app);
  out = out.replace(
    new RegExp(`href="${escapeRegExp(base)}/"`, 'g'),
    `href="${base}/#${locale}/${entry}"`
  );
  // Guides / blog index → same-language URLs (leave EN-only wave-1 posts on English path)
  out = out.replace(/href="\/blog\/"/g, `href="/blog/${locale}/"`);
  for (const slug of LOCALIZED_BLOG_SLUGS) {
    out = out.replace(
      new RegExp(`href="/blog/${escapeRegExp(slug)}/"`, 'g'),
      `href="/blog/${slug}/${locale}/"`
    );
  }
  // For-professionals hub → locale twin (PBJ Learn more / footer)
  out = out.replace(/href="\/for-professionals\/"/g, `href="/for-professionals/${locale}/"`);
  return out;
}

function rewriteHowtoBlock(html, appKey, locale) {
  const app = APPS[appKey];
  const aria = locale === 'en' ? 'How-to languages' : 'Product page languages';
  const strip = buildLangStrip(appKey, locale, aria);

  // Replace existing howto-langs block
  let out = html.replace(
    /<p class="howto-langs"[^>]*>[\s\S]*?<\/p>/,
    strip
  );

  // Video clip + poster for locale (Unscribe: keep en, flagged in report)
  const clipLocale = app.hasLocaleClips ? locale : 'en';
  if (locale !== 'en' || app.hasLocaleClips) {
    out = out.replaceAll(
      `/videos/${app.dir}/user-guide/clips/en/${app.clip}.`,
      `/videos/${app.dir}/user-guide/clips/${clipLocale}/${app.clip}.`
    );
  }

  return out;
}

const HREFLANG_MAP = {
  en: 'en',
  es: 'es',
  de: 'de',
  fr: 'fr',
  pt: 'pt',
  zh: 'zh-Hans',
  it: 'it',
  hi: 'hi',
};

function buildProductHreflangBlock(appKey) {
  const app = APPS[appKey];
  const lines = LANG_ORDER.map(({ code }) => {
    const href =
      code === 'en'
        ? `https://josspatech.com/${app.dir}/`
        : `https://josspatech.com/${app.dir}/${code}/`;
    return `<link rel="alternate" hreflang="${HREFLANG_MAP[code]}" href="${href}">`;
  });
  lines.push(`<link rel="alternate" hreflang="x-default" href="https://josspatech.com/${app.dir}/">`);
  return lines.join('\n');
}

function injectProductHreflang(html, appKey) {
  const block = buildProductHreflangBlock(appKey);
  let out = html.replace(
    /(?:<link rel="alternate" hreflang="[^"]*" href="[^"]*">\s*)+/g,
    ''
  );
  if (/<link rel="canonical"/i.test(out)) {
    return out.replace(/(<link rel="canonical"[^>]*>)/i, `$1\n${block}`);
  }
  return out.replace(/<\/head>/i, `${block}\n</head>`);
}

function rewriteHead(html, appKey, locale) {
  const app = APPS[appKey];
  const urlPath = productHref(appKey, locale);
  let out = html;
  if (locale !== 'en') {
    const meta = LOCALE_META[locale];
    out = out.replace(/<html lang="[^"]*">/, `<html lang="${meta.htmlLang}">`);
    out = out.replace(
      /<meta property="og:locale" content="[^"]*">/,
      `<meta property="og:locale" content="${meta.ogLocale}">`
    );
  }
  // JSON-LD / absolute product URL first (English path only), then set canonical/og:url
  if (locale !== 'en') {
    const absEn = `https://josspatech.com/${app.dir}/`;
    const absLoc = `https://josspatech.com${urlPath}`;
    out = out.replaceAll(absEn, absLoc);
  }
  out = out.replace(
    /<link rel="canonical" href="[^"]*">/,
    `<link rel="canonical" href="https://josspatech.com${urlPath}">`
  );
  out = out.replace(
    /<meta property="og:url" content="[^"]*">/,
    `<meta property="og:url" content="https://josspatech.com${urlPath}">`
  );
  return out;
}

function processPage(appKey, locale) {
  const app = APPS[appKey];
  // Always start from English product page on disk
  const src = path.join(ROOT, app.dir, 'index.html');
  let html = fs.readFileSync(src, 'utf8');
  let used = [];

  if (locale !== 'en') {
    // Translate first (howto-preview protected), then stamp locale video + product lang strip
    const translated = translateHtml(html, locale);
    html = translated.html;
    used = translated.used;
    html = rewriteHowtoBlock(html, appKey, locale);
    html = rewriteHead(html, appKey, locale);
    html = retargetGuideLinks(html, app, locale);
    // Locale number/price orthography (visible text only; JSON-LD untouched)
    html = formatVisibleMoneyHtml(html, locale);
  } else {
    html = rewriteHowtoBlock(html, appKey, locale);
    html = rewriteHead(html, appKey, locale);
  }
  html = injectProductHreflang(html, appKey);

  const selfHref = productHref(appKey, locale);
  html = html.replace(
    new RegExp(`href="/${app.dir}/"( aria-current="page")?`),
    `href="${selfHref}" aria-current="page"`
  );

  const outDir =
    locale === 'en' ? path.join(ROOT, app.dir) : path.join(ROOT, app.dir, locale);
  fs.mkdirSync(outDir, { recursive: true });
  const outFile = path.join(outDir, 'index.html');
  fs.writeFileSync(outFile, html, 'utf8');
  return { outFile, usedCount: used.length, used };
}

const report = { pages: [], unscribeVideoGap: true, freshByLocale: {} };

for (const appKey of Object.keys(APPS)) {
  // Update English first (lang strip retarget only + keep English copy)
  const en = processPage(appKey, 'en');
  report.pages.push({ app: appKey, locale: 'en', path: en.outFile.replace(ROOT, '').replace(/\\/g, '/') });

  for (const locale of LOCALES) {
    const r = processPage(appKey, locale);
    const rel = `/${APPS[appKey].dir}/${locale}/`;
    report.pages.push({ app: appKey, locale, url: rel, path: r.outFile });
    if (!report.freshByLocale[locale]) report.freshByLocale[locale] = new Set();
    // Keys used that are NOT in FEATURE_FROM_APP count as fresh page copy
    for (const k of r.used) {
      if (!FEATURE_FROM_APP?.[locale]?.[k]) report.freshByLocale[locale].add(k);
    }
  }
}

// Serialize fresh sets
const freshOut = {};
for (const [loc, set] of Object.entries(report.freshByLocale)) {
  freshOut[loc] = [...set].sort();
}
report.freshByLocale = freshOut;
report.inventory = [];
for (const appKey of Object.keys(APPS)) {
  for (const locale of LOCALES) {
    report.inventory.push(`/${APPS[appKey].dir}/${locale}/`);
  }
}

fs.writeFileSync(
  path.join(ROOT, 'scripts', '_localized-product-pages-report.json'),
  JSON.stringify(
    {
      inventory: report.inventory,
      pageCount: report.inventory.length,
      unscribeLocaleClipsMissing: true,
      freshStringCounts: Object.fromEntries(
        Object.entries(report.freshByLocale).map(([k, v]) => [k, v.length])
      ),
      freshByLocaleSample: Object.fromEntries(
        Object.entries(report.freshByLocale).map(([k, v]) => [k, v.slice(0, 40)])
      ),
    },
    null,
    2
  ),
  'utf8'
);

console.log('Built', report.inventory.length, 'localized pages + updated 4 English pages');
console.log('Inventory:\n' + report.inventory.join('\n'));
console.log('Unscribe locale clips: MISSING (embedded English clips)');
