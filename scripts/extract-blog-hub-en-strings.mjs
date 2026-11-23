/**
 * Extract unique English visible-copy strings from blog posts and hub pages
 * for localization. Writes scripts/_blog-hub-en-strings.json
 */
import fs from 'fs';
import path from 'path';
import { fileURLToPath } from 'url';

const __dirname = path.dirname(fileURLToPath(import.meta.url));
const ROOT = path.join(__dirname, '..');
const OUT = path.join(__dirname, '_blog-hub-en-strings.json');

const HTML_FILES = [
  'blog/apps-for-antique-collectors/index.html',
  'blog/budget-app-without-bank-login/index.html',
  'blog/ynab-alternative-private-budgeting/index.html',
  'blog/chrono24-alternative-watch-identification/index.html',
  'blog/card-ladder-alternative-collectibles-vault/index.html',
  'blog/coin-collection-inventory-software-free/index.html',
  'blog/stamp-collection-book-value/index.html',
  'blog/watch-service-log-template/index.html',
  'blog/document-collection-for-insurance/index.html',
  'blog/index.html',
  'for-professionals/index.html',
  'how-to/index.html',
  'how-to/faq/index.html',
];

const META_KEYS = new Set([
  'description',
  'og:title',
  'og:description',
  'og:site_name',
  'twitter:title',
  'twitter:description',
]);

const MACHINE_CONTENT = new Set([
  'index, follow',
  'index, follow, max-image-preview:large, max-snippet:-1',
  'summary_large_image',
  'en_US',
  'website',
  'article',
  'width=device-width, initial-scale=1.0',
  'UTF-8',
  '#0C3358',
  '#0c3358',
]);

const TINY_BRAND_ONLY = new Set([
  'HHH',
  'PBJ',
  'CVC',
  'Blog',
  'FAQ',
  '·',
  'OFX',
  'CSV',
  'PDF',
  'Pro',
  'App',
  'iOS',
]);

const JSON_LD_PROSE_KEYS = new Set([
  'headline',
  'name',
  'text',
  'description',
  'alternativeHeadline',
  'articleBody',
]);

const JSON_LD_SKIP_KEYS = new Set([
  '@context',
  '@type',
  '@id',
  'url',
  'image',
  'logo',
  'datePublished',
  'dateModified',
  'position',
  'mainEntityOfPage',
  'contentUrl',
  'sameAs',
]);

const BLOCK_TAGS =
  'p|h[1-6]|li|td|th|caption|figcaption|blockquote|dt|dd|summary|button|label|legend|a|figcaption';

const ENTITY_MAP = {
  amp: '&',
  lt: '<',
  gt: '>',
  quot: '"',
  apos: "'",
  nbsp: ' ',
};

function decodeEntities(raw) {
  return raw
    .replace(/&#(\d+);/g, (_, n) => String.fromCharCode(Number(n)))
    .replace(/&#x([0-9a-fA-F]+);/g, (_, h) => String.fromCharCode(parseInt(h, 16)))
    .replace(/&([a-z]+);/gi, (m, name) => ENTITY_MAP[name.toLowerCase()] ?? m);
}

function stripTags(html) {
  return html.replace(/<[^>]+>/g, ' ');
}

function normalize(text) {
  return decodeEntities(text)
    .replace(/\s+/g, ' ')
    .trim();
}

function isPureUrl(s) {
  return /^https?:\/\/\S+$/i.test(s) || /^mailto:\S+$/i.test(s);
}

function isMachineValue(s) {
  if (MACHINE_CONTENT.has(s)) return true;
  if (/^\d{4}-\d{2}-\d{2}$/.test(s)) return true;
  if (/^\d+$/.test(s)) return true;
  if (/^#[0-9a-fA-F]{3,8}$/.test(s)) return true;
  if (/^https?:\/\//i.test(s) && !/\s/.test(s)) return true;
  return false;
}

function isTinyBrandOnly(s) {
  if (TINY_BRAND_ONLY.has(s)) return true;
  if (s.length <= 2 && /^[A-Za-z0-9·]+$/.test(s)) return true;
  return false;
}

function shouldKeep(s) {
  if (!s || s.length < 2) return false;
  if (isPureUrl(s)) return false;
  if (isMachineValue(s)) return false;
  if (isTinyBrandOnly(s)) return false;
  if (!/[a-zA-Z]/.test(s)) return false;
  return true;
}

function addString(set, raw) {
  const s = normalize(raw);
  if (shouldKeep(s)) set.add(s);
}

function extractTitle(html, set) {
  const m = html.match(/<title[^>]*>([\s\S]*?)<\/title>/i);
  if (m) addString(set, stripTags(m[1]));
}

function extractMeta(html, set) {
  const metaRe =
    /<meta\s+[^>]*(?:name|property)=["']([^"']+)["'][^>]*content=["']([^"']*)["'][^>]*>/gi;
  let m;
  while ((m = metaRe.exec(html)) !== null) {
    const key = m[1].toLowerCase();
    if (META_KEYS.has(key) || key === 'twitter:title' || key === 'twitter:description') {
      addString(set, m[2]);
    }
  }
  const metaRe2 =
    /<meta\s+[^>]*content=["']([^"']*)["'][^>]*(?:name|property)=["']([^"']+)["'][^>]*>/gi;
  while ((m = metaRe2.exec(html)) !== null) {
    const key = m[2].toLowerCase();
    if (META_KEYS.has(key)) addString(set, m[1]);
  }
}

function collectJsonLdProse(value, set, parentKey = '') {
  if (value == null) return;
  if (typeof value === 'string') {
    if (JSON_LD_SKIP_KEYS.has(parentKey)) return;
    if (JSON_LD_PROSE_KEYS.has(parentKey) || parentKey === '') {
      addString(set, value);
    }
    return;
  }
  if (Array.isArray(value)) {
    for (const item of value) collectJsonLdProse(item, set, parentKey);
    return;
  }
  if (typeof value === 'object') {
    for (const [k, v] of Object.entries(value)) {
      if (JSON_LD_SKIP_KEYS.has(k)) continue;
      if (k === 'author' || k === 'publisher') {
        if (v && typeof v === 'object' && typeof v.name === 'string') {
          addString(set, v.name);
        }
        continue;
      }
      collectJsonLdProse(v, set, k);
    }
  }
}

function extractJsonLd(html, set) {
  const re = /<script\s+type=["']application\/ld\+json["'][^>]*>([\s\S]*?)<\/script>/gi;
  let m;
  while ((m = re.exec(html)) !== null) {
    try {
      const data = JSON.parse(m[1].trim());
      if (Array.isArray(data)) {
        for (const item of data) collectJsonLdProse(item, set);
      } else {
        collectJsonLdProse(data, set);
      }
    } catch {
      /* ignore malformed JSON-LD */
    }
  }
}

function sliceRegion(html, tag) {
  const open = new RegExp(`<${tag}[^>]*>`, 'i');
  const startM = html.match(open);
  if (!startM) return '';
  const start = startM.index + startM[0].length;
  const close = new RegExp(`</${tag}>`, 'gi');
  close.lastIndex = start;
  const endM = close.exec(html);
  if (!endM) return html.slice(start);
  return html.slice(start, endM.index);
}

function removeScriptsAndStyles(html) {
  return html
    .replace(/<script[\s\S]*?<\/script>/gi, '')
    .replace(/<style[\s\S]*?<\/style>/gi, '');
}

function extractBlockText(html, set) {
  const blockRe = new RegExp(
    `<(${BLOCK_TAGS})(\\s[^>]*)?>([\\s\\S]*?)<\\/\\1>`,
    'gi',
  );
  let m;
  while ((m = blockRe.exec(html)) !== null) {
    const inner = m[3];
    const text = normalize(stripTags(inner));
    if (!text) continue;
    addString(set, text);
    const childRe = new RegExp(
      `<(${BLOCK_TAGS})(\\s[^>]*)?>([\\s\\S]*?)<\\/\\1>`,
      'gi',
    );
    let cm;
    while ((cm = childRe.exec(inner)) !== null) {
      addString(set, stripTags(cm[3]));
    }
  }
}

function extractRegions(html, set) {
  const body = removeScriptsAndStyles(html);
  const header = sliceRegion(body, 'header');
  const main = sliceRegion(body, 'main');
  const article = sliceRegion(main || body, 'article');
  const navHeader = sliceRegion(header || body, 'nav');
  const navMain = sliceRegion(main || body, 'nav');
  const footer = sliceRegion(body, 'footer');

  for (const chunk of [navHeader, navMain, article || main, footer]) {
    if (chunk) extractBlockText(chunk, set);
  }
  if (!main && !article) {
    const bodyInner = sliceRegion(body, 'body');
    extractBlockText(bodyInner, set);
  }
}

function extractFile(relPath, set) {
  const abs = path.join(ROOT, relPath);
  const html = fs.readFileSync(abs, 'utf8');
  extractTitle(html, set);
  extractMeta(html, set);
  extractJsonLd(html, set);
  extractRegions(html, set);
}

const all = new Set();
for (const rel of HTML_FILES) {
  extractFile(rel, all);
}

const sorted = [...all].sort((a, b) => b.length - a.length || a.localeCompare(b));
fs.writeFileSync(OUT, JSON.stringify(sorted, null, 2) + '\n', 'utf8');

const stat = fs.statSync(OUT);
console.log(`Wrote ${sorted.length} strings → ${OUT}`);
console.log(`File size: ${stat.size} bytes (${(stat.size / 1024).toFixed(1)} KiB)`);
console.log('\nFirst 20 strings (longest-first):');
sorted.slice(0, 20).forEach((s, i) => {
  const preview = s.length > 120 ? s.slice(0, 117) + '…' : s;
  console.log(`${String(i + 1).padStart(2)}. [${s.length}] ${preview}`);
});