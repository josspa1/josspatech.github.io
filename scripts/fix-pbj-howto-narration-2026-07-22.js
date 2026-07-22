#!/usr/bin/env node
'use strict';
/**
 * PocketBudJet User Manual: keep narration as step-by-step how-to (no tech dump).
 * Also rewrites partner-showcase EN overview lines to match slides.
 */
const fs = require('fs');
const path = require('path');

const ROOT = path.resolve(__dirname, '..');
const GUIDE_HTML = path.join(ROOT, 'videos', 'user-guide', 'index.html');
const GUIDE_JSON = path.join(ROOT, 'videos', 'user-guide', 'narration-en.json');
const LOCALES = path.join(ROOT, 'videos', 'pocketbudjet', 'partner-showcase', 'locales.json');

const GUIDE_UPDATES = {
  0: 'Open PocketBudJet after install. Wait for the splash screen, then continue.',
  57: 'Or tap Import from file and pick a bank statement from Files or Downloads. Confirm the columns look right, then continue.',
  64: 'For stacks of paper, open the document scanner in Toolbox and follow the on-screen steps to bring pages in.',
  66: 'Universal Scan works for statements, invoices, and mixed documents — crop the corners, review, then import.',
  85: 'How PocketBudJet Learns shows how categories improve as you correct them — your numbers stay on your phone.',
  86: 'Bank sync is for US banks with paid Premium — not included in the free trial. Two banks are included; each extra bank is an add-on.',
  87: 'In Settings, tap Connect Bank. Search for your US bank and sign in securely — PocketBudJet never stores your bank password.',
  94: 'Household sync lets you share a budget with a partner on the same plan. Follow the invite steps on each phone.',
  107: 'Couples Dashboard shows shared envelopes and who spent what — each phone still keeps its own local copy.',
  111: 'Notification Capture can turn bank alerts into draft transactions — turn it on in Settings if you want it.',
  114: 'Connect Google Drive, OneDrive, Dropbox, or iCloud for encrypted backup. Your cloud account, your control.',
};

const OVERVIEW_NARRATIONS = [
  'Welcome to PocketBudJet — private budgeting on your phone. Watch this short tour, then use the User Manual when you want step-by-step help.',
  'Open Activity to see every dollar — categories and accounts that make sense at a glance.',
  'On Budget, set envelope limits and watch progress fill in as you spend.',
  'Track debt payoff and savings goals so you can see freedom on a timeline.',
  'Ask the Coach in plain English — how you are doing this month, where you overspent, what to prioritize next.',
  'When you buy something, PocketBudJet can show where that item costs less nearby or online.',
  'Choose a look you like — classic navy and gold, grape and honey, or true OLED black.',
  'Swipe the home cards — money-flow, spending breakdown, busiest days, and bills due this month.',
  'It surfaces recurring subscriptions from your spending and gives you a find-how-to-cancel path. You stay in control.',
  'When you need more, bank sync, tax exports, household sharing, and other tools are ready in the app.',
  'Start free. Unlock Premium when you are ready — cancel anytime from your store subscriptions.',
];

const OVERVIEW_CAPTIONS = [
  { tag: 'WELCOME', h2: 'PocketBudJet' },
  { tag: 'ACTIVITY', h2: 'See every dollar' },
  { tag: 'BUDGET', h2: 'Budget with depth' },
  { tag: 'GOALS', h2: 'Freedom on a timeline' },
  { tag: 'COACH', h2: 'Your Coach' },
  { tag: 'SAVE', h2: 'Lowest price near you' },
  { tag: 'LOOK', h2: 'Pick your look' },
  { tag: 'HOME', h2: 'Swipe the carousel' },
  { tag: 'BILLS', h2: 'Subscriptions surfaced' },
  { tag: 'MORE', h2: 'More when you need it' },
  { tag: 'START', h2: 'Start free' },
];

function escapeJs(s) {
  return s.replace(/\\/g, '\\\\').replace(/"/g, '\\"');
}

// --- User Manual ---
const narr = JSON.parse(fs.readFileSync(GUIDE_JSON, 'utf8'));
const changed = [];
for (const [k, text] of Object.entries(GUIDE_UPDATES)) {
  const i = Number(k);
  if (narr[i] !== text) {
    narr[i] = text;
    changed.push(i);
  }
}
fs.writeFileSync(GUIDE_JSON, JSON.stringify(narr, null, 2) + '\n');

let html = fs.readFileSync(GUIDE_HTML, 'utf8');
const start = html.indexOf('const NARRATION = [');
const end = html.indexOf('];', start);
if (start < 0 || end < 0) throw new Error('NARRATION not found');
const body = narr.map((t) => ' "' + escapeJs(t) + '",').join('\n');
html = html.slice(0, start) + 'const NARRATION = [\n' + body + '\n' + html.slice(end);
fs.writeFileSync(GUIDE_HTML, html);

// --- Partner showcase overview ---
const locales = JSON.parse(fs.readFileSync(LOCALES, 'utf8'));
locales.locales.en.narrations = OVERVIEW_NARRATIONS;
locales.locales.en.captions = OVERVIEW_CAPTIONS;
locales.locales.en.overlayTagline = 'Private budgeting that stays on your phone.';
locales.locales.en.featureNote = 'More tools when you need them';
locales.locales.en.themeLabels = [
  'Classic navy & gold',
  'Grape & honey PBJ',
  'True OLED black',
];
locales.locales.en.eyeLabels = [
  'Home hero',
  'Where money went',
  'Donut chart breakdown',
  'Top merchants',
  'Weekly patterns',
];
fs.writeFileSync(LOCALES, JSON.stringify(locales, null, 2) + '\n');

// Keep HTML captions in sync for first paint before locale apply
let ov = fs.readFileSync(path.join(ROOT, 'videos', 'pocketbudjet', 'partner-showcase', 'index.html'), 'utf8');
ov = ov.replace(
  'A Mack truck of features — that handles like a Porsche.',
  'Private budgeting that stays on your phone.',
);
ov = ov.replace('102 features total · 7 shown here', 'More tools when you need them');
fs.writeFileSync(path.join(ROOT, 'videos', 'pocketbudjet', 'partner-showcase', 'index.html'), ov);

console.log('Guide slides updated:', changed.join(', ') || '(none)');
console.log('Partner-showcase EN overview narrations rewritten (11 slides).');
