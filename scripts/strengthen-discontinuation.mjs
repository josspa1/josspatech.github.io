/**
 * Strengthen discontinuation language across JosspaTech app Terms + EULAs.
 * Run from josspatech.github.io root: node scripts/strengthen-discontinuation.mjs
 */
import fs from 'fs';
import path from 'path';
import { fileURLToPath } from 'url';

const ROOT = path.resolve(path.dirname(fileURLToPath(import.meta.url)), '..');
const HOSTED = 'C:/Users/jossp/Documents/MobileApps/WebSite/HostedFiles';

const TERMS_DISCONTINUE = {
  hhh: {
    file: 'docs/handyhorology/HandyHorologyHelper_TermsOfService.html',
    services:
      'including AI identification, cloud backup relays, community sync, or eBay integrations',
    dataExport:
      'you may export your collection using the App’s backup tools at any time before or after discontinuation',
    freeLine: true,
    survive:
      'The provisions of Sections 2 (Not Professional Advice), 3 (Accuracy of Information), 4 (Limitation of Liability), 6 (Intellectual Property), 8 (AI, Market Data, and Third-Party Services), and this Section 9 survive termination or discontinuation.',
  },
  pbj: {
    file: 'docs/pocketbudjet/PocketBudJet_TermsOfService.html',
    services:
      'including cloud OCR, AI Coach, crowd benchmarks, bank sync / Teller relay, or cloud backup',
    dataExport: 'you may export your data as CSV or JSON at any time',
    freeLine: true,
    survive:
      'The provisions of Sections 2 (Not Financial Advice), 3 (Accuracy of Calculations), 4 (Limitation of Liability), 6 (Intellectual Property), 8 (Bank Account Connectivity), and this Section 9 survive termination or discontinuation.',
  },
  cvc: {
    file: 'docs/curatorsvault/CuratorsVault_TermsOfService.html',
    services:
      'including AI identification, cert lookups, cloud backup, community sync, or marketplace integrations',
    dataExport:
      'you may export your collection using the App’s backup tools at any time before or after discontinuation',
    freeLine: true,
    survive:
      'The provisions of Sections addressing disclaimers, limitation of liability, intellectual property, third-party services, and this Section 9 survive termination or discontinuation.',
  },
};

function discontinueBlock({ services, dataExport, freeLine, survive }) {
  const free = freeLine
    ? `<li>Users on the Free tier or an expired trial who have not converted to a paid subscription are not owed a refund, because no paid subscription payment was made.</li>
    `
    : '';
  return `<p><strong>If JosspaTech discontinues the App.</strong> JosspaTech may, at its sole discretion, at any time, and for any reason or for no reason, with or without prior notice (except where notice is required by law or by Apple / Google store policy), cease publishing, updating, supporting, or operating the App or any feature of it. This applies to all users regardless of pricing tier — Free, trial, or paid subscription. In that event:</p>
  <ul>
    <li><strong>Good-faith refund intent.</strong> Where practicable, JosspaTech will use commercially reasonable efforts to arrange a pro-rata refund of the unused portion of an active paid subscriber’s then-current billing period (for example, remaining days on a monthly plan or remaining months on an annual plan) through Apple App Store or Google Play, in accordance with each platform’s refund procedures and policies.</li>
    <li><strong>No guaranteed refund.</strong> JosspaTech does <strong>not</strong> guarantee that any refund will be available or completed. Refunds depend on Apple’s and Google’s systems, policies, and cooperation; on JosspaTech’s ability to identify and process eligible subscriptions; and on circumstances beyond JosspaTech’s reasonable control (including platform outages, account or identity issues, insolvency or wind-down constraints, force majeure, legal or regulatory restraints, or other events that make refunds impracticable or impossible). To the maximum extent permitted by law, JosspaTech has <strong>no obligation</strong> to issue refunds from its own funds, to guarantee store refunds, or to continue operating any billing relationship solely to facilitate refunds.</li>
    ${free}<li>To the maximum extent permitted by law, any store-processed pro-rata refund that may be obtained — or, if none is obtainable, the absence of a refund — is your <strong>sole and exclusive remedy</strong> for discontinuation of the App.</li>
    <li>JosspaTech has <strong>no obligation</strong> to continue developing, supporting, updating, or operating the App; to maintain any server-side service (${services}); to provide replacement software; or to transition users to a successor product.</li>
    <li>Because data is stored locally on your device by default, discontinuation of the App does not delete data already on your device. You may continue to use the last-installed version on your device subject to your device’s and operating system’s compatibility, and ${dataExport}.</li>
  </ul>
  <p>${survive}</p>`;
}

function eulaDiscontinueSection() {
  return `<h2>9. Termination and App Discontinuation</h2>
  <p>This EULA is effective until terminated. Your rights under this EULA will terminate automatically without notice from JosspaTech if you fail to comply with any of its terms. Upon termination, you must cease all use of the App and destroy all copies in your possession.</p>
  <p><strong>App discontinuation.</strong> JosspaTech may, at its sole discretion, at any time, and for any reason or for no reason, with or without prior notice (except where required by law or store policy), cease publishing, updating, supporting, or operating the App or any feature of it, for all users including Free, trial, and paid subscribers.</p>
  <p><strong>Refunds on discontinuation.</strong> Where practicable, JosspaTech will use commercially reasonable efforts to arrange a pro-rata refund of the unused portion of an active paid subscriber’s then-current billing period through Apple or Google under their policies. JosspaTech does <strong>not</strong> guarantee any refund. To the maximum extent permitted by law, JosspaTech has <strong>no obligation</strong> to issue refunds from its own funds, to guarantee store refunds, to continue any service solely to process refunds, to provide replacement software, or to transition users to a successor product. Any store refund obtained — or the absence of a refund if none is obtainable — is your sole and exclusive remedy for discontinuation, to the maximum extent permitted by law. See also the App’s Terms of Service.</p>`;
}

function patchTermsHhhPbjCvc() {
  for (const [key, cfg] of Object.entries(TERMS_DISCONTINUE)) {
    const p = path.join(ROOT, cfg.file);
    let html = fs.readFileSync(p, 'utf8');
    const start = html.indexOf('<p><strong>If JosspaTech discontinues the App.</strong>');
    if (start < 0) throw new Error('missing discontinue start: ' + cfg.file);
    const after = html.indexOf('<h2>', start + 10);
    if (after < 0) throw new Error('missing next h2: ' + cfg.file);
    const block = discontinueBlock(cfg);
    html = html.slice(0, start) + block + '\n\n  ' + html.slice(after);
    html = html.replace(/Effective Date:[^<]+/, 'Effective Date: August 4, 2026');
    fs.writeFileSync(p, html);
    console.log('patched Terms', key);
  }
}

function patchPalTerms() {
  const p = path.join(ROOT, 'docs/pal/PocketAllowanceLedger_TermsOfService.html');
  let html = fs.readFileSync(p, 'utf8');
  const start = html.indexOf('<h2>8. Discontinuation</h2>');
  if (start < 0) throw new Error('PAL discontinue h2 not found');
  const after = html.indexOf('<h2>9. Changes</h2>');
  if (after < 0) throw new Error('PAL changes h2 not found');
  const neu =
    `<h2>8. Termination and App Discontinuation</h2>
  <p><strong>By you.</strong> You may stop using the App at any time. Cancel paid subscriptions through your App Store or Google Play account. Uninstalling removes local data on that device unless you have exported a backup.</p>
  <p><strong>By JosspaTech for cause.</strong> JosspaTech reserves the right to terminate or suspend your access to the App for violations of these Terms, without refund.</p>
  ` +
    discontinueBlock({
      services:
        'including any optional cloud, sync, or companion-related services that may be offered',
      dataExport: 'you may export any backups you need before uninstalling',
      freeLine: true,
      survive:
        'Provisions that by nature should survive (ownership, disclaimers, limitation of liability, and this Section 8) survive termination or discontinuation.',
    });
  html = html.slice(0, start) + neu + '\n\n  ' + html.slice(after);
  html = html.replace(/Effective Date:[^<]+/, 'Effective Date: August 4, 2026');
  html = html.replace(
    'Unless required by law, fees are non-refundable once charged by the store.',
    'Unless required by law or store policy, fees are non-refundable once charged by the store, except that if JosspaTech discontinues the App, Section 8 (good-faith pro-rata efforts / no guaranteed refund) applies.',
  );
  fs.writeFileSync(p, html);
  console.log('patched PAL Terms');
}

function patchAllEulas() {
  const files = [
    'docs/handyhorology/HandyHorologyHelper_EULA.html',
    'docs/pocketbudjet/PocketBudJet_EULA.html',
    'docs/curatorsvault/CuratorsVault_EULA.html',
    'docs/pal/PocketAllowanceLedger_EULA.html',
  ];
  const neu = eulaDiscontinueSection();
  for (const rel of files) {
    const p = path.join(ROOT, rel);
    let html = fs.readFileSync(p, 'utf8');
    let start = html.indexOf('<h2>9. Termination and App Discontinuation</h2>');
    if (start < 0) start = html.indexOf('<h2>9. Termination</h2>');
    if (start < 0) throw new Error('no termination h2: ' + rel);
    const after = html.indexOf('<h2>10.', start);
    if (after < 0) throw new Error('no h2 10: ' + rel);
    html = html.slice(0, start) + neu + '\n\n  ' + html.slice(after);
    html = html.replace(/Effective Date:[^<]+/, 'Effective Date: August 4, 2026');
    fs.writeFileSync(p, html);
    console.log('patched EULA', rel);
  }
}

patchTermsHhhPbjCvc();
patchPalTerms();
patchAllEulas();

const mirrors = [
  'docs/handyhorology/HandyHorologyHelper_TermsOfService.html',
  'docs/handyhorology/HandyHorologyHelper_EULA.html',
  'docs/pocketbudjet/PocketBudJet_TermsOfService.html',
  'docs/pocketbudjet/PocketBudJet_EULA.html',
  'docs/curatorsvault/CuratorsVault_TermsOfService.html',
  'docs/curatorsvault/CuratorsVault_EULA.html',
  'docs/pal/PocketAllowanceLedger_TermsOfService.html',
  'docs/pal/PocketAllowanceLedger_EULA.html',
];
for (const rel of mirrors) {
  const src = path.join(ROOT, rel);
  const dst = path.join(HOSTED, rel);
  fs.mkdirSync(path.dirname(dst), { recursive: true });
  fs.copyFileSync(src, dst);
  console.log('mirrored', rel);
}

console.log('DONE');
