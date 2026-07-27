#!/usr/bin/env node
'use strict';
const fs = require('fs');
const path = require('path');
const { spawnSync } = require('child_process');

const OUT = path.join(__dirname, '..', 'videos', 'user-guide-hhh');
const narr = JSON.parse(fs.readFileSync(path.join(OUT, 'narration-en.json'), 'utf8'));
const html = fs.readFileSync(path.join(OUT, 'index.html'), 'utf8');

const slideRe = /<div class="slide(?:\s+active)?"([^>]*)>/g;
const slides = [];
let m;
while ((m = slideRe.exec(html))) {
  const attrs = m[1];
  const idx = Number((attrs.match(/data-index="(\d+)"/) || [])[1]);
  const multiRaw = (attrs.match(/data-taps='([^']+)'/) || [])[1];
  slides.push({
    idx,
    tapNone: /\bdata-tap-none\b/.test(attrs),
    tapX: (attrs.match(/data-tap-x="([^"]+)"/) || [])[1],
    tapY: (attrs.match(/data-tap-y="([^"]+)"/) || [])[1],
    label: (attrs.match(/data-tap-label="([^"]+)"/) || [])[1],
    showAt: Number((attrs.match(/data-tap-show-at="([^"]+)"/) || [])[1] || '0.3'),
    duration: Number((attrs.match(/data-tap-duration="([^"]+)"/) || [])[1] || '2.5'),
    multiTap: !!multiRaw,
  });
}

const mp3s = fs
  .readdirSync(path.join(OUT, 'audio'))
  .filter((f) => /^slide-\d+\.mp3$/.test(f))
  .map((f) => Number(f.match(/\d+/)[0]))
  .sort((a, b) => a - b);

console.log(
  JSON.stringify(
    {
      narr: narr.length,
      slides: slides.length,
      slideIdxRange: [slides[0]?.idx, slides[slides.length - 1]?.idx],
      mp3: mp3s.length,
      mp3Last: mp3s[mp3s.length - 1],
    },
    null,
    2,
  ),
);

const missingSlides = [];
for (let i = 0; i < narr.length; i++) if (!slides.some((s) => s.idx === i)) missingSlides.push(i);
const missingMp3 = [];
for (let i = 0; i < narr.length; i++) if (!mp3s.includes(i)) missingMp3.push(i);
console.log('missingSlides', missingSlides);
console.log('missingMp3', missingMp3);

const TAP_VERB = /\b(Tap|Open|Press|Choose|Pick|Select|Swipe|Go to)\b/i;
const issues = [];
for (const s of slides) {
  const n = narr[s.idx] || '';
  const hasVerb = TAP_VERB.test(n);
  const hasTap = !s.tapNone && (s.tapX != null || s.multiTap);
  if (hasVerb && s.tapNone) issues.push({ idx: s.idx, issue: 'verb+none', n: n.slice(0, 100) });
  if (hasVerb && !hasTap && !s.tapNone) issues.push({ idx: s.idx, issue: 'verb+noCoords', n: n.slice(0, 100) });
  if (!hasVerb && hasTap) issues.push({ idx: s.idx, issue: 'coords+noVerb', label: s.label, n: n.slice(0, 100) });
}
console.log('tapIssues', issues.length);
for (const row of issues.slice(0, 40)) console.log(JSON.stringify(row));

// Probe a few audio durations vs showAt
function resolveFfmpeg() {
  const w = spawnSync('where.exe', ['ffmpeg'], { encoding: 'utf8', shell: true });
  if (w.status === 0 && w.stdout.trim()) return w.stdout.trim().split(/\r?\n/)[0];
  return null;
}
function probe(ffmpeg, file) {
  const r = spawnSync(ffmpeg, ['-i', file, '-f', 'null', '-'], { encoding: 'utf8' });
  const mm = (r.stderr || '').match(/Duration:\s*(\d+):(\d+):(\d+(?:\.\d+)?)/);
  if (!mm) return null;
  return parseInt(mm[1], 10) * 3600 + parseInt(mm[2], 10) * 60 + parseFloat(mm[3]);
}
const ffmpeg = resolveFfmpeg();
if (ffmpeg) {
  const badTiming = [];
  for (const s of slides) {
    if (s.tapNone || !s.tapX) continue;
    const mp3 = path.join(OUT, 'audio', `slide-${s.idx}.mp3`);
    if (!fs.existsSync(mp3)) continue;
    const dur = probe(ffmpeg, mp3);
    if (dur == null) continue;
    if (s.showAt + 0.4 > dur) {
      badTiming.push({ idx: s.idx, showAt: s.showAt, audioSec: +dur.toFixed(2), n: (narr[s.idx] || '').slice(0, 80) });
    }
  }
  console.log('showAtPastAudioEnd', badTiming.length);
  for (const row of badTiming.slice(0, 30)) console.log(JSON.stringify(row));
}
