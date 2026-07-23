#!/usr/bin/env node
'use strict';
const fs = require('fs');
const path = require('path');

const ROOT = path.resolve(__dirname, '..');
const OUT = path.join(ROOT, 'videos', 'user-guide-hhh');
const narr = JSON.parse(fs.readFileSync(path.join(OUT, 'narration-en.json'), 'utf8'));
const html = fs.readFileSync(path.join(OUT, 'index.html'), 'utf8');

const slides = [];
const re = /<div class="slide(?:\s+active)?"([^>]*)>/g;
let m;
while ((m = re.exec(html))) {
  const a = m[1];
  const idx = Number((a.match(/data-index="(\d+)"/) || [])[1]);
  const chunk = html.slice(m.index, m.index + 800);
  const src = ((chunk.match(/<img[^>]+src="([^"]+)/) || [])[1] || '').split('?')[0];
  const alt = (chunk.match(/alt="([^"]*)"/) || [])[1] || '';
  const abs = src ? path.join(ROOT, src.replace(/^\//, '')) : '';
  slides.push({
    idx,
    src,
    alt,
    exists: abs ? fs.existsSync(abs) : false,
  });
}

const byIdx = new Map(slides.map((s) => [s.idx, s]));
const rows = narr.map((n, i) => {
  const s = byIdx.get(i) || {};
  return {
    i,
    n,
    src: s.src || null,
    alt: s.alt || null,
    exists: !!s.exists,
  };
});

const flags = {
  harold: rows.filter((r) => /Harold/i.test(r.n)),
  ludwig: rows.filter((r) => /Ludwig/i.test(r.n)).map((r) => r.i),
  install: rows.filter((r) => /install|TestFlight|internal testing|Play open|opt in/i.test(r.n)),
  fourTabs: rows.filter((r) => /four tabs/i.test(r.n)),
  missingFiles: rows.filter((r) => r.src && !r.exists),
  noImg: rows.filter((r) => !r.src),
  installAssets: rows.filter((r) => /play-internal-install|testflight/i.test(r.src || '')),
};

const report = { narr: narr.length, slides: slides.length, flags, rows };
fs.writeFileSync(path.join(OUT, '_shot-audit.json'), JSON.stringify(report, null, 2));
console.log(JSON.stringify({
  narr: report.narr,
  slides: report.slides,
  harold: flags.harold.map((r) => r.i),
  ludwigSlides: flags.ludwig,
  installSlides: flags.install.map((r) => ({ i: r.i, n: r.n.slice(0, 100) })),
  fourTabs: flags.fourTabs.map((r) => r.i),
  missingFiles: flags.missingFiles.map((r) => r.i + ':' + r.src),
  installAssets: flags.installAssets.map((r) => r.i + ':' + r.src),
}, null, 2));
