/**
 * Merge per-locale arrays _blog-hub-tr-{loc}.json into _blog-hub-tr-all.json
 */
import fs from 'fs';
import path from 'path';
import { fileURLToPath } from 'url';

const __dirname = path.dirname(fileURLToPath(import.meta.url));
const LOCALES = ['es', 'de', 'fr', 'pt', 'zh', 'it', 'hi'];
const en = JSON.parse(fs.readFileSync(path.join(__dirname, '_blog-hub-en-strings.json'), 'utf8'));

const arrays = {};
for (const loc of LOCALES) {
  const p = path.join(__dirname, `_blog-hub-tr-${loc}.json`);
  if (!fs.existsSync(p)) {
    console.error('Missing', p);
    process.exit(1);
  }
  arrays[loc] = JSON.parse(fs.readFileSync(p, 'utf8'));
  if (!Array.isArray(arrays[loc]) || arrays[loc].length !== en.length) {
    console.error('Bad length', loc, arrays[loc]?.length, 'expected', en.length);
    process.exit(1);
  }
  const missing = arrays[loc].filter((x) => typeof x !== 'string' || !x.length).length;
  if (missing) {
    console.error('Incomplete', loc, 'null/empty', missing);
    process.exit(1);
  }
}

const out = {};
for (let i = 0; i < en.length; i++) {
  const row = {};
  for (const loc of LOCALES) row[loc] = arrays[loc][i];
  out[en[i]] = row;
}

const dest = path.join(__dirname, '_blog-hub-tr-all.json');
fs.writeFileSync(dest, `${JSON.stringify(out, null, 2)}\n`);
console.log('Merged', Object.keys(out).length, '→', dest);
