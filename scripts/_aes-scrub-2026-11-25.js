/**
 * One-shot AES/encrypted-backup scrub (2026-11-25).
 * Replaces false AES / encrypted-backup claims with the locked honest line.
 * Does NOT touch video narration JSON / NARRATION arrays (report-only).
 */
const fs = require('fs');
const path = require('path');

const ROOT = path.join(__dirname, '..');
const CORRECT_EN =
  'Optional backups live in your own cloud storage — never on a JosspaTech server.';
const CORRECT_EN_RS =
  'Optional backups live in your own cloud storage &mdash; never on a JosspaTech server.';

const LOCALE_CORRECT = {
  es: 'Las copias de seguridad opcionales viven en tu propio almacenamiento en la nube — nunca en un servidor de JosspaTech.',
  de: 'Optionale Backups liegen in deinem eigenen Cloud-Speicher — nie auf einem JosspaTech-Server.',
  fr: 'Les sauvegardes facultatives restent dans votre propre stockage cloud — jamais sur un serveur JosspaTech.',
  pt: 'As cópias de segurança opcionais ficam no teu próprio armazenamento na nuvem — nunca num servidor JosspaTech.',
  zh: '可选备份保存在你自己的云存储中——绝不会放在 JosspaTech 服务器上。',
  it: 'I backup facoltativi restano nel tuo spazio di archiviazione cloud — mai su un server JosspaTech.',
  hi: 'वैकल्पिक बैकअप आपके अपने क्लाउड स्टोरेज में रहते हैं — कभी भी JosspaTech सर्वर पर नहीं।',
};

const replacements = [];

function add(file, from, to) {
  replacements.push({ file: path.normalize(file), from, to });
}

function walk(dir, pred, out = []) {
  for (const ent of fs.readdirSync(dir, { withFileTypes: true })) {
    if (ent.name === 'node_modules' || ent.name === '.git') continue;
    const p = path.join(dir, ent.name);
    if (ent.isDirectory()) walk(p, pred, out);
    else if (pred(p)) out.push(p);
  }
  return out;
}

// —— Exact English strings ——
const EN_PAIRS = [
  [
    'Optional cloud backup uses AES-256 encryption with a key only you know.',
    CORRECT_EN,
  ],
  [
    'Optional backups are encrypted files you own in your Google Drive or iCloud — not a JosspaTech cloud.',
    CORRECT_EN,
  ],
  [
    'Optional backups are encrypted files you own in your Google Drive or iCloud. If the app store listing ever goes away, you keep what is on the device and in your own backup.',
    `${CORRECT_EN} If the app store listing ever goes away, you keep what is on the device and in your own backup.`,
  ],
  [
    'On your device in PocketBudJet\'s private storage. We never store bank usernames or passwords. Optional cloud backup uses AES-256 encryption with a key only you know.',
    `On your device in PocketBudJet's private storage. We never store bank usernames or passwords. ${CORRECT_EN}`,
  ],
  [
    'On your device in PocketBudJet&rsquo;s private storage. We never store bank usernames or passwords. Optional cloud backup uses AES-256 encryption with a key only you know.',
    `On your device in PocketBudJet&rsquo;s private storage. We never store bank usernames or passwords. ${CORRECT_EN_RS}`,
  ],
  [
    'Backups are optional, opt-in, and AES-256 encrypted with a key only your client holds.',
    CORRECT_EN.replace('Optional backups', 'Backups are optional and'),
  ],
  [
    'Transactions live in PocketBudJet\'s private app storage on their phone. Backups are optional, opt-in, and AES-256 encrypted with a key only your client holds.',
    `Transactions live in PocketBudJet's private app storage on their phone. ${CORRECT_EN}`,
  ],
  [
    'Turn on backups or cloud sync and you pick the provider &mdash; payloads are always AES-256 encrypted with a key only you know.',
    `Turn on backups or cloud sync and you pick the provider &mdash; ${CORRECT_EN_RS}`,
  ],
  [
    'Optional encrypted backups live in your Drive or iCloud — not a JosspaTech cloud.',
    CORRECT_EN,
  ],
  [
    'Optional encrypted cloud backup uses a key only you know.',
    CORRECT_EN,
  ],
  [
    'Yes. Export CSV or JSON anytime. Optional encrypted cloud backup uses a key only you know. Your data is never locked in.',
    `Yes. Export CSV or JSON anytime. ${CORRECT_EN} Your data is never locked in.`,
  ],
  [
    '<strong>If you turn on backups or sync.</strong> You pick the cloud provider (iCloud, Google Drive, OneDrive, or Dropbox). Before anything leaves your device, the payload is compressed and encrypted with AES-256-CTR + HMAC-SHA256 using a key derived from a password <em>only you know</em>. JosspaTech has no copy of that password and cannot decrypt your backups.',
    `<strong>If you turn on backups or sync.</strong> You pick the cloud provider (iCloud, Google Drive, OneDrive, or Dropbox). ${CORRECT_EN}`,
  ],
  [
    '<div class="priv-title">AES-256 encryption</div>',
    `<div class="priv-title">Your cloud, your control</div>`,
  ],
  [
    '<div class="priv-desc">Backups are encrypted with a key only you hold. We can\'t read them — not even for support.</div>',
    `<div class="priv-desc">${CORRECT_EN}</div>`,
  ],
  [
    'Local-only encryption',
    'Data stays on your phone',
  ],
  [
    'Encrypted cloud backup',
    CORRECT_EN,
  ],
  [
    'Connect Google Drive, OneDrive, Dropbox, or iCloud for encrypted backup. Your cloud, your control.',
    `Connect Google Drive, OneDrive, Dropbox, or iCloud. ${CORRECT_EN}`,
  ],
];

// Locale FAQ JSON-LD / body replacements (full localized AES sentences → locale correct + keep device preface where present)
const LOCALE_FAQ_AES = {
  de: [
    [
      'Auf deinem Gerät im privaten Speicher von PocketBudJet. Wir speichern niemals Bank-Benutzernamen oder -Passwörter. Das optionale Cloud-Backup nutzt AES-256-Verschlüsselung mit einem Schlüssel, den nur du kennst.',
      `Auf deinem Gerät im privaten Speicher von PocketBudJet. Wir speichern niemals Bank-Benutzernamen oder -Passwörter. ${LOCALE_CORRECT.de}`,
    ],
    [
      'Transaktionen liegen im privaten App-Speicher von PocketBudJet auf dem Handy. Backups sind optional, müssen aktiv gewählt werden und sind AES-256-verschlüsselt, mit einem Schlüssel, den nur dein Kunde besitzt.',
      `Transaktionen liegen im privaten App-Speicher von PocketBudJet auf dem Handy. ${LOCALE_CORRECT.de}`,
    ],
  ],
  es: [
    [
      'En tu dispositivo, en el almacenamiento privado de PocketBudJet. Nunca guardamos nombres de usuario ni contraseñas del banco. La copia de seguridad opcional en la nube usa cifrado AES-256 con una clave que solo tú conoces.',
      `En tu dispositivo, en el almacenamiento privado de PocketBudJet. Nunca guardamos nombres de usuario ni contraseñas del banco. ${LOCALE_CORRECT.es}`,
    ],
    [
      'Las transacciones viven en el almacenamiento privado de la app PocketBudJet en su teléfono. Las copias de seguridad son opcionales, requieren activación y están cifradas con AES-256 con una clave que solo tiene tu cliente.',
      `Las transacciones viven en el almacenamiento privado de la app PocketBudJet en su teléfono. ${LOCALE_CORRECT.es}`,
    ],
  ],
  fr: [
    [
      'Sur votre appareil, dans le stockage privé de PocketBudJet. Nous ne stockons jamais d\'identifiants ni de mots de passe bancaires. La sauvegarde cloud facultative utilise un chiffrement AES-256 avec une clé que vous seul connaissez.',
      `Sur votre appareil, dans le stockage privé de PocketBudJet. Nous ne stockons jamais d'identifiants ni de mots de passe bancaires. ${LOCALE_CORRECT.fr}`,
    ],
    [
      'Les transactions résident dans le stockage privé de l\'appli PocketBudJet sur leur téléphone. Les sauvegardes sont facultatives, sur option, et chiffrées en AES-256 avec une clé que seul votre client détient.',
      `Les transactions résident dans le stockage privé de l'appli PocketBudJet sur leur téléphone. ${LOCALE_CORRECT.fr}`,
    ],
  ],
  pt: [
    [
      'No teu dispositivo, no armazenamento privado do PocketBudJet. Nunca guardamos nomes de utilizador nem palavras-passe do banco. A cópia de segurança opcional na nuvem usa encriptação AES-256 com uma chave que só tu conheces.',
      `No teu dispositivo, no armazenamento privado do PocketBudJet. Nunca guardamos nomes de utilizador nem palavras-passe do banco. ${LOCALE_CORRECT.pt}`,
    ],
    [
      'As transações ficam no armazenamento privado da app PocketBudJet no telemóvel deles. As cópias de segurança são opcionais, têm de ser ativadas e estão encriptadas com AES-256 com uma chave que só o teu cliente tem.',
      `As transações ficam no armazenamento privado da app PocketBudJet no telemóvel deles. ${LOCALE_CORRECT.pt}`,
    ],
  ],
  zh: [
    [
      '保存在你设备上 PocketBudJet 的私有存储中。我们从不存储银行用户名或密码。可选的云备份使用 AES-256 加密，密钥只有你自己知道。',
      `保存在你设备上 PocketBudJet 的私有存储中。我们从不存储银行用户名或密码。${LOCALE_CORRECT.zh}`,
    ],
    [
      '交易保存在他们手机上 PocketBudJet 的私有应用存储中。备份是可选的、需主动开启，并使用 AES-256 加密，密钥只有你的客户持有。',
      `交易保存在他们手机上 PocketBudJet 的私有应用存储中。${LOCALE_CORRECT.zh}`,
    ],
  ],
  it: [
    [
      'Sul tuo dispositivo, nell\'archivio privato di PocketBudJet. Non memorizziamo mai nomi utente o password della banca. Il backup cloud facoltativo usa la crittografia AES-256 con una chiave che conosci solo tu.',
      `Sul tuo dispositivo, nell'archivio privato di PocketBudJet. Non memorizziamo mai nomi utente o password della banca. ${LOCALE_CORRECT.it}`,
    ],
    [
      'Le transazioni risiedono nell\'archivio privato dell\'app PocketBudJet sul loro telefono. I backup sono facoltativi, da attivare volontariamente e cifrati con AES-256 con una chiave che solo il tuo cliente possiede.',
      `Le transazioni risiedono nell'archivio privato dell'app PocketBudJet sul loro telefono. ${LOCALE_CORRECT.it}`,
    ],
  ],
  hi: [
    [
      'आपके डिवाइस पर, PocketBudJet के निजी स्टोरेज में। हम बैंक यूज़रनेम या पासवर्ड कभी स्टोर नहीं करते। वैकल्पिक क्लाउड बैकअप AES-256 एन्क्रिप्शन इस्तेमाल करता है, जिसकी कुंजी सिर्फ़ आपको पता है।',
      `आपके डिवाइस पर, PocketBudJet के निजी स्टोरेज में। हम बैंक यूज़रनेम या पासवर्ड कभी स्टोर नहीं करते। ${LOCALE_CORRECT.hi}`,
    ],
    [
      'लेन-देन उनके फ़ोन पर PocketBudJet के निजी ऐप स्टोरेज में रहते हैं। बैकअप वैकल्पिक हैं, चुनकर चालू करने होते हैं और AES-256 से एन्क्रिप्टेड हैं, जिसकी कुंजी सिर्फ़ आपके क्लाइंट के पास है।',
      `लेन-देन उनके फ़ोन पर PocketBudJet के निजी ऐप स्टोरेज में रहते हैं। ${LOCALE_CORRECT.hi}`,
    ],
  ],
};

const SKIP_NARRATION = [
  path.normalize('videos/pbj/user-guide/index-slides.html'),
  path.normalize('videos/pbj/user-guide/narration-en.json'),
  path.normalize('videos/pbj/user-guide/_shot-map.json'),
];

const targets = [
  ...walk(ROOT, (p) => p.endsWith('.html')),
  ...walk(path.join(ROOT, 'scripts'), (p) =>
    /\.(mjs|js|json)$/.test(p) && !p.includes('_aes-scrub'),
  ),
  ...walk(path.join(ROOT, 'videos'), (p) =>
    /\.(js|json|html)$/.test(p) && !SKIP_NARRATION.some((s) => p.replace(/\\/g, '/').endsWith(s.replace(/\\/g, '/'))),
  ),
];

const report = [];
let filesChanged = 0;

for (const file of targets) {
  const rel = path.relative(ROOT, file).replace(/\\/g, '/');
  if (SKIP_NARRATION.some((s) => rel === s.replace(/\\/g, '/'))) continue;
  // Skip narration-bearing index-slides entirely (spoken lines = report only)
  if (rel.includes('user-guide/index-slides.html')) continue;
  if (rel.includes('user-guide/narration-') || rel.includes('_shot-map.json')) continue;

  let text = fs.readFileSync(file, 'utf8');
  const before = text;
  for (const [from, to] of EN_PAIRS) {
    if (text.includes(from)) text = text.split(from).join(to);
  }
  for (const pairs of Object.values(LOCALE_FAQ_AES)) {
    for (const [from, to] of pairs) {
      if (text.includes(from)) text = text.split(from).join(to);
    }
  }
  // Remaining generic English FAQ trailer still on localized FAQ pages
  if (text.includes('Optional backups are encrypted files you own in your Google Drive or iCloud — not a JosspaTech cloud.')) {
    text = text.split(
      'Optional backups are encrypted files you own in your Google Drive or iCloud — not a JosspaTech cloud.',
    ).join(CORRECT_EN);
  }
  if (text !== before) {
    fs.writeFileSync(file, text, 'utf8');
    filesChanged += 1;
    report.push(rel);
  }
}

console.log(JSON.stringify({ filesChanged, files: report }, null, 2));
