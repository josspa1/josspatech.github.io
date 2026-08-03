#!/usr/bin/env node
/**
 * Precise A/V + tap-circle sync for videos/user-guide-hhh/
 *
 * - Patch narration so circled controls use clear action verbs
 * - Fix missing / wrong tap coords + labels
 * - Recalibrate data-tap-show-at / duration from real MP3 length × verb word index
 *
 * Usage:
 *   node scripts/sync-hhh-user-guide-precise.js
 *   python scripts/gen-user-guide-hhh-en-audio.py --only-changed
 *   node scripts/render-user-guide-hhh-video.js
 */
'use strict';

const fs = require('fs');
const path = require('path');
const { spawnSync } = require('child_process');

const ROOT = path.resolve(__dirname, '..');
const OUT = path.join(ROOT, 'videos', 'user-guide-hhh');
const NARR_PATH = path.join(OUT, 'narration-en.json');
const HTML_PATH = path.join(OUT, 'index.html');
const AUDIO_DIR = path.join(OUT, 'audio');

const ACTION_VERB =
  /\b(Tap|Open|Press|Choose|Pick|Select|Swipe|Switch|Scroll|Use|Fill|Enter|Install|Allow|Manage|Browse|Expand|Notice|Clear)\b/i;

const NARRATION_PATCHES = {
  1: 'iOS: Email support@josspatech.com for a TestFlight invite. Install TestFlight, accept the invite, then tap Install for Handy Horology Helper.',
  10: 'Tap Hunt on the quick command row for eBay grails. Identify opens photo ID, Clock Repair Help starts the symptom wizard, and Add Watch opens My Museum. Bench tools live under Tools.',
  11: 'Tap a getting started path card to jump straight to Hunt on eBay, troubleshoot a clock, start your museum, or identify a piece.',
  14: 'Tap Owned at the top to see your collection. Wish holds grail targets; For Sale lists pieces you are selling.',
  18: 'On Piece Detail, swipe the photo gallery. Brand, model, reference, and estimated value sit below the photos.',
  19: 'Tap Provenance to record where you bought the piece, serial numbers, and collector notes.',
  26: 'Tap the Brand field and fill brand, model, reference, serial, purchase price, and optional notes.',
  32: 'Scroll to What do you know? Tap Brand guess and enter model, reference, serial, or free-text clues.',
  51: 'Tap a wish-list row to open Grail Radar for that grail. Hunt rules and last-check time appear at the top.',
  71: 'Optional: tap Device Sync to move pieces between your own phones or tablets on the same Wi-Fi. Pro cloud sync stays optional — your museum lives on the device first.',
  76: 'Database encryption is shown as Not available. HHH does not currently use SQLCipher, so the local SQLite file is not encrypted at rest by this setting.',
  77: 'Tap Notifications, then allow eBay Grail Radar alerts and service reminders.',
  80: 'Tap Manage to cancel or change your subscription through Google Play or the App Store.',
  106: 'Tap Contact and fill Your contact for dealers — name is required; add phone, email, and optional website.',
  111: 'Tap a Demand Rolodex board group by make and model. Expand it for contacts, specs, and notes — no prices on the card.',
};

/** idx → null (tap-none) | {x,y,label} | undefined (keep existing coords, retimed) */
const TAP_PATCHES = {
  1: { x: 50, y: 88, label: 'Install' },
  10: { x: 13, y: 24, label: 'Hunt' },
  11: { x: 50, y: 45, label: 'Path card' },
  14: { x: 17, y: 22, label: 'Owned' },
  18: { x: 50, y: 32, label: 'Photos' },
  19: { x: 50, y: 55, label: 'Provenance' },
  26: { x: 50, y: 50, label: 'Brand' },
  32: { x: 50, y: 58, label: 'Brand guess' },
  51: { x: 50, y: 40, label: 'Wish row' },
  71: { x: 50, y: 55, label: 'Device Sync' },
  76: null,
  77: { x: 50, y: 65, label: 'Notifications' },
  80: { x: 50, y: 80, label: 'Manage' },
  106: { x: 50, y: 40, label: 'Contact' },
  111: { x: 50, y: 45, label: 'Board' },
};

function resolveFfmpeg() {
  const w = spawnSync('where.exe', ['ffmpeg'], { encoding: 'utf8', shell: true });
  if (w.status === 0 && w.stdout.trim()) return w.stdout.trim().split(/\r?\n/)[0];
  return process.env.FFMPEG_PATH || null;
}

function probeDuration(ffmpeg, filePath) {
  const r = spawnSync(ffmpeg, ['-i', filePath, '-f', 'null', '-'], { encoding: 'utf8' });
  const m = (r.stderr || '').match(/Duration:\s*(\d+):(\d+):(\d+(?:\.\d+)?)/);
  if (!m) return null;
  return parseInt(m[1], 10) * 3600 + parseInt(m[2], 10) * 60 + parseFloat(m[3]);
}

function estimateShowAt(narration, audioSec) {
  if (!narration || !audioSec) return 0.3;
  const m = ACTION_VERB.exec(narration);
  if (!m) return 0.3;
  const wordsBefore = narration.slice(0, m.index).split(/\s+/).filter(Boolean).length;
  const totalWords = Math.max(1, narration.split(/\s+/).filter(Boolean).length);
  const frac = wordsBefore / totalWords;
  const show = Math.max(0.15, audioSec * frac - 0.12);
  return Math.round(Math.min(audioSec * 0.82, show) * 10) / 10;
}

function estimateDuration(audioSec, showAt) {
  const remaining = Math.max(0.4, audioSec - showAt - 0.15);
  return Math.round(Math.min(3.2, Math.max(1.4, remaining * 0.55)) * 10) / 10;
}

function parseOpen(attrs) {
  const idx = Number((attrs.match(/data-index="(\d+)"/) || [])[1]);
  return {
    idx,
    active: /\bactive\b/.test(attrs) || /class="slide active"/.test(attrs),
    x: (attrs.match(/data-tap-x="([^"]+)"/) || [])[1],
    y: (attrs.match(/data-tap-y="([^"]+)"/) || [])[1],
    label: (attrs.match(/data-tap-label="([^"]+)"/) || [])[1],
    tapNone: /\bdata-tap-none\b/.test(attrs),
  };
}

function buildOpen({ active, idx, tapNone, x, y, label, showAt, duration }) {
  const cls = active ? 'slide active' : 'slide';
  if (tapNone || x == null || y == null) {
    return `<div class="${cls}" data-index="${idx}" data-tap-none>`;
  }
  return (
    `<div class="${cls}" data-index="${idx}"` +
    ` data-tap-x="${x}" data-tap-y="${y}" data-tap-label="${label || ''}"` +
    ` data-tap-show-at="${showAt}" data-tap-duration="${duration}">`
  );
}

function audioSeconds(ffmpeg, idx, narr) {
  const mp3 = path.join(AUDIO_DIR, `slide-${idx}.mp3`);
  if (fs.existsSync(mp3)) {
    const d = probeDuration(ffmpeg, mp3);
    if (d != null) return d;
  }
  const words = (narr[idx] || '').split(/\s+/).filter(Boolean).length;
  return Math.max(1.5, words * 0.38);
}

function main() {
  const ffmpeg = resolveFfmpeg();
  if (!ffmpeg) {
    console.error('ffmpeg required');
    process.exit(1);
  }

  const narr = JSON.parse(fs.readFileSync(NARR_PATH, 'utf8'));
  const changedAudio = [];
  for (const [k, text] of Object.entries(NARRATION_PATCHES)) {
    const i = Number(k);
    if (narr[i] !== text) {
      narr[i] = text;
      changedAudio.push(i);
    }
  }
  fs.writeFileSync(NARR_PATH, `${JSON.stringify(narr, null, 2)}\n`, 'utf8');

  let html = fs.readFileSync(HTML_PATH, 'utf8');
  const re = /<div class="slide(?:\s+active)?"([^>]*)>/g;
  let m;
  const jobs = [];
  while ((m = re.exec(html))) {
    jobs.push({ start: m.index, end: m.index + m[0].length, full: m[0], attrs: m[1] });
  }

  let updated = 0;
  // rebuild from end
  for (let j = jobs.length - 1; j >= 0; j--) {
    const job = jobs[j];
    const parsed = parseOpen(job.full);
    const idx = parsed.idx;
    if (!Number.isFinite(idx)) continue;

    let tapNone = parsed.tapNone;
    let x = parsed.x;
    let y = parsed.y;
    let label = parsed.label;

    if (Object.prototype.hasOwnProperty.call(TAP_PATCHES, idx)) {
      const patch = TAP_PATCHES[idx];
      if (patch == null) {
        tapNone = true;
        x = y = label = undefined;
      } else {
        tapNone = false;
        x = String(patch.x);
        y = String(patch.y);
        label = patch.label;
      }
    }

    let showAt = 0.3;
    let duration = 2.5;
    if (!tapNone && x != null && y != null) {
      const sec = audioSeconds(ffmpeg, idx, narr);
      showAt = estimateShowAt(narr[idx] || '', sec);
      duration = estimateDuration(sec, showAt);
    }

    const next = buildOpen({
      active: /class="slide active"/.test(job.full),
      idx,
      tapNone: tapNone || x == null || y == null,
      x,
      y,
      label,
      showAt,
      duration,
    });
    if (next !== job.full) {
      html = html.slice(0, job.start) + next + html.slice(job.end);
      updated += 1;
    }
  }

  if (/const NARRATION\s*=/.test(html)) {
    html = html.replace(/const NARRATION\s*=\s*\[[\s\S]*?\];/, `const NARRATION = ${JSON.stringify(narr)};`);
  }

  for (const [k, text] of Object.entries(NARRATION_PATCHES)) {
    const i = Number(k);
    const tre = new RegExp(
      `(<p class="transcript-para(?: current)?" data-slide="${i}">)[\\s\\S]*?(</p>)`,
    );
    html = html.replace(tre, `$1${text.replace(/&/g, '&amp;').replace(/</g, '&lt;')}$2`);
  }

  fs.writeFileSync(HTML_PATH, html, 'utf8');
  fs.writeFileSync(path.join(OUT, '_audio_regen_slides.json'), JSON.stringify(changedAudio, null, 2));
  console.log(`slides retimed/patched: ${updated}`);
  console.log(`audio regen slides: ${changedAudio.join(', ') || '(none)'}`);
}

main();
