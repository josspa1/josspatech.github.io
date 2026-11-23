/**
 * Finish blog/hub batch 0a indices 20–56 via Azure Translator (pbj-translator F0).
 * Reads AZURE_TRANSLATOR_* from PBJ SourceCode/.env — never writes keys into this repo.
 * Brand + feature terms wrapped in translate="no" spans (HTML textType).
 */
import fs from 'fs';
import path from 'path';
import { fileURLToPath } from 'url';

const __dirname = path.dirname(fileURLToPath(import.meta.url));
const ROOT = path.join(__dirname, '..');
const PBJ_ENV = 'C:\\Users\\jossp\\Documents\\MobileApps\\PBJ\\SourceCode\\.env';
const QUOTA_PATH =
  'C:\\Users\\jossp\\Documents\\MobileApps\\PBJ\\SourceCode\\scripts\\.i18n_quota_state.json';

const LOCALES = ['es', 'de', 'fr', 'pt', 'zh', 'it', 'hi'];
const AZURE_TO = { es: 'es', de: 'de', fr: 'fr', pt: 'pt', zh: 'zh-Hans', it: 'it', hi: 'hi' };

const PROTECT = [
  'Handy Horology Helper',
  "Curator's Vault",
  "Curator’s Vault",
  'PocketBudJet',
  'JosspaTech',
  'Chrono24',
  'Card Ladder',
  'Clockworks',
  'Unscribe',
  'Goodbudget',
  'Actual Budget',
  'Stanley Gibbons',
  'Grail Radar',
  'My Museum',
  'Clock Repair Help',
  'App Store',
  'Google Play',
  'American Philatelic Society',
  'Identify',
  'Coach',
  'Vault',
  'Wish list',
  'Reminders',
  'Export',
  'Import',
  'Budget',
  'Debt',
  'YNAB',
  'OFX',
  'CSV',
  'PDF',
  'JSON',
  'Scott',
  'Pro',
  'HHH',
  'CVC',
  'PBJ',
].sort((a, b) => b.length - a.length);

function loadEnv(file) {
  const out = {};
  for (const line of fs.readFileSync(file, 'utf8').split(/\r?\n/)) {
    const m = line.match(/^([A-Z0-9_]+)=(.*)$/);
    if (m) out[m[1]] = m[2].trim();
  }
  return out;
}

function protectHtml(text) {
  let s = text
    .replace(/&/g, '&amp;')
    .replace(/</g, '&lt;')
    .replace(/>/g, '&gt;')
    .replace(/\n/g, '<br/>');
  for (const term of PROTECT) {
    const esc = term.replace(/[.*+?^${}()|[\]\\]/g, '\\$&');
    s = s.replace(new RegExp(esc, 'g'), `<span translate="no">${term}</span>`);
  }
  return s;
}

function unprotectHtml(text) {
  return text
    .replace(/<span translate="no">\s*([\s\S]*?)\s*<\/span>/gi, '$1')
    .replace(/<br\s*\/?>/gi, '\n')
    .replace(/&lt;/g, '<')
    .replace(/&gt;/g, '>')
    .replace(/&quot;/g, '"')
    .replace(/&#39;/g, "'")
    .replace(/&amp;/g, '&');
}

async function translateBatch(strings, to, key, region) {
  const url = `https://api.cognitive.microsofttranslator.com/translate?api-version=3.0&from=en&to=${to}&textType=html`;
  const body = strings.map((s) => ({ Text: protectHtml(s) }));
  const sentChars = body.reduce((n, b) => n + b.Text.length, 0);
  let json;
  for (let attempt = 0; attempt < 8; attempt++) {
    const res = await fetch(url, {
      method: 'POST',
      headers: {
        'Ocp-Apim-Subscription-Key': key,
        'Ocp-Apim-Subscription-Region': region,
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(body),
    });
    if (res.status === 429) {
      await new Promise((r) => setTimeout(r, 15000 * (attempt + 1)));
      continue;
    }
    if (!res.ok) {
      const t = await res.text();
      throw new Error(`azure_${res.status}: ${t.slice(0, 200)}`);
    }
    json = await res.json();
    break;
  }
  if (!json) throw new Error('azure_throttled');
  return {
    texts: json.map((r) => unprotectHtml(r.translations[0].text)),
    sentChars,
  };
}

function loadQuota() {
  try {
    return JSON.parse(fs.readFileSync(QUOTA_PATH, 'utf8'));
  } catch {
    return { month: new Date().toISOString().slice(0, 7), used: 0 };
  }
}

function saveQuota(q) {
  fs.writeFileSync(QUOTA_PATH, `${JSON.stringify(q, null, 2)}\n`);
}

const env = loadEnv(PBJ_ENV);
const KEY = env.AZURE_TRANSLATOR_KEY;
const REGION = env.AZURE_TRANSLATOR_REGION || 'westus';
if (!KEY) {
  console.error('Missing AZURE_TRANSLATOR_KEY in PBJ .env');
  process.exit(1);
}

const enAll = JSON.parse(fs.readFileSync(path.join(__dirname, '_blog-hub-batch-0a.json'), 'utf8'));
const part0 = JSON.parse(
  fs.readFileSync(path.join(__dirname, '_blog-hub-tr-batch-0a-idx_part0.json'), 'utf8')
);
const part1 = JSON.parse(
  fs.readFileSync(path.join(__dirname, '_blog-hub-tr-batch-0a-idx_part1.json'), 'utf8')
);
if (part0.length !== 10 || part1.length !== 10) {
  console.error('Expected part0/part1 length 10 each', part0.length, part1.length);
  process.exit(1);
}

const restEn = enAll.slice(20); // 37 strings
const quotaBefore = loadQuota();
console.log(
  JSON.stringify({
    resource: 'pbj-translator',
    region: REGION,
    tier: 'F0',
    quotaBefore,
    restCount: restEn.length,
    enChars: restEn.reduce((n, s) => n + s.length, 0),
  })
);

const restIdx = [];
let totalSent = 0;
const CHUNK = 8;
for (let i = 0; i < restEn.length; i++) {
  restIdx.push({});
}

for (const loc of LOCALES) {
  const to = AZURE_TO[loc];
  for (let i = 0; i < restEn.length; i += CHUNK) {
    const chunk = restEn.slice(i, i + CHUNK);
    const { texts, sentChars } = await translateBatch(chunk, to, KEY, REGION);
    totalSent += sentChars;
    texts.forEach((t, j) => {
      restIdx[i + j][loc] = t;
    });
    console.log(`ok ${loc} ${Math.min(i + CHUNK, restEn.length)}/${restEn.length} chars+${sentChars}`);
    await new Promise((r) => setTimeout(r, Math.max(400, Math.ceil(sentChars / 28000 * 60000))));
  }
}

for (let i = 0; i < restIdx.length; i++) {
  for (const loc of LOCALES) {
    if (!restIdx[i][loc]) throw new Error(`missing ${i} ${loc}`);
  }
}

fs.writeFileSync(
  path.join(__dirname, '_blog-hub-tr-batch-0a-idx_part2.json'),
  `${JSON.stringify(restIdx.slice(0, 20), null, 2)}\n`
);
fs.writeFileSync(
  path.join(__dirname, '_blog-hub-tr-batch-0a-idx_part3.json'),
  `${JSON.stringify(restIdx.slice(20), null, 2)}\n`
);

const tr = [...part0, ...part1, ...restIdx];
if (tr.length !== enAll.length) throw new Error(`len ${tr.length}`);
const out = {};
for (let i = 0; i < enAll.length; i++) out[enAll[i]] = tr[i];
fs.writeFileSync(path.join(__dirname, '_blog-hub-tr-batch-0a-idx.json'), `${JSON.stringify(tr)}\n`);
fs.writeFileSync(
  path.join(__dirname, '_blog-hub-tr-batch-0a.json'),
  `${JSON.stringify(out, null, 2)}\n`
);

const month = new Date().toISOString().slice(0, 7);
const quotaAfter = {
  month,
  used: (quotaBefore.month === month ? quotaBefore.used : 0) + totalSent,
};
saveQuota(quotaAfter);

console.log(
  JSON.stringify({
    done: true,
    keys: Object.keys(out).length,
    azureCharsSent: totalSent,
    quotaAfter,
    note: 'No app production keys modified; only local .i18n_quota_state.json counter updated',
  })
);
