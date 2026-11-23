/**
 * Localize blog posts + hubs (es/de/fr/pt/zh/it/hi).
 * Run: node scripts/build-localized-blog-hub-pages.mjs
 * Requires: scripts/localized-blog-hub-i18n.mjs (from assemble-blog-hub-i18n.mjs)
 */
import fs from 'fs';
import path from 'path';
import { fileURLToPath } from 'url';
import { LOCALE_META } from './localized-product-i18n.mjs';
import { formatVisibleMoneyHtml } from './locale-money-format.mjs';
import { LOCALES, STRINGS, FEATURE_FROM_APP } from './localized-blog-hub-i18n.mjs';

const __dirname = path.dirname(fileURLToPath(import.meta.url));
const ROOT = path.join(__dirname, '..');
const BR_MARK = '\uE010';

const POSTS = [
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

const PAGES = [
  ...POSTS.map((slug) => ({
    key: `blog/${slug}`,
    enPath: path.join(ROOT, 'blog', slug, 'index.html'),
    outRel: (loc) => path.join('blog', slug, loc),
    enUrl: `/blog/${slug}/`,
    locUrl: (loc) => `/blog/${slug}/${loc}/`,
  })),
  {
    key: 'blog',
    enPath: path.join(ROOT, 'blog', 'index.html'),
    outRel: (loc) => path.join('blog', loc),
    enUrl: '/blog/',
    locUrl: (loc) => `/blog/${loc}/`,
    isBlogIndex: true,
  },
  {
    key: 'for-professionals',
    enPath: path.join(ROOT, 'for-professionals', 'index.html'),
    outRel: (loc) => path.join('for-professionals', loc),
    enUrl: '/for-professionals/',
    locUrl: (loc) => `/for-professionals/${loc}/`,
  },
  {
    key: 'how-to',
    enPath: path.join(ROOT, 'how-to', 'index.html'),
    outRel: (loc) => path.join('how-to', loc),
    enUrl: '/how-to/',
    locUrl: (loc) => `/how-to/${loc}/`,
  },
  {
    key: 'how-to/faq',
    enPath: path.join(ROOT, 'how-to', 'faq', 'index.html'),
    outRel: (loc) => path.join('how-to', 'faq', loc),
    enUrl: '/how-to/faq/',
    locUrl: (loc) => `/how-to/faq/${loc}/`,
  },
];

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

/** Paths that get /<locale>/ appended (longest first). Homepage and legal stay EN. */
const LOCALIZED_HREFS = [
  ...POSTS.map((s) => `/blog/${s}/`),
  '/for-professionals/',
  '/how-to/faq/',
  '/how-to/',
  '/blog/',
  '/pbj/',
  '/hhh/',
  '/cvc/',
  '/unscribe/',
];

function escapeRegExp(s) {
  return s.replace(/[.*+?^${}()|[\]\\]/g, '\\$&');
}

function buildLangStrip(page, currentCode) {
  const links = LANG_ORDER.map(({ code, label }) => {
    const href = code === 'en' ? page.enUrl : page.locUrl(code);
    const cur = code === currentCode ? ' aria-current="page"' : '';
    return `<a href="${href}"${cur}>${label}</a>`;
  });
  return `<p class="howto-langs blog-langs" aria-label="Languages">\n        ${links.join('\n        ')}\n      </p>`;
}

function insertLangStrip(html, strip) {
  if (/class="howto-langs/.test(html)) {
    return html.replace(/<p class="howto-langs[^"]*"[^>]*>[\s\S]*?<\/p>/, strip);
  }
  if (/<\/h1>/.test(html)) {
    return html.replace(/<\/h1>/, `</h1>\n    ${strip}`);
  }
  // Hub hero: after hero h1
  if (/<div class="hero"[\s\S]*?<\/h1>/.test(html)) {
    return html.replace(/(<div class="hero"[\s\S]*?<\/h1>)/, `$1\n    ${strip}`);
  }
  return html.replace(/<main[^>]*>/, (m) => `${m}\n    ${strip}`);
}

function mapTextNodes(html, fn) {
  return html.replace(/(^|>)([^<]*)/g, (_, lead, text) => lead + fn(text));
}

function unwrapPhrasing(html) {
  let out = html;
  out = out.replace(/<\/?(?:strong|em|b)>/gi, '');
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
  out = out.replace(
    /(<li>)([^—–<\n]{1,48})(\s+[—–]\s+)/g,
    '$1<strong>$2</strong>$3'
  );
  out = out.replace(
    /(<p>)([^—–<\n:]{3,60}:)(\s+)/g,
    '$1<strong>$2</strong>$3'
  );
  const feats = FEATURE_FROM_APP?.[locale];
  if (feats) {
    for (const [en, tr] of Object.entries(feats)) {
      if (!tr || tr === en) continue;
      out = out.replace(
        new RegExp(`(<strong>)${escapeRegExp(en)}(</strong>)`, 'g'),
        `$1${tr}$2`
      );
    }
  }
  return out;
}

function applyString(html, en, tr) {
  if (!en || !tr || tr === en) return { html, hit: false };
  // Short tokens: only replace when the whole text node equals the key
  // (table cells / labels). Avoid shredding longer copy.
  const shortBare = !/\s/.test(en) && en.length < 28;

  let hit = false;
  const variants = [
    ...new Set([en, en.replace(/'/g, '’'), en.replace(/’/g, "'"), en.replace(/&/g, '&amp;')]),
  ];

  let out = html;
  for (const variant of variants) {
    out = mapTextNodes(out, (text) => {
      if (shortBare) {
        if (text === variant || text.trim() === variant) {
          hit = true;
          return text === variant ? tr : text.replace(variant, tr);
        }
        return text;
      }
      const flexible = escapeRegExp(variant).replace(/ /g, `(?: |${BR_MARK})`);
      const re = new RegExp(flexible, 'g');
      if (!re.test(text)) return text;
      hit = true;
      re.lastIndex = 0;
      return text.replace(re, (match) => {
        if (!match.includes(BR_MARK) || tr.includes(BR_MARK) || tr.includes('<br>')) {
          return tr;
        }
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
  const protectedBlocks = [];
  let out = html.replace(/<p class="howto-langs[^"]*"[^>]*>[\s\S]*?<\/p>/g, (m) => {
    const i = protectedBlocks.length;
    protectedBlocks.push(m);
    return `<!--PROTECT_${i}-->`;
  });

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

  for (let i = 0; i < protectedBlocks.length; i++) {
    out = out.replace(`<!--PROTECT_${i}-->`, protectedBlocks[i]);
  }
  return { html: out, used };
}

function rewriteHead(html, page, locale) {
  const meta = LOCALE_META[locale];
  const urlPath = page.locUrl(locale);
  let out = html;
  out = out.replace(/<html lang="[^"]*">/, `<html lang="${meta.htmlLang}">`);
  if (/og:locale/.test(out)) {
    out = out.replace(
      /<meta property="og:locale" content="[^"]*">/,
      `<meta property="og:locale" content="${meta.ogLocale}">`
    );
  } else {
    out = out.replace(
      /<meta property="og:type"/,
      `<meta property="og:locale" content="${meta.ogLocale}">\n<meta property="og:type"`
    );
  }
  // Absolute EN URLs in JSON-LD / body before canonical rewrite
  const absEn = `https://josspatech.com${page.enUrl}`;
  const absLoc = `https://josspatech.com${urlPath}`;
  out = out.replaceAll(absEn, absLoc);
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

function alreadyLocaleHref(href, locale) {
  return new RegExp(`/${locale}/(?:$|#|\\?)`).test(href);
}

function retargetInternalLinks(html, locale) {
  let out = html;
  const prefixes = [...LOCALIZED_HREFS].sort((a, b) => b.length - a.length);
  for (const pre of prefixes) {
    // href="/pbj/" → href="/pbj/es/" ; skip if already /pbj/es/
    const re = new RegExp(`href="${escapeRegExp(pre)}(?![a-z]{2}/)`, 'g');
    out = out.replace(re, `href="${pre}${locale}/`);
  }
  // Absolute product URLs
  for (const app of ['pbj', 'hhh', 'cvc', 'unscribe']) {
    out = out.replace(
      new RegExp(`https://josspatech\\.com/${app}/(?![a-z]{2}/)`, 'g'),
      `https://josspatech.com/${app}/${locale}/`
    );
  }
  // Video guide entry (English root only) → locale folder if present pattern /videos/*/user-guide/
  // Keep existing /videos/.../zh/ etc. untouched (alreadyLocale).
  out = out.replace(
    /href="(\/videos\/(?:pbj|hhh|cvc|unscribe|pal)\/user-guide)\/"(?![a-z])/g,
    (_m, base) => `href="${base}/${locale}/"`
  );
  // FAQ chapter hashes on product video guides: /#chapter → /#locale/chapter when linking from hubs
  out = out.replace(
    /href="(\/videos\/(?:pbj|hhh|cvc|unscribe)\/user-guide)\/#(?![a-z]{2}\/)([a-z0-9-]+)"/g,
    (_m, base, ch) => `href="${base}/#${locale}/${ch}"`
  );
  void alreadyLocaleHref;
  return out;
}

function localizeBlogIndexScript(html, locale) {
  return html
    .replace("fetch('/blog/posts.json'", `fetch('/blog/posts-${locale}.json'`)
    .replace(
      'a.href = p.path;',
      `a.href = (p.path || '').replace(/\\/$/, '') + '/${locale}/';`
    );
}

function processPage(page, locale) {
  let html = fs.readFileSync(page.enPath, 'utf8');
  // Strip any prior EN lang strip so translate starts from clean EN (we re-add after)
  html = html.replace(/<p class="howto-langs blog-langs"[^>]*>[\s\S]*?<\/p>\n?/g, '');

  const { html: translated, used } = translateHtml(html, locale);
  html = translated;
  html = insertLangStrip(html, buildLangStrip(page, locale));
  html = rewriteHead(html, page, locale);
  html = retargetInternalLinks(html, locale);
  if (page.isBlogIndex) html = localizeBlogIndexScript(html, locale);
  html = formatVisibleMoneyHtml(html, locale);

  const outDir = path.join(ROOT, page.outRel(locale));
  fs.mkdirSync(outDir, { recursive: true });
  const outFile = path.join(outDir, 'index.html');
  fs.writeFileSync(outFile, html, 'utf8');
  return { outFile, used: used.length };
}

function buildLocalePostsJson(locale) {
  const en = JSON.parse(fs.readFileSync(path.join(ROOT, 'blog', 'posts.json'), 'utf8'));
  const out = en.map((p) => ({
    ...p,
    title: STRINGS[p.title]?.[locale] || p.title,
    excerpt: STRINGS[p.excerpt]?.[locale] || p.excerpt,
  }));
  fs.writeFileSync(
    path.join(ROOT, 'blog', `posts-${locale}.json`),
    `${JSON.stringify(out, null, 2)}\n`
  );
}

function addLangStripToEnglish(page) {
  let html = fs.readFileSync(page.enPath, 'utf8');
  html = html.replace(/<p class="howto-langs blog-langs"[^>]*>[\s\S]*?<\/p>\n?/g, '');
  html = insertLangStrip(html, buildLangStrip(page, 'en'));
  fs.writeFileSync(page.enPath, html, 'utf8');
}

function retargetPbjProfessionals() {
  for (const locale of LOCALES) {
    const f = path.join(ROOT, 'pbj', locale, 'index.html');
    if (!fs.existsSync(f)) continue;
    let html = fs.readFileSync(f, 'utf8');
    html = html.replace(
      /href="\/for-professionals\/"/g,
      `href="/for-professionals/${locale}/"`
    );
    fs.writeFileSync(f, html, 'utf8');
  }
}

// --- main ---
for (const page of PAGES) {
  if (!fs.existsSync(page.enPath)) {
    console.error('Missing EN source', page.enPath);
    process.exit(1);
  }
  addLangStripToEnglish(page);
}

const report = [];
for (const locale of LOCALES) {
  buildLocalePostsJson(locale);
  for (const page of PAGES) {
    const r = processPage(page, locale);
    report.push({ url: page.locUrl(locale), used: r.used });
    console.log('wrote', page.locUrl(locale), 'used', r.used);
  }
}

retargetPbjProfessionals();

// Append locale URLs to sitemap.xml (blog posts, blog index, hubs)
{
  const sitemapPath = path.join(ROOT, 'sitemap.xml');
  let sm = fs.readFileSync(sitemapPath, 'utf8');
  const today = new Date().toISOString().slice(0, 10);
  const entries = [];
  for (const page of PAGES) {
    for (const locale of LOCALES) {
      const loc = `https://josspatech.com${page.locUrl(locale)}`;
      if (sm.includes(`<loc>${loc}</loc>`)) continue;
      entries.push(
        `  <url>\n    <loc>${loc}</loc>\n    <lastmod>${today}</lastmod>\n  </url>`
      );
    }
  }
  if (entries.length) {
    sm = sm.replace('</urlset>', `${entries.join('\n')}\n</urlset>`);
    fs.writeFileSync(sitemapPath, sm, 'utf8');
    console.log('sitemap +', entries.length, 'locale URLs');
  }
}

fs.writeFileSync(
  path.join(__dirname, '_localized-blog-hub-report.json'),
  `${JSON.stringify({ generatedAt: new Date().toISOString(), pages: report }, null, 2)}\n`
);
console.log(
  'Done.',
  PAGES.length,
  '×',
  LOCALES.length,
  '+ EN language strips + PBJ locale → /for-professionals/<locale>/'
);
