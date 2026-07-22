#!/usr/bin/env node
'use strict';

const fs = require('fs');
const path = require('path');

const ROOT = path.resolve(__dirname, '..');
const NARR = path.join(ROOT, 'videos', 'user-guide-hhh', 'narration-en.json');
const HTML = path.join(ROOT, 'videos', 'user-guide-hhh', 'index.html');
const WT = path.join(ROOT, 'videos', 'hhh', 'walkthrough', 'index.html');

const UPDATES = {
  34: 'Tap Identify. Wait while HHH reads your photo and searches reference databases.',
  65: 'From Tools, open Web Companion and tap Start. Your phone shows a local address and a large four-digit pairing code.',
  66: 'On a PC on the same Wi-Fi, open that address in a browser, then type the four-digit code shown on the phone.',
  67: 'On the PC dashboard, browse pieces, add watches, and manage hunts — changes sync back to the phone over your home network.',
  68: 'Open Settings, then File backup — or open File backup from Tools — to manage your portable .hhh backup.',
  69: 'Tap Save a Copy. Choose Drive, Files, email, or another share destination for the .hhh file.',
  70: 'On another phone, tap Bring a Copy Back and pick your .hhh file. Confirm before it adds or replaces museum data.',
  71: 'Optional: use Device Sync to move pieces between your own phones or tablets on the same Wi-Fi. Pro cloud sync stays optional — your museum lives on the device first.',
  88: 'Tap Photo Coach for guided step-by-step shots — dial, caseback, movement — Pro feature.',
  100: 'Tap Offline Show Pack under Settings before a flea market or show with no signal. Identify with internet is always more accurate — use the pack only offline.',
};

const narr = JSON.parse(fs.readFileSync(NARR, 'utf8'));
for (const [k, text] of Object.entries(UPDATES)) {
  const i = Number(k);
  if (!narr[i]) throw new Error('missing slide ' + i);
  narr[i] = text;
}
fs.writeFileSync(NARR, JSON.stringify(narr, null, 2) + '\n');

let html = fs.readFileSync(HTML, 'utf8');

// Sync transcript paragraphs
for (const [k, text] of Object.entries(UPDATES)) {
  const re = new RegExp(
    `(<p class="transcript-para" data-slide="${k}">)[\\s\\S]*?(</p>)`,
  );
  if (!re.test(html)) throw new Error('transcript missing slide ' + k);
  html = html.replace(re, `$1${text}$2`);
}

// Sync embedded NARRATION array — replace whole const NARRATION = [...];
{
  const start = html.indexOf('const NARRATION = [');
  const end = html.indexOf('];', start);
  if (start === -1 || end === -1) throw new Error('NARRATION array not found');
  const body = narr.map((t) => ' "' + t.replace(/\\/g, '\\\\').replace(/"/g, '\\"') + '",').join('\n');
  html = html.slice(0, start) + 'const NARRATION = [\n' + body + '\n' + html.slice(end);
}

// Slide chrome labels
html = html.replace('data-tap-label="QR code"', 'data-tap-label="Pairing code"');
html = html.replace('alt="QR code pairing"', 'alt="Pairing code on phone"');
html = html.replace('data-tap-label="Export"', 'data-tap-label="Save a Copy"');
html = html.replace('alt="Export backup"', 'alt="Save a Copy"');
html = html.replace('data-tap-label="Restore"', 'data-tap-label="Bring a Copy Back"');
html = html.replace('alt="Restore backup"', 'alt="Bring a Copy Back"');
html = html.replace('data-tap-label="Cloud sync"', 'data-tap-label="Device Sync"');
html = html.replace('alt="Cloud sync toggle"', 'alt="Device Sync option"');
html = html.replace('data-tap-label="Photo Studio"', 'data-tap-label="Photo Coach"');
html = html.replace('alt="Photo Studio Pro"', 'alt="Photo Coach Pro"');

// Recalibrate WC / backup tap show-at for longer accurate lines (fraction of typical TTS)
html = html.replace(
  'data-index="65" data-tap-x="50" data-tap-y="58" data-tap-label="Web Companion" data-tap-show-at="2.7"',
  'data-index="65" data-tap-x="50" data-tap-y="58" data-tap-label="Web Companion" data-tap-show-at="1.2"',
);
html = html.replace(
  'data-index="66" data-tap-x="50" data-tap-y="33" data-tap-label="Pairing code" data-tap-show-at="0.3"',
  'data-index="66" data-tap-x="50" data-tap-y="48" data-tap-label="Pairing code" data-tap-show-at="1.4"',
);

fs.writeFileSync(HTML, html);

let wt = fs.readFileSync(WT, 'utf8');
wt = wt.replace(
  "line: 'Web Companion puts the collection on your PC via LAN QR.'",
  "line: 'Web Companion opens your museum on a PC — same Wi‑Fi, address + 4-digit code.'",
);
wt = wt.replace(
  "line: 'Pro tools: compare pieces, atomic time, moon phase, and more.'",
  "line: 'Pro tools, Photo Coach, Offline Show Pack, and Device Sync when you need them.'",
);
fs.writeFileSync(WT, wt);

console.log('Updated narration, interactive manual, walkthrough overview.');
console.log('Changed slides:', Object.keys(UPDATES).join(', '));
