/**
 * Unscribe product pages (EN + 7 locales): snapshot model + PBJ demo caption.
 *  - "First five free" is gone. The model is: one free first look (one import), then Pro.
 *  - Part 7: caption under the PBJ share-a-statement video (the video is already on every page).
 * Translations are NOT typed here. They come from Unscribe's scripts/i18n_sync.js --strings (Azure Translator):
 *   node <Unscribe>/scripts/i18n_sync.js --strings=C:\g\tmp\unscribe\site_en.json --out=C:\g\tmp\unscribe\site_tr.json
 * Price sentences and the "no monthly plan" sentence keep the existing localized text on each page.
 * Run: node scripts/_unscribe-snapshot-2026-11-26.js [--dry-run]
 */
const fs = require('fs');
const path = require('path');

const ROOT = path.join(__dirname, '..');
const DRY = process.argv.includes('--dry-run');
const TR = JSON.parse(fs.readFileSync('C:\\g\\tmp\\unscribe\\site_tr.json', 'utf8'));
const LOCALES = ['es', 'zh', 'de', 'fr', 'pt', 'it', 'hi'];

const EN = {
  chip: 'Free first look',
  proA: 'Share a statement to Unscribe and see what it can do for you. Your first import is a free first look: you can look through everything it finds, with your totals.',
  proB: 'Pro keeps the dates live, sends reminders, flags price increases and duplicates, makes the cancel buttons work (each one opens that service’s own cancellation page), lets you import as often as you like, and exports to CSV.',
  faqCostFirst: 'Your first import is a free first look.',
  faqFreeA: 'Free first look: one import. You can look through everything it finds, with your totals. After that the list is saved as it was: dates stop moving, there are no reminders, and no more imports.',
  faqFreeB: 'Pro: live dates, reminders, price-increase and duplicate flags, cancel buttons that open each service’s own cancellation page, unlimited imports, and CSV export.',
  faqCancel: 'Open that subscription’s detail and tap the cancel button (Pro). It opens that service’s own cancellation page. Unscribe does not cancel for you.',
  demoNote: 'Demo filmed with PocketBudJet — Unscribe works exactly the same way. Just choose Unscribe when you share, instead of PBJ.',
};
const DEMO_STYLE = 'font-size:0.8rem;opacity:0.85;margin:0.5rem 0 0';

function must(cond, msg) {
  if (!cond) throw new Error(msg);
}

function splitSentences(text) {
  return text.split(/(?<=[.。।])\s*(?=[^\s\d.])/).map((s) => s.trim()).filter(Boolean);
}

function edit(file, loc) {
  const t = loc === 'en' ? EN : TR[loc];
  must(t, `no translations for ${loc}`);
  const join = (...parts) => parts.join(loc === 'zh' ? '' : ' ');
  let html = fs.readFileSync(file, 'utf8');
  must(!html.includes(t.proA), `${file}: already applied`);

  // 1. trust chip (3rd item)
  html = html.replace(/(<ul class="trust-chips[^>]*>\s*(?:<li>[^<]*<\/li>\s*){2})<li>[^<]*<\/li>/, `$1<li>${t.chip}</li>`);

  // 2. Pro paragraph
  html = html.replace(/(<h2>Pro<\/h2>\s*<p>)([\s\S]*?)(<\/p>)/, (_, a, body, c) => {
    let next;
    if (loc === 'en') {
      next = join(t.proA, '<strong>Pro is $29.99 once, or $9.99 a year.</strong>', 'No monthly plan.', t.proB);
    } else {
      const s = splitSentences(body);
      must(s.length === 5, `${file}: Pro paragraph has ${s.length} sentences: ${body}`);
      next = join(t.proA, s[1], s[2], t.proB);
    }
    return a + next + c;
  });

  // 3-5. FAQ answers, by their <details> position / link
  let n = 0;
  html = html.replace(/<details>\s*<summary>([^<]*)<\/summary>\s*<p>([\s\S]*?)<\/p>\s*<\/details>/g, (whole, sum, body) => {
    n++;
    if (n === 1) {
      // How much does it cost? Swap the first sentence only.
      const s = splitSentences(body);
      must(s.length >= 3, `${file}: cost FAQ sentences ${s.length}`);
      return whole.replace(body, join(t.faqCostFirst, ...s.slice(1)));
    }
    if (n === 2) {
      // What's free vs Pro?
      return whole.replace(body, join(t.faqFreeA, t.faqFreeB));
    }
    if (/#(?:[a-z]{2}\/)?detail-cancel/.test(body)) {
      const link = body.slice(body.indexOf('<a '));
      return whole.replace(body, join(t.faqCancel, link));
    }
    return whole;
  });

  // 6. Part 7 caption under the PBJ demo video
  const demo = /(<div class="howto-preview[^>]*id="howto-share-statement">[\s\S]*?<\/video>)(\s*<\/div>)/;
  must(demo.test(html), `${file}: PBJ demo video block not found`);
  html = html.replace(demo, `$1\n      <p class="howto-cap howto-demo-note" style="${DEMO_STYLE}">${t.demoNote}</p>$2`);

  must(!/\bfive\b|fünf|cinco|cinq|cinque|前五|पाँच/i.test(html.replace(/<script[\s\S]*?<\/script>/g, '')), `${file}: a "five" claim is still on the page`);
  if (!DRY) fs.writeFileSync(file, html);
  console.log('ok', path.relative(ROOT, file));
}

edit(path.join(ROOT, 'unscribe', 'index.html'), 'en');
for (const loc of LOCALES) edit(path.join(ROOT, 'unscribe', loc, 'index.html'), loc);
