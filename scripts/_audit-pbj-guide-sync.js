#!/usr/bin/env node
'use strict';
const fs = require('fs');
const path = require('path');

const ROOT = path.resolve(__dirname, '..');
const OUT = path.join(ROOT, 'videos', 'user-guide');
const narr = JSON.parse(fs.readFileSync(path.join(OUT, 'narration-en.json'), 'utf8'));
const html = fs.readFileSync(path.join(OUT, 'index.html'), 'utf8');

const slides = [];
const re = /<div class="slide(?:\s+active)?"([^>]*)>/g;
let m;
while ((m = re.exec(html))) {
  const attrs = m[1];
  const idx = Number((attrs.match(/data-index="(\d+)"/) || [])[1]);
  const chunk = html.slice(m.index, m.index + 900);
  const src = (chunk.match(/<img[^>]+src="([^"]+)"/) || [])[1] || null;
  slides.push({
    idx,
    src,
    tapNone: /\bdata-tap-none\b/.test(attrs),
    tapX: (attrs.match(/data-tap-x="([^"]+)"/) || [])[1],
    tapY: (attrs.match(/data-tap-y="([^"]+)"/) || [])[1],
    label: (attrs.match(/data-tap-label="([^"]+)"/) || [])[1],
    showAt: Number((attrs.match(/data-tap-show-at="([^"]+)"/) || [])[1] || '0.3'),
  });
}

const broken = [];
const missingSrc = [];
for (const s of slides) {
  if (!s.src) {
    missingSrc.push(s.idx);
    continue;
  }
  const rel = s.src.replace(/^\//, '');
  const clean = rel.split('?')[0];
  const abs = path.join(ROOT, clean);
  if (!fs.existsSync(abs)) broken.push({ idx: s.idx, src: s.src });
}

const byIdx = new Map(slides.map((s) => [s.idx, s]));
const missingSlides = [];
for (let i = 0; i < narr.length; i++) if (!byIdx.has(i)) missingSlides.push(i);

const TAP_VERB = /\b(Tap|Open|Press|Choose|Pick|Select|Swipe|Go to|Allow)\b/i;
const tapIssues = [];
for (const s of slides) {
  const n = narr[s.idx] || '';
  const hasVerb = TAP_VERB.test(n);
  const hasTap = !s.tapNone && s.tapX != null;
  if (hasVerb && s.tapNone) tapIssues.push({ idx: s.idx, issue: 'verb+none', n: n.slice(0, 90) });
  if (hasVerb && !hasTap && !s.tapNone) tapIssues.push({ idx: s.idx, issue: 'verb+noCoords', n: n.slice(0, 90) });
  if (!hasVerb && hasTap) tapIssues.push({ idx: s.idx, issue: 'coords+noVerb', label: s.label, n: n.slice(0, 90) });
}

const report = {
  narr: narr.length,
  slides: slides.length,
  brokenCount: broken.length,
  missingSrc,
  missingSlides,
  tapIssues: tapIssues.length,
  broken,
  tapIssuesSample: tapIssues.slice(0, 50),
  map0to25: Array.from({ length: Math.min(26, narr.length) }, (_, i) => ({
    i,
    n: (narr[i] || '').slice(0, 72),
    src: byIdx.get(i)?.src || null,
    label: byIdx.get(i)?.label || null,
  })),
};

fs.writeFileSync(path.join(OUT, '_sync-audit.json'), JSON.stringify(report, null, 2));
console.log(JSON.stringify({
  narr: report.narr,
  slides: report.slides,
  broken: report.brokenCount,
  missingSlides: report.missingSlides.length,
  tapIssues: report.tapIssues,
}, null, 2));
console.log('broken:', broken.map((b) => `${b.idx}:${b.src}`).join('\n'));
console.log('wrote', path.join(OUT, '_sync-audit.json'));
