'use strict';
const fs = require('fs');
const path = require('path');

const ROOT = path.resolve(__dirname, '..');
const OUT = path.join(ROOT, 'videos', 'user-guide');
let html = fs.readFileSync(path.join(OUT, 'index.html'), 'utf8');
const narr = JSON.parse(fs.readFileSync(path.join(OUT, 'narration-en.json'), 'utf8'));

function altFromSrc(src, idx) {
  const base = path.basename(src.split('?')[0], path.extname(src.split('?')[0]));
  const name = base.replace(/[-_]/g, ' ').trim();
  if (name) return name.charAt(0).toUpperCase() + name.slice(1);
  return String(narr[idx] || 'PocketBudJet screen').slice(0, 72);
}

let filled = 0;
let guard = 0;
while (guard++ < 250) {
  const slideRe = /<div class="slide(?:\s+active)?"([^>]*)>/g;
  let sm;
  let changed = false;
  while ((sm = slideRe.exec(html))) {
    const idx = Number((sm[1].match(/data-index="(\d+)"/) || [])[1]);
    const start = sm.index;
    const region = html.slice(start, start + 1000);
    const img = region.match(/<img\b[^>]*>/);
    if (!img) continue;
    const tag = img[0];
    const altM = tag.match(/\salt="([^"]*)"/);
    if (altM && altM[1].trim()) continue;
    const srcM = tag.match(/\ssrc="([^"]+)"/);
    if (!srcM) continue;
    const alt = altFromSrc(srcM[1], idx).replace(/"/g, '');
    let newTag;
    if (altM) newTag = tag.replace(/\salt="[^"]*"/, ` alt="${alt}"`);
    else newTag = tag.replace(/<img\b/, `<img alt="${alt}"`);
    const abs = start + img.index;
    html = html.slice(0, abs) + newTag + html.slice(abs + tag.length);
    filled += 1;
    changed = true;
    break;
  }
  if (!changed) break;
}

fs.writeFileSync(path.join(OUT, 'index.html'), html);
console.log(JSON.stringify({ filled, emptyAlts: (html.match(/alt=""/g) || []).length }));
