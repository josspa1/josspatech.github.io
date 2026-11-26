/**
 * Provider-neutral backup wording (2026-11-25).
 * Replaces Drive/iCloud AES-scrub line with brand-free cloud storage line.
 * Does NOT touch video narration (report-only from Part 1).
 * Does NOT stage scripts/_localized-*-report.json (pre-existing dirty WIP).
 */
const fs = require('fs');
const path = require('path');

const ROOT = path.join(__dirname, '..');

const PAIRS = [
  // EN (+ HTML entity dash)
  [
    'Optional backups live in your own Drive or iCloud — never on a JosspaTech server.',
    'Optional backups live in your own cloud storage — never on a JosspaTech server.',
  ],
  [
    'Optional backups live in your own Drive or iCloud &mdash; never on a JosspaTech server.',
    'Optional backups live in your own cloud storage &mdash; never on a JosspaTech server.',
  ],
  [
    'Backups are optional and live in your own Drive or iCloud — never on a JosspaTech server.',
    'Optional backups live in your own cloud storage — never on a JosspaTech server.',
  ],
  // Locale translations of the scrub line
  [
    'Las copias de seguridad opcionales viven en tu propio Drive o iCloud — nunca en un servidor de JosspaTech.',
    'Las copias de seguridad opcionales viven en tu propio almacenamiento en la nube — nunca en un servidor de JosspaTech.',
  ],
  [
    'Optionale Backups liegen in deinem eigenen Drive oder iCloud — nie auf einem JosspaTech-Server.',
    'Optionale Backups liegen in deinem eigenen Cloud-Speicher — nie auf einem JosspaTech-Server.',
  ],
  [
    'Les sauvegardes facultatives restent dans votre propre Drive ou iCloud — jamais sur un serveur JosspaTech.',
    'Les sauvegardes facultatives restent dans votre propre stockage cloud — jamais sur un serveur JosspaTech.',
  ],
  [
    'As cópias de segurança opcionais ficam no teu próprio Drive ou iCloud — nunca num servidor JosspaTech.',
    'As cópias de segurança opcionais ficam no teu próprio armazenamento na nuvem — nunca num servidor JosspaTech.',
  ],
  [
    '可选备份保存在你自己的 Drive 或 iCloud 中——绝不会放在 JosspaTech 服务器上。',
    '可选备份保存在你自己的云存储中——绝不会放在 JosspaTech 服务器上。',
  ],
  [
    'I backup facoltativi restano nel tuo Drive o iCloud — mai su un server JosspaTech.',
    'I backup facoltativi restano nel tuo spazio di archiviazione cloud — mai su un server JosspaTech.',
  ],
  [
    'वैकल्पिक बैकअप आपके अपने Drive या iCloud में रहते हैं — कभी भी JosspaTech सर्वर पर नहीं।',
    'वैकल्पिक बैकअप आपके अपने क्लाउड स्टोरेज में रहते हैं — कभी भी JosspaTech सर्वर पर नहीं।',
  ],
];

const SKIP = new Set([
  path.normalize('scripts/_localized-blog-hub-report.json'),
  path.normalize('scripts/_localized-product-pages-report.json'),
  path.normalize('scripts/_provider-neutral-backup-2026-11-25.js'),
]);

function walk(dir, out = []) {
  for (const ent of fs.readdirSync(dir, { withFileTypes: true })) {
    if (ent.name === 'node_modules' || ent.name === '.git') continue;
    const p = path.join(dir, ent.name);
    if (ent.isDirectory()) walk(p, out);
    else if (/\.(html?|md|txt|js|mjs|json|py|ts)$/i.test(ent.name)) out.push(p);
  }
  return out;
}

const changed = [];
for (const file of walk(ROOT)) {
  const rel = path.relative(ROOT, file);
  if (SKIP.has(path.normalize(rel))) continue;
  let text = fs.readFileSync(file, 'utf8');
  let next = text;
  for (const [from, to] of PAIRS) {
    if (next.includes(from)) next = next.split(from).join(to);
  }
  if (next !== text) {
    fs.writeFileSync(file, next, 'utf8');
    changed.push(rel.replace(/\\/g, '/'));
  }
}

console.log(`Updated ${changed.length} files:`);
for (const f of changed) console.log(' ', f);
