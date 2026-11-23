/**
 * Merge _blog-hub-tr-batch-*.json into localized-blog-hub-i18n.mjs
 * Run after all 4 translation batches finish.
 */
import fs from 'fs';
import path from 'path';
import { fileURLToPath } from 'url';
import { FEATURE_FROM_APP } from './localized-product-i18n.mjs';

const __dirname = path.dirname(fileURLToPath(import.meta.url));
const LOCALES = ['es', 'de', 'fr', 'pt', 'zh', 'it', 'hi'];

const enList = JSON.parse(
  fs.readFileSync(path.join(__dirname, '_blog-hub-en-strings.json'), 'utf8')
);

const allPath = path.join(__dirname, '_blog-hub-tr-all.json');
const merged = {};
if (fs.existsSync(allPath)) {
  Object.assign(merged, JSON.parse(fs.readFileSync(allPath, 'utf8')));
} else {
  const batchIds = ['0a', '0b', '1', '2', '3a', '3b', '4', '5', '6', '7'];
  for (const id of batchIds) {
    const p = path.join(__dirname, `_blog-hub-tr-batch-${id}.json`);
    if (!fs.existsSync(p)) {
      console.error('Missing', p, '(or _blog-hub-tr-all.json)');
      process.exit(1);
    }
    Object.assign(merged, JSON.parse(fs.readFileSync(p, 'utf8')));
  }
}

const missing = enList.filter((s) => !merged[s]);
const incomplete = [];
for (const en of enList) {
  const m = merged[en];
  if (!m) continue;
  for (const loc of LOCALES) {
    if (!m[loc] || typeof m[loc] !== 'string') {
      incomplete.push(`${en.slice(0, 40)}… missing ${loc}`);
      break;
    }
  }
}

console.log('EN keys:', enList.length);
console.log('Merged keys:', Object.keys(merged).length);
console.log('Missing EN:', missing.length);
console.log('Incomplete locales:', incomplete.length);
if (missing.length || incomplete.length) {
  console.error(missing.slice(0, 5));
  console.error(incomplete.slice(0, 10));
  process.exit(1);
}

// Only keep EN list keys (drop extras)
const STRINGS = {};
for (const en of enList) STRINGS[en] = merged[en];

const outPath = path.join(__dirname, 'localized-blog-hub-i18n.mjs');
const body = `/**
 * Auto-assembled blog + hub i18n. Do not hand-edit HTML clones.
 * Source EN: _blog-hub-en-strings.json · translations: _blog-hub-tr-batch-*.json
 */
export const LOCALES = ${JSON.stringify(LOCALES)};

export const STRINGS = ${JSON.stringify(STRINGS, null, 2)};

/** Re-export feature labels from product i18n for <strong> rewrap. */
export const FEATURE_FROM_APP = ${JSON.stringify(FEATURE_FROM_APP, null, 2)};
`;

fs.writeFileSync(outPath, body, 'utf8');
console.log('Wrote', outPath, 'bytes', fs.statSync(outPath).size);
