#!/usr/bin/env node
/**
 * PocketBudJet user-guide: map each narration line to a real screenshot + tap target.
 * Replaces "Screenshot pending" placeholders and obvious mismatches.
 *
 *   node scripts/sync-pbj-user-guide-precise.js
 */
'use strict';

const fs = require('fs');
const path = require('path');
const { spawnSync } = require('child_process');

const ROOT = path.resolve(__dirname, '..');
const OUT = path.join(ROOT, 'videos', 'user-guide');
const HTML_PATH = path.join(OUT, 'index.html');
const NARR_PATH = path.join(OUT, 'narration-en.json');
const AUDIO_DIR = path.join(OUT, 'audio');
const ASSETS = path.join(ROOT, 'assets', 'screenshots');

const ACTION_VERB =
  /\b(Tap|Open|Press|Choose|Pick|Select|Swipe|Switch|Scroll|Allow|Enter|Start|Launch|Connect|Enable|Say|Ask|Set|Flag|Grab|Review|Load|Type|Crush)\b/i;

/** idx → absolute web path under /assets/screenshots/… */
const IMG = {
  0: '/assets/screenshots/cold-start/splash.png',
  1: '/assets/screenshots/cold-start/showcase-1.png',
  2: '/assets/screenshots/cold-start/showcase-2.png',
  3: '/assets/screenshots/cold-start/showcase-3.png',
  4: '/assets/screenshots/cold-start/showcase-4.png',
  5: '/assets/screenshots/cold-start/onboarding-terms-tab-initial.png',
  6: '/assets/screenshots/cold-start/onboarding-disclaimer-tab.png',
  7: '/assets/screenshots/cold-start/onboarding-terms-both-complete.png',
  8: '/assets/screenshots/cold-start/security-setup.png',
  9: '/assets/screenshots/pbj/01-home-dashboard.png',
  10: '/assets/screenshots/wayfinding/wayfinding-tab-bar.png',
  11: '/assets/screenshots/wayfinding/wayfinding-header.png',
  12: '/assets/screenshots/wayfinding/wayfinding-drawer.png',
  13: '/assets/screenshots/wayfinding/wayfinding-toolbox.png',
  14: '/assets/screenshots/wayfinding/wayfinding-quick-add.png',
  15: '/assets/screenshots/cold-start/subscription-intro.png',
  16: '/assets/screenshots/pbj/manual/notification-opt-in.png',
  17: '/assets/screenshots/settings/settings-open.png',
  18: '/assets/screenshots/budget-setup/step-1-name.png',
  19: '/assets/screenshots/cold-start/wizard-currency.png',
  20: '/assets/screenshots/budget-setup/step-5-accounts.png',
  21: '/assets/screenshots/budget-setup/step-2-income.png',
  22: '/assets/screenshots/cold-start/wizard-bills.png',
  23: '/assets/screenshots/cold-start/wizard-goals.png',
  24: '/assets/screenshots/budget-setup/step-3-templates.png',
  25: '/assets/screenshots/cold-start/wizard-accessibility.png',
  26: '/assets/screenshots/budget-setup/step-7-dashboard.png',
  27: '/assets/screenshots/pbj/01-home-dashboard.png',
  28: '/assets/screenshots/activity/activity-tab.png',
  29: '/assets/screenshots/activity/activity-transaction-list.png',
  30: '/assets/screenshots/pbj/manual/activity-filters.png',
  31: '/assets/screenshots/activity/activity-transaction-detail.png',
  32: '/assets/screenshots/import/step-5-confirm-import.png',
  33: '/assets/screenshots/pbj/01-home-dashboard.png',
  34: '/assets/screenshots/pbj/03-budget-envelopes.png',
  35: '/assets/screenshots/budget-setup/step-4-categories.png',
  36: '/assets/screenshots/budget-setup/step-3-templates.png',
  37: '/assets/screenshots/budget/category-manager.png',
  38: '/assets/screenshots/budget/spending-plan.png',
  39: '/assets/screenshots/pbj/01-home-dashboard.png',
  40: '/assets/screenshots/pbj/06-goals-languages.png',
  41: '/assets/screenshots/pbj/06-goals-languages.png',
  42: '/assets/screenshots/pbj/06-goals-languages.png',
  43: '/assets/screenshots/goals/purchase-wishlist.png',
  44: '/assets/screenshots/pbj/01-home-dashboard.png',
  45: '/assets/screenshots/pbj/05-ai-coach.png',
  46: '/assets/screenshots/pbj/05-ai-coach.png',
  47: '/assets/screenshots/coach/weekly-recap.png',
  48: '/assets/screenshots/pbj/01-home-dashboard.png',
  49: '/assets/screenshots/wayfinding/wayfinding-quick-add.png',
  50: '/assets/screenshots/budget-setup/step-6-scan.png',
  51: '/assets/screenshots/budget-setup/step-6-scan.png',
  52: '/assets/screenshots/budget-setup/step-6-scan.png',
  53: '/assets/screenshots/budget-setup/step-6-scan.png',
  54: '/assets/screenshots/pbj/02-import-center.png',
  55: '/assets/screenshots/pbj/02-import-center.png',
  56: '/assets/screenshots/import/step-5-confirm-import.png',
  57: '/assets/screenshots/pbj/02-import-center.png',
  58: '/assets/screenshots/import/step-5-confirm-import.png',
  59: '/assets/screenshots/pbj/02-import-center.png',
  60: '/assets/screenshots/pbj/02-import-center.png',
  61: '/assets/screenshots/import/import-history.png',
  62: '/assets/screenshots/receipt-scanning/receipt-scan.png',
  63: '/assets/screenshots/receipt-scanning/receipt-scan.png',
  64: '/assets/screenshots/scanner.png',
  65: '/assets/screenshots/scanner.png',
  66: '/assets/screenshots/scanner.png',
  67: '/assets/screenshots/bills/bills-calendar.png',
  68: '/assets/screenshots/bills.png',
  69: '/assets/screenshots/bills/subscription-tracker.png',
  70: '/assets/screenshots/bills/bills-calendar.png',
  71: '/assets/screenshots/income/recurring-income.png',
  72: '/assets/screenshots/pbj/manual/pay-stub-review.png',
  73: '/assets/screenshots/pbj/manual/direct-deposit-advisor.png',
  74: '/assets/screenshots/debt/debt-planner.png',
  75: '/assets/screenshots/debt/debt-strategy.png',
  76: '/assets/screenshots/debt/loan-calculator.png',
  77: '/assets/screenshots/debt/debt-progress.png',
  78: '/assets/screenshots/reports/reports-hub.png',
  79: '/assets/screenshots/reports/spending-trends.png',
  80: '/assets/screenshots/reports/category-breakdown.png',
  81: '/assets/screenshots/reports/merchant-analysis.png',
  82: '/assets/screenshots/reports/financial-health-score.png',
  83: '/assets/screenshots/reports/custom-report-builder.png',
  84: '/assets/screenshots/net-worth/net-worth-hub.png',
  85: '/assets/screenshots/settings/how-pbj-learns.png',
  86: '/assets/screenshots/bank-sync.png',
  87: '/assets/screenshots/bank-sync.png',
  88: '/assets/screenshots/tax/tax-center.png',
  89: '/assets/screenshots/tax/tax-center.png',
  90: '/assets/screenshots/tax/mileage-log.png',
  91: '/assets/screenshots/tax/tax-center.png',
  92: '/assets/screenshots/settings/settings-open.png',
  93: '/assets/screenshots/settings/profile-accounts.png',
  94: '/assets/screenshots/household-sync/household-sync.png',
  95: '/assets/screenshots/settings/privacy-backup.png',
  96: '/assets/screenshots/settings/privacy-backup.png',
  97: '/assets/screenshots/settings/how-pbj-learns.png',
  98: '/assets/screenshots/bank-sync.png',
  99: '/assets/screenshots/bank-sync.png',
  100: '/assets/screenshots/bank-sync.png',
  101: '/assets/screenshots/rules/transaction-rules.png',
  102: '/assets/screenshots/rules/transaction-rules.png',
  103: '/assets/screenshots/rules/bookmarks.png',
  104: '/assets/screenshots/pbj/05-ai-coach.png',
  105: '/assets/screenshots/pbj/05-ai-coach.png',
  106: '/assets/screenshots/pbj/06-goals-languages.png',
  107: '/assets/screenshots/household-sync/household-sync.png',
  108: '/assets/screenshots/settings/privacy-backup.png',
  109: '/assets/screenshots/pbj/04-shopping-intelligence.png',
  110: '/assets/screenshots/pbj/07-web-companion.png',
  111: '/assets/screenshots/pbj/manual/notification-opt-in.png',
  112: '/assets/screenshots/household-sync/household-sync.png',
  113: '/assets/screenshots/wayfinding/wayfinding-header.png',
  114: '/assets/screenshots/settings/privacy-backup.png',
  115: '/assets/screenshots/pbj/manual/notification-opt-in.png',
  116: '/assets/screenshots/pbj/manual/widgets-watch.png',
  117: '/assets/screenshots/settings/privacy-backup.png',
  118: '/assets/screenshots/settings/privacy-backup.png',
  119: '/assets/screenshots/help/help-support.png',
};

/** idx → null (tap-none) | {x,y,label} */
const TAP = {
  0: null,
  1: { x: 50, y: 88, label: 'Next' },
  2: { x: 50, y: 88, label: 'Next' },
  3: { x: 50, y: 88, label: 'Next' },
  4: { x: 50, y: 88, label: 'Get Started' },
  5: null,
  6: { x: 72, y: 18, label: 'Disclaimer' },
  7: { x: 50, y: 92, label: 'Accept' },
  8: { x: 50, y: 90, label: 'Continue' },
  9: null,
  10: { x: 50, y: 94, label: 'Tab bar' },
  11: { x: 82, y: 7, label: 'Search & Coach' },
  12: { x: 12, y: 24, label: 'Open menu' },
  13: { x: 50, y: 40, label: 'Toolbox' },
  14: { x: 88, y: 78, label: 'Quick-add' },
  15: { x: 50, y: 78, label: 'Start trial' },
  16: { x: 50, y: 78, label: 'Allow' },
  17: { x: 91, y: 8, label: 'Settings' },
  18: { x: 50, y: 38, label: 'Name' },
  19: { x: 50, y: 42, label: 'Currency' },
  20: { x: 50, y: 55, label: 'Add account' },
  21: { x: 50, y: 42, label: 'Income' },
  22: { x: 50, y: 50, label: 'Add bill' },
  23: { x: 50, y: 48, label: 'Goal' },
  24: { x: 50, y: 55, label: 'Style' },
  25: { x: 50, y: 55, label: 'Continue' },
  26: { x: 50, y: 90, label: 'Finish' },
  27: null,
  28: { x: 12, y: 94, label: 'Activity' },
  29: null,
  30: { x: 88, y: 8, label: 'Filters' },
  31: { x: 50, y: 35, label: 'Row' },
  32: { x: 50, y: 88, label: 'Approve' },
  33: { x: 38, y: 94, label: 'Budget' },
  34: null,
  35: { x: 50, y: 50, label: 'Category' },
  36: { x: 50, y: 55, label: 'Template' },
  37: null,
  38: null,
  39: { x: 62, y: 94, label: 'Goals' },
  40: null,
  41: { x: 88, y: 88, label: 'Plus' },
  42: null,
  43: null,
  44: { x: 88, y: 94, label: 'Coach' },
  45: null,
  46: { x: 85, y: 24, label: 'Ask' },
  47: null,
  48: { x: 50, y: 88, label: 'Gold +' },
  49: { x: 85, y: 82, label: 'Gold +' },
  50: { x: 50, y: 30, label: 'Amount' },
  51: { x: 50, y: 50, label: 'Category' },
  52: { x: 50, y: 65, label: 'Split' },
  53: { x: 50, y: 92, label: 'Save' },
  54: { x: 50, y: 28, label: 'Import' },
  55: null,
  56: { x: 50, y: 55, label: 'PocketBudJet' },
  57: { x: 50, y: 65, label: 'Browse files' },
  58: { x: 50, y: 91, label: 'Confirm' },
  59: null,
  60: null,
  61: null,
  62: { x: 50, y: 22, label: 'Scan' },
  63: { x: 50, y: 88, label: 'Save' },
  64: { x: 50, y: 48, label: 'Scanner' },
  65: null,
  66: null,
  67: null,
  68: { x: 50, y: 70, label: 'Mark paid' },
  69: null,
  70: null,
  71: null,
  72: null,
  73: null,
  74: null,
  75: null,
  76: null,
  77: null,
  78: { x: 50, y: 18, label: 'Reports' },
  79: null,
  80: null,
  81: null,
  82: null,
  83: null,
  84: null,
  85: null,
  86: null,
  87: { x: 50, y: 55, label: 'Connect Bank' },
  88: null,
  89: null,
  90: null,
  91: null,
  92: { x: 91, y: 8, label: 'Settings' },
  93: null,
  94: null,
  95: { x: 50, y: 40, label: 'Backup' },
  96: { x: 50, y: 50, label: 'Storage' },
  97: null,
  98: null,
  99: { x: 50, y: 45, label: 'Connect Bank' },
  100: { x: 50, y: 70, label: 'Confirm' },
  101: { x: 50, y: 40, label: 'Rules' },
  102: null,
  103: null,
  104: null,
  105: null,
  106: null,
  107: null,
  108: { x: 50, y: 45, label: 'Mindful' },
  109: null,
  110: { x: 50, y: 50, label: 'Companion' },
  111: null,
  112: null,
  113: { x: 50, y: 8, label: 'Search' },
  114: null,
  115: null,
  116: null,
  117: { x: 50, y: 40, label: 'App lock' },
  118: null,
  119: null,
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

function assertAssets(narrLen) {
  const missing = [];
  for (let i = 0; i < narrLen; i++) {
    const src = IMG[i];
    if (!src) {
      missing.push({ i, reason: 'no mapping' });
      continue;
    }
    const abs = path.join(ROOT, src.replace(/^\//, ''));
    if (!fs.existsSync(abs)) missing.push({ i, src, reason: 'file missing' });
  }
  if (missing.length) {
    console.error('Missing assets:', missing);
    process.exit(1);
  }
}

function buildOpen({ active, idx, tap, showAt, duration }) {
  const cls = active ? 'slide active' : 'slide';
  if (!tap) return `<div class="${cls}" data-index="${idx}" data-tap-none>`;
  return (
    `<div class="${cls}" data-index="${idx}"` +
    ` data-tap-x="${tap.x}" data-tap-y="${tap.y}" data-tap-label="${tap.label || ''}"` +
    ` data-tap-show-at="${showAt}" data-tap-duration="${duration}">`
  );
}

function imgTag(src, eager) {
  const loading = eager ? 'eager' : 'lazy';
  return `<img src="${src}" alt="" loading="${loading}" decoding="async">`;
}

function main() {
  const narr = JSON.parse(fs.readFileSync(NARR_PATH, 'utf8'));
  assertAssets(narr.length);

  let html = fs.readFileSync(HTML_PATH, 'utf8');
  const ffmpeg = resolveFfmpeg();

  // Replace each slide block from opening <div class="slide... to closing </div> before next slide
  const slideOpenRe = /<div class="slide(?:\s+active)?"[^>]*>[\s\S]*?(?=<div class="slide|<\/div>\s*<\/div>\s*<\/div>\s*<div class="progress-track")/g;

  // Safer: rebuild slideshow inner slides only
  const startMark = '<div class="slideshow" id="slideshow">';
  const start = html.indexOf(startMark);
  if (start < 0) throw new Error('slideshow not found');
  const afterStart = start + startMark.length;
  // find tap-to-start block end, keep it
  const tapStartEnd = html.indexOf('</div>', html.indexOf('id="tapToStart"', afterStart)) + 6;
  const slidesEnd = html.indexOf('</div>\n </div>\n </div>\n <div class="progress-track"', tapStartEnd);
  // fallback search
  let end = slidesEnd;
  if (end < 0) {
    end = html.indexOf('<div class="progress-track"', tapStartEnd);
    // walk back to close slideshow children — find last </div> before progress
    // We'll instead regex-replace each data-index slide individually
  }

  const ffmpegOk = !!ffmpeg;
  let updated = 0;
  for (let i = 0; i < narr.length; i++) {
    const src = IMG[i];
    const tap = TAP[i] === undefined ? null : TAP[i];
    let showAt = 0.3;
    let duration = 2.5;
    if (tap && ffmpegOk) {
      const mp3 = path.join(AUDIO_DIR, `slide-${i}.mp3`);
      const sec = fs.existsSync(mp3) ? probeDuration(ffmpeg, mp3) : null;
      if (sec) {
        showAt = estimateShowAt(narr[i], sec);
        duration = estimateDuration(sec, showAt);
      }
    }

    const open = buildOpen({
      active: i === 0,
      idx: i,
      tap,
      showAt,
      duration,
    });
    const eager = i < 15;
    const body = `\n ${imgTag(src, eager)}\n`;

    const slideRe = new RegExp(
      `<div class="slide(?:\\s+active)?"[^>]*data-index="${i}"[^>]*>[\\s\\S]*?(?=\\n <div class="slide|\\n </div>\\n </div>\\n </div>)`,
      'm',
    );
    const next = `${open}${body}</div>`;
    if (!slideRe.test(html)) {
      console.warn('slide block not found for', i);
      continue;
    }
    html = html.replace(slideRe, next);
    updated++;
  }

  // Sync embedded NARRATION array if present
  const narrLiteral = JSON.stringify(narr, null, 1)
    .replace(/^\[/, '[\n ')
    .replace(/\n\]$/, '\n ]');
  html = html.replace(
    /const NARRATION = \[[\s\S]*?\];/,
    `const NARRATION = ${JSON.stringify(narr)};`,
  );

  // Sync transcript paragraphs
  for (let i = 0; i < narr.length; i++) {
    const esc = narr[i]
      .replace(/&/g, '&amp;')
      .replace(/</g, '&lt;')
      .replace(/>/g, '&gt;')
      .replace(/"/g, '&quot;');
    const tre = new RegExp(
      `(<p class="transcript-para(?: current)?" data-slide="${i}">)[\\s\\S]*?(</p>)`,
    );
    if (tre.test(html)) {
      html = html.replace(tre, `$1${esc}$2`);
    }
  }

  fs.writeFileSync(HTML_PATH, html);
  console.log(`Updated ${updated}/${narr.length} slides`);
  console.log('Assets base:', ASSETS);

  // Re-audit broken
  const broken = [];
  for (let i = 0; i < narr.length; i++) {
    const abs = path.join(ROOT, IMG[i].replace(/^\//, ''));
    if (!fs.existsSync(abs)) broken.push(i);
  }
  console.log('broken after:', broken.length ? broken : 'none');
}

main();
