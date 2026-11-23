/**
 * One-shot publisher: five English-only wave-1 blog posts.
 * No locale strips / no translations.
 */
import fs from 'node:fs';
import path from 'node:path';
import { fileURLToPath } from 'node:url';

const root = path.resolve(path.dirname(fileURLToPath(import.meta.url)), '..');
const DATE = '2026-11-23';

function shell({ title, description, canonicalPath, ogImage, appLabel, appHref, bodyHtml }) {
  const desc = description.slice(0, 160);
  return `<!DOCTYPE html>
<html lang="en">
<head>
<script src="/scripts/heycatch-store-queue.js"></script><link rel="modulepreload" href="/scripts/vendor/heycatch-sdk-0.8.5.js"><script type="module" src="/scripts/heycatch-init.js?v=13"></script>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>${title} — JosspaTech</title>
<meta name="description" content="${escAttr(desc)}">
<meta name="robots" content="index, follow, max-image-preview:large, max-snippet:-1">
<link rel="canonical" href="https://josspatech.com${canonicalPath}">
<meta name="author" content="JosspaTech">
<meta name="theme-color" content="#0C3358">
<link rel="icon" href="/assets/brand/josspatech-mark-app.svg?v=jt2star" type="image/svg+xml">
<link rel="stylesheet" href="/assets/product-landing.css?v=polish26">
<link rel="stylesheet" href="/blog/blog.css">

<meta property="og:type" content="article">
<meta property="og:locale" content="en_US">
<meta property="og:title" content="${escAttr(title)}">
<meta property="og:description" content="${escAttr(desc)}">
<meta property="og:url" content="https://josspatech.com${canonicalPath}">
<meta property="og:site_name" content="JosspaTech">
<meta property="og:image" content="https://josspatech.com${ogImage}">
<meta property="article:published_time" content="${DATE}">

<meta name="twitter:card" content="summary_large_image">
<meta name="twitter:title" content="${escAttr(title)}">
<meta name="twitter:description" content="${escAttr(desc)}">
<meta name="twitter:image" content="https://josspatech.com${ogImage}">

<script type="application/ld+json">
${JSON.stringify({
  '@context': 'https://schema.org',
  '@type': 'BlogPosting',
  headline: title,
  datePublished: DATE,
  description: desc,
  author: { '@type': 'Organization', name: 'JosspaTech' },
  publisher: {
    '@type': 'Organization',
    name: 'JosspaTech',
    logo: { '@type': 'ImageObject', url: 'https://josspatech.com/assets/brand/josspatech-logo-512.png' },
  },
  mainEntityOfPage: `https://josspatech.com${canonicalPath}`,
})}
</script>
</head>
<body>
  <header>
    <nav><a href="/">JosspaTech</a> · <a href="/blog/">Blog</a></nav>
  </header>
  <main>
    <article class="blog-post">
      <h1>${title}</h1>
      <p class="meta">${DATE} · ${appLabel}</p>
${bodyHtml}
      <div class="cta-app">
        <p>Built by JosspaTech — private apps that keep your data on your device.</p>
        <p><a href="${appHref}">See the app</a> <a href="/blog/">More articles</a></p>
      </div>
    </article>
  </main>
  <footer class="foot">
    <p><a href="/blog/">Blog</a> · <a href="/">JosspaTech home</a> · <a href="mailto:support@josspatech.com">support@josspatech.com</a></p>
  </footer>
  <script src="/scripts/site-analytics-saas.js?v=13" defer></script>
</body>
</html>
`;
}

function escAttr(s) {
  return s.replace(/&/g, '&amp;').replace(/"/g, '&quot;').replace(/</g, '&lt;');
}

const posts = [
  {
    slug: 'error-coins-in-your-change',
    title: 'Error Coins You Can Find in Your Change',
    app: "Curator's Vault",
    appHref: '/cvc/',
    ogImage: '/assets/brand/og-josspatech.jpg',
    excerpt:
      'Doubled dies, off-centers, broadstrikes, and wrong planchets still turn up in pocket change. How to check a suspect coin by hand — and when a photo ID and vault entry replace the lookup stack.',
    body: `
      <div class="takeaways">
<h2>Key takeaways</h2>
<ul>
<li>Error coins are minting mistakes that left the Mint — doubled dies, off-centers, broadstrikes, clipped planchets, and wrong-metal strikes are the types that still show up in change.</li>
<li>Most odd-looking coins are damage, not mint errors: scratches, corrosion, and post-mint bends do not raise value the way a verified minting fault can.</li>
<li>A hand check uses weight, diameter, edge, and magnification against published varieties; the slow step is matching the exact variety and logging a value you can find again later.</li>
<li>Curator's Vault identifies a coin from a photo, returns a value estimate with the cues it used, and stores the piece in your vault on the device.</li>
<li>Keep hand-sorting for a quick reject pile. Use the vault when you need an ID, a number, and a catalog entry that stays with the coin.</li>
</ul>
<p>Most coins in change are common. A few leave the Mint with a wrong die, a wrong planchet, or a misaligned strike. This article names the error types that still turn up in pocket change, shows the hand checks collectors use, and marks the point where looking the piece up by hand becomes a stack of tabs and notes.</p>
</div>

<h2>What counts as an error coin (and what does not)</h2>
<p>An error coin is a piece that left the United States Mint with a minting fault: a doubled die, an off-center strike, a broadstrike, a clipped planchet, or a planchet of the wrong metal or denomination. Damage after the coin left the Mint — scratches, acid etching, jewelry holes, or machine marks — is not an error. Collectors price mint errors; they discount or ignore post-mint damage.</p>
<h3>Common error types in circulating change</h3>
<ul>
<li><strong>Doubled die</strong> — design elements appear doubled because the die was hubbed twice out of register. Famous examples include certain Lincoln cent dates; most doubling you see under a loupe is machine doubling, which is not the same variety.</li>
<li><strong>Off-center</strong> — the blank was not centered under the dies, so part of the design is missing and blank planchet shows.</li>
<li><strong>Broadstrike</strong> — struck without a collar, so the coin spreads wider than normal diameter and often lacks a full edge reed.</li>
<li><strong>Clipped planchet</strong> — the blank was punched overlapping a previous punch or the strip edge, leaving a curved or straight missing section.</li>
<li><strong>Wrong planchet / wrong metal</strong> — a blank meant for another denomination or alloy was fed into the press (for example, a cent struck on a dime planchet).</li>
</ul>
<h3>Damage that fools people</h3>
<p>Corrosion, plating loss, heat, and intentional alteration can look dramatic and still be worth face value. Weight and diameter that match the published specs for that denomination, plus a clean strike under magnification, separate a candidate from a damaged common coin.</p>

<h2>How to check a suspect coin by hand</h2>
<p>Pull anything that looks wrong into a separate pile. Work one denomination at a time so diameter and weight stay comparable.</p>
<h3>Measurements first</h3>
<p>Weigh the coin on a scale that reads to 0.01 g and compare to the Mint specification for that denomination and era. Measure diameter with calipers. A broadstrike or wrong-planchet piece often fails one of those checks before you open a catalog.</p>
<h3>Edge and strike</h3>
<p>Look at the edge under light: missing reeds can signal a broadstrike; a partial design with blank field can signal off-center. Under a loupe or USB microscope, check whether doubling is raised and rounded (die doubling) or flat and shelf-like (often machine doubling).</p>
<h3>Match a published variety</h3>
<p>Published price guides and variety attributions (for example, listings maintained by services such as <a href="https://www.pcgs.com/">PCGS</a> and major variety references) are how you turn “looks odd” into a named error with a market range. That match is the tedious step: you flip between photos, date/mint, and variety notes until one page fits — or none do.</p>

<h2>Where the manual stack breaks down</h2>
<p>One odd cent is a five-minute loupe check. A handful of candidates means repeating weight, diameter, magnification, and guide lookup for each piece, then writing down what you found so you do not re-research the same coin next month. Photos in a camera roll without a linked record drift away from the coin in the tube. Value estimates without a date and source become guesses you cannot defend to yourself later.</p>
<p>That's why I developed <a href="/cvc/">Curator's Vault</a> — because it identifies the coin from a photo, returns a value estimate with the cues it used, and catalogs the piece in your vault on the phone with photos, condition, and that estimate attached. App page: <a href="/cvc/">Curator's Vault</a>. Identify walkthrough: <a href="/videos/cvc/user-guide/#identify">Identify chapter</a>.</p>
<h3>What the Identify path does on a suspect coin</h3>
<ul>
<li>Takes the photo (or photos) you shoot of the piece in hand.</li>
<li>Returns series / era cues and grading cues with an honest confidence note — not a silent “perfect match.”</li>
<li>Gives a value estimate you can store on the vault item.</li>
<li>Lets you keep the record on the device: photos, condition, provenance notes, and value in one entry across coins (and the other vault categories).</li>
</ul>
<p>Honest limits: Curator's Vault is not a grading service, authentication lab, or appraisal firm. Market estimates are informational. Confirm high-stakes sale or insurance numbers with a credentialed grader or dealer when the dollar amount warrants it.</p>

<h2>When to keep sorting by hand vs. use the vault</h2>
<p>Hand-sort when you are clearing a jar and only need to reject obvious damage. Open the vault when a coin passes the weight/diameter smell test and you need a named ID, a number next to a date, and a place to put the photo so the next check does not start from zero. Two or more candidates in one sitting is usually past the point where tab-hopping stays honest.</p>

<h2>FAQ</h2>
<h3>Are error coins still found in pocket change?</h3>
<p>Yes, though most odd coins are damage. Off-centers, clipped planchets, and occasional doubled dies or wrong-planchet strikes still leave circulation; frequency is low enough that a disciplined check beats hoping every shiny mark is valuable.</p>
<h3>Does machine doubling make a coin an error?</h3>
<p>No. Machine doubling is a strike effect that collectors treat separately from true doubled-die varieties. Under magnification, machine doubling often looks flat or shelf-like rather than raised and rounded.</p>
<h3>Should I clean a suspect error before photographing it?</h3>
<p>No. Cleaning can leave hairlines and lower collector interest. Photograph as found; note dirt or residue in the record instead of polishing.</p>
<h3>What if Identify is unsure?</h3>
<p>Treat a low-confidence result as a cue to re-shoot under even light, check weight and diameter again, or ask a dealer. The vault still stores your photos and notes so the next pass starts from the same evidence.</p>
`,
  },
  {
    slug: 'pocket-watch-grades-and-sizes-explained',
    title: 'Pocket Watch Grades and Sizes Explained',
    app: 'Handy Horology Helper',
    appHref: '/hhh/',
    ogImage: '/assets/brand/og-josspatech.jpg',
    excerpt:
      'American pocket watch “grade” and size markings decode movement quality and case fit. How to read them by hand — and when a photo ID returns movement, grade, and value.',
    body: `
      <div class="takeaways">
<h2>Key takeaways</h2>
<ul>
<li>On American pocket watches, <strong>size</strong> (for example 16-size or 18-size) describes the movement diameter class used for case fit; <strong>grade</strong> names a factory quality tier for that movement family.</li>
<li>Markings on the movement and case are not always the same story: a high-grade movement can sit in a later or mismatched case.</li>
<li>Decoding by hand means opening the case, reading size and grade marks, then matching factory catalogs or serial/grade tables for jewel count and finish level.</li>
<li>Handy Horology Helper identifies the movement from a photo (or typed clues), returns grade cues and a value estimate, and stores the piece in My Museum.</li>
<li>Use a reference book when you already know the maker and only need one line confirmed. Use the app when the dial and movement marks do not line up in one sitting.</li>
</ul>
<p>American railroad-era pocket watches used a shared language of size and grade. This article defines those terms, shows where the marks live, and marks the step where flipping between catalogs for one movement becomes the bottleneck.</p>
</div>

<h2>What “size” means on a pocket watch</h2>
<p>Size is a traditional American movement measurement class, not the case diameter in millimeters you might expect from modern wristwatches. Common classes include 18-size and 16-size open-face or hunting movements; smaller sizes appear in thinner or ladies’ pieces. Case makers built cases to fit a stated size. A 16-size movement in an 18-size case (or the reverse) is a mismatch you can see once both are identified.</p>
<h3>Where size is marked</h3>
<p>Look on the movement plates and sometimes on the case dust cover or cuvette. Sellers often list “16s” or “18s” from those marks. If only the case is marked, treat that as a case claim until the movement confirms it.</p>

<h2>What “grade” means (and what it does not)</h2>
<p>Grade is a factory designation for a movement’s quality tier within a maker’s line — finish, adjustment claims, and often jewel count sit behind that name. Elgin, Waltham, Hamilton, Illinois, and other American makers published grade lists. A grade name is not a modern “condition grade” like a coin’s AU-50; it is a model/quality label from the factory catalog.</p>
<h3>Grade vs. jewels vs. adjustments</h3>
<p>Jewel count (for example 17 jewels, 21 jewels) and adjustment statements (to temperature, positions) often travel with grade, but they are separate facts. Two movements can share a jewel count and differ in grade finish. Record size, grade name, jewel count, and serial as four fields, not one combined string.</p>
<h3>Open-face vs. hunting case</h3>
<p>Movement layout and dial orientation differ between open-face and hunting-case watches. Size still describes the movement class; the case type is a separate attribute for fit and value.</p>

<h2>How collectors decode markings by hand</h2>
<p>Open the case carefully. Photograph the dial, movement, and any serial or grade stamps. Note maker, size mark, grade mark, jewel count if stated, and case metal marks (for example gold-filled stamps). Then match the grade name and serial range in a factory table or a compiled reference for that maker.</p>
<h3>Why the lookup stalls</h3>
<p>Makers reused similar names across eras. Serial ranges determine approximate production period. Case serials and movement serials can disagree when a movement was re-cased. Getting from “Hamilton 16-size, grade stamped X” to a dated production window and a market comparison means opening more than one table — often while standing at a show with the piece in hand.</p>
<p>That's why I developed <a href="/hhh/">Handy Horology Helper</a> — because it identifies the watch from a photo or the clues you type, returns movement and grade cues with a value estimate, and stores the piece in My Museum on the device with photos and notes attached. App page: <a href="/hhh/">Handy Horology Helper</a>. Identify walkthrough: <a href="/videos/hhh/user-guide/#identify">Identify chapter</a>.</p>
<h3>What Identify returns for a pocket watch in hand</h3>
<ul>
<li>Model / movement cues from the photo and dial or plate marks you can see.</li>
<li>Grade and size-related cues when the marks are readable in the shot.</li>
<li>A rough worth estimate with confidence stated honestly.</li>
<li>A path to save the piece in <strong>My Museum</strong> (photos, serials, values) so the next lookup starts from the same record.</li>
</ul>
<p>Honest limits: HHH is not a professional appraisal or authentication service. Estimates are informational. Confirm sale or insurance numbers with a qualified watchmaker or appraiser when the stakes require it.</p>

<h2>When a catalog is enough vs. when to use the app</h2>
<p>Stay with a printed or PDF catalog when you already know the maker and grade and only need to confirm jewel count for one piece at the desk. Open HHH when the dial name, movement stamps, and case marks disagree, or when you need an ID and value estimate before the piece goes back in the tray. At a show, the phone is the tool that is actually with the watch.</p>

<h2>FAQ</h2>
<h3>Is a higher grade always worth more?</h3>
<p>Not by itself. Condition, completeness, case metal, and demand for that maker/grade matter. A worn high-grade movement in a mismatched case can sell for less than a clean mid-grade example in an original case.</p>
<h3>Do European pocket watches use the same size system?</h3>
<p>No. The American size classes are a U.S. trade convention. Swiss and other makers used different sizing and naming; do not force an American size label onto a movement that was never marked that way.</p>
<h3>Can I identify grade from the dial alone?</h3>
<p>Sometimes the dial names the maker; grade usually lives on the movement. A dial-only photo is a start. A movement photo is what grade decoding needs.</p>
<h3>Where do I store the decoded fields?</h3>
<p>In My Museum: photos, brand, model/reference, serial, movement notes, and estimated value on the piece. That keeps size/grade notes with the watch instead of in a separate spreadsheet row that drifts.</p>
`,
  },
  {
    slug: 'paper-money-seal-colors-and-series-years',
    title: 'Paper Money Seal Colors and Series Years',
    app: "Curator's Vault",
    appHref: '/cvc/',
    ogImage: '/assets/brand/og-josspatech.jpg',
    excerpt:
      'Seal color and series year place a U.S. note in a type and era. How those marks affect what collectors look up — and when photo ID plus a vault value replace the guide stack.',
    body: `
      <div class="takeaways">
<h2>Key takeaways</h2>
<ul>
<li>On U.S. paper money, <strong>seal color</strong> and <strong>series year</strong> (with signatures) are primary type clues — they separate Federal Reserve Notes, United States Notes, silver certificates, and specialty issues at a glance.</li>
<li>Series year is not always the year the note was printed; it marks a signature or design series, so two notes with the same series year can still differ in plate and signature details.</li>
<li>Value lookup by hand means identifying type from seal and obligation text, then matching series, denomination, and condition in a price guide.</li>
<li>Curator's Vault identifies a note from a photo, returns a value estimate, and catalogs it in the vault under paper money on the device.</li>
<li>Use a guide for notes you already typed correctly. Use the vault when type, series, and condition research is repeating for every bill in a stack.</li>
</ul>
<p>Seal color and series year are the first fields experienced collectors read on a U.S. note. This article maps the common seal colors to note types, explains what series year does and does not mean, and marks where hand lookup turns into a pile of open guides.</p>
</div>

<h2>Seal colors and what they usually mark</h2>
<p>Modern collectors still sort circulating and near-circulating U.S. notes by seal and obligation language. Typical associations:</p>
<ul>
<li><strong>Green seal</strong> — Federal Reserve Notes (the standard type in circulation today).</li>
<li><strong>Blue seal</strong> — historically associated with silver certificates (redeemable in silver under older law; those notes are collectible now, not a current redemption path for silver).</li>
<li><strong>Red seal</strong> — United States Notes (legal tender notes), distinct from Federal Reserve Notes.</li>
<li><strong>Brown seal</strong> — specialty issues such as Hawaii overprint notes from World War II (and some other limited issues); treat brown as a flag to read the overprint and series carefully.</li>
</ul>
<p>Always confirm with the obligation text and denomination design, not seal color alone. Counterfeits and fantasy notes exist; seal color is a sorting key, not authentication by itself.</p>

<h2>What “series year” means on a note</h2>
<p>The series year on a U.S. note identifies a signature combination and design series, not necessarily the calendar year the sheet was printed. A Series 2017A note, for example, belongs to that signature/design series; printing can continue after the calendar year in the label. When signatures change or a design revision is designated, the Bureau of Engraving and Printing advances the series letter or year per its rules.</p>
<h3>Why series still matters for value</h3>
<p>Collectors price many notes by denomination + series + district (for FRNs) + condition. Star notes (replacement notes) and certain districts carry different premiums. Getting the series wrong sends you to the wrong line in a guide.</p>

<h2>Looking up value by hand</h2>
<p>Identify type from seal color and face text. Read series year and signatures. Note the Federal Reserve bank letter/number on FRNs. Grade condition honestly (folds, soil, tears). Then open a paper-money price guide or auction comps for that exact type/series/denomination.</p>
<h3>Where the stack gets slow</h3>
<p>One note is manageable. A short stack means repeating type ID, series decode, condition calls, and guide lines for each bill, then writing results so you do not mix two similar series. Photos without a linked record make it hard to remember which bill matched which line.</p>
<p>That's why I developed <a href="/cvc/">Curator's Vault</a> — because it identifies the note from a photo, returns a value estimate with the cues it used, and catalogs the piece under paper money in your vault on the phone. App page: <a href="/cvc/">Curator's Vault</a>. Identify walkthrough: <a href="/videos/cvc/user-guide/#identify">Identify chapter</a>.</p>
<h3>What the app does on a note</h3>
<ul>
<li>Reads the photo you take of the face (and reverse when you add it).</li>
<li>Returns type / series-era cues and grading cues with confidence stated.</li>
<li>Attaches a value estimate you can store on the vault item.</li>
<li>Keeps paper money alongside coins, cards, stamps, and lighters in one on-device vault.</li>
</ul>
<p>Honest limits: estimates are not a dealer bid or a grading-service opinion. Confirm high-value notes with a paper-money dealer or third-party grading when the amount justifies it.</p>

<h2>When a guide is enough vs. when to catalog in the vault</h2>
<p>Stay in the guide when you already know the type and only need one series line at the desk. Open the vault when you are working through a stack and need each note identified, valued, and filed with its photo so the next session does not re-sort the same pile.</p>

<h2>FAQ</h2>
<h3>Does a blue seal always mean a silver certificate?</h3>
<p>Blue seals are strongly associated with silver certificates on classic U.S. notes, but you still confirm with the obligation wording and design. Do not price from seal color alone.</p>
<h3>Is an older series year automatically worth more?</h3>
<p>No. Common series in low grade often sell near face or a small premium. Scarcer combinations, stars, and high grade drive price more than “older” as a word.</p>
<h3>Should I press folds out of a note before photographing it?</h3>
<p>Do not iron or chemically flatten collectible notes; that can be considered damage. Photograph flat under even light; record folds in the condition notes.</p>
<h3>Can the vault replace a paper-money price guide?</h3>
<p>It stores your ID and estimate on the device. For a sale decision on a high-value note, compare against current dealer or auction comps as well.</p>
`,
  },
  {
    slug: 'how-to-date-a-vintage-watch-by-serial-number',
    title: 'How to Date a Vintage Watch by Serial Number',
    app: 'Handy Horology Helper',
    appHref: '/hhh/',
    ogImage: '/assets/brand/og-josspatech.jpg',
    excerpt:
      'Serial tables date many vintage watches once you know the maker. How manual lookups work — and when the app looks up the serial, jewel count, and gold vs gold-filled from a photo.',
    body: `
      <div class="takeaways">
<h2>Key takeaways</h2>
<ul>
<li>Many American and some Swiss makers published serial ranges that map roughly to production years; the serial alone is useless without the correct maker table.</li>
<li>Case serials and movement serials can disagree after a re-case; date from the movement serial when you are dating the watch as a mechanism.</li>
<li>Manual dating means reading the serial, opening the maker’s table, then separately confirming jewel count and case metal marks (solid gold vs gold-filled).</li>
<li>Handy Horology Helper looks up from a photo or clues: serial-related dating cues, jewel count when readable, and metal cues that separate solid gold from gold-filled.</li>
<li>Keep a printed table for one maker you already collect. Use the app when maker, serial, jewels, and case metal are four open questions at once.</li>
</ul>
<p>Dating a vintage watch from its serial is a table lookup — if you have the right maker and the right serial. This article covers where serials live, how tables are used, and the step where case metal and jewel count turn one lookup into three.</p>
</div>

<h2>Where serial numbers live</h2>
<p>On pocket watches, the movement serial is usually stamped on a plate visible when the case back is open. Case serials may appear on the cuvette or case lip. On wristwatches, serials can sit between lugs, on the case back, or on the movement — depending on maker and era. Always photograph the serial next to a note of whether it came from movement or case.</p>
<h3>Movement serial vs. case serial</h3>
<p>A movement serial dates the caliber’s production window in maker tables. A case serial dates the case. Re-casing was common; a solid-gold case around an older movement (or the reverse) is a fact pattern you must record, not flatten into one year.</p>

<h2>How manual serial dating works</h2>
<p>Identify the maker from dial and movement marks. Find a serial list for that maker (factory records, compiled references, or museum databases for some brands). Locate the range that contains your number. Treat the result as an approximate production window, not a birth certificate day.</p>
<h3>Limits of serial tables</h3>
<p>Gaps, reused blocks, and incomplete archives exist. Some makers are well documented; others are sparse. If two tables disagree, record both sources and dates you checked.</p>
<h3>Jewel count and case metal in the same sitting</h3>
<p>Collectors rarely stop at year. Jewel count (stamped or counted on the movement) and case marks (for example karat stamps vs gold-filled / RGP / GF marks) change what the piece is and what comps apply. Solid gold and gold-filled are different metals for pricing; confusing them is a common expensive mistake.</p>
<p>That's why I developed <a href="/hhh/">Handy Horology Helper</a> — because it looks up from a photo or the clues you enter, reports dating cues tied to the serial when the maker path supports it, reads jewel-count cues when they are visible, and flags metal cues that help separate genuine gold from gold-filled — then stores the piece in My Museum. App page: <a href="/hhh/">Handy Horology Helper</a>. Identify walkthrough: <a href="/videos/hhh/user-guide/#identify">Identify chapter</a>.</p>
<h3>Concrete steps the app performs</h3>
<ul>
<li>Accepts a photo of the dial / movement / marks, or typed clues (brand, serial, visible stamps).</li>
<li>Returns identification and dating cues for the piece.</li>
<li>Surfaces jewel-count information when the movement evidence supports it.</li>
<li>Surfaces metal / case cues used to distinguish solid gold presentations from gold-filled.</li>
<li>Saves photos, serial, and estimated value on the My Museum entry.</li>
</ul>
<p>Honest limits: serial dating is approximate. HHH is not a laboratory assay for gold content and not a substitute for a hallmark reference when selling high-karat metal. Confirm with a watchmaker or assayer when metal value dominates the price.</p>

<h2>When to stay in the tables vs. use the app</h2>
<p>Stay in the tables when you collect one maker, already know the movement, and only need the year range at a desk. Open HHH when you are holding an unfamiliar piece and need serial dating, jewel count, and gold vs gold-filled cues without juggling three references before the case closes.</p>

<h2>FAQ</h2>
<h3>Can I date any watch from the serial alone?</h3>
<p>No. You need the correct maker (and often the correct model family). A number without a maker table is just a number.</p>
<h3>What if the case says 14K but the movement is low grade?</h3>
<p>Record both facts. The case metal and the movement quality are separate value drivers; a mismatch is historically common and should stay visible in your notes.</p>
<h3>Does gold-filled mean solid gold?</h3>
<p>No. Gold-filled (and related marks) means a bonded gold layer over base metal, not a solid karat gold case. Price and scrap math differ.</p>
<h3>Where should I keep the dated record?</h3>
<p>In My Museum on the device: serial, photos, movement notes, and estimated value on the piece, with service history elsewhere in Repairs &amp; Service when you service it later.</p>
`,
  },
  {
    slug: 'what-a-subscription-audit-actually-finds',
    title: 'What a Subscription Audit Actually Finds',
    app: 'PocketBudJet',
    appHref: '/pbj/',
    ogImage: '/assets/brand/og-pbj.jpg',
    excerpt:
      'C+R Research: people guessed about $86/month in subscriptions, itemized about $219; 42% paid for a service they no longer used. How a statement audit surfaces those charges without a bank login.',
    body: `
      <div class="takeaways">
<h2>Key takeaways</h2>
<ul>
<li>In a 2022 <a href="https://www.crresearch.com/blog/subscription-service-statistics-and-costs/">C+R Research</a> survey of 1,000 U.S. consumers, people first guessed about <strong>$86 per month</strong> on subscriptions; when they itemized by category, the average was about <strong>$219</strong>.</li>
<li>In the same survey, <strong>42%</strong> said they had stopped using a subscription but were still paying for it; 74% said recurring charges were easy to forget.</li>
<li>A subscription audit is a pass over real statement lines — not a memory of what you think you pay.</li>
<li>Doing it by hand means downloading statements and marking every recurring merchant across cards and banks.</li>
<li>PocketBudJet surfaces recurring charges from a statement you share to the phone — no bank login — so the audit starts from the file, not from recall.</li>
</ul>
<p>People underestimate subscription spend until they list it. This article uses the published C+R figures, shows what a line-by-line audit actually catches, and marks where scrolling PDFs by hand becomes the bottleneck.</p>
</div>

<h2>What the documented figures say</h2>
<p>C+R Research surveyed 1,000 U.S. consumers (April 22–May 2, 2022). Respondents first estimated monthly subscription spend (about ten seconds). Later they broke spending down by category. Average first guess: about <strong>$86</strong> per month. Average after itemizing: about <strong>$219</strong> — more than double the guess. About 30% underestimated by $100–$199; about 24% underestimated by $200 or more.</p>
<p>The same study reported that <strong>42%</strong> had stopped using a service but forgotten they were still paying, and that 74% found recurring monthly charges easy to forget. Most respondents used autopay for subscriptions. Those numbers are from 2022; treat the dollar levels as that survey’s results, not a claim about your household today. The useful fact is the gap between a quick guess and a category-by-category list.</p>

<h2>What “subscription audit” means in practice</h2>
<p>An audit is a list of recurring charges found on statements, with merchant name, amount, cadence, and a keep/cancel decision. It is not a feeling that “we only have Netflix.” Streaming, software, cloud storage, memberships, box services, and app-store renewals all count when they hit the card or bank on a schedule.</p>
<h3>What it usually finds</h3>
<ul>
<li>Charges you recognize but forgot the price of.</li>
<li>Duplicates (same service on two cards, or annual + monthly leftovers).</li>
<li>Trials that converted.</li>
<li>Services nobody in the household opens anymore — the 42% pattern from the survey, seen as a concrete line.</li>
</ul>

<h2>How people do the audit by hand</h2>
<p>Download recent statements (PDF or CSV) for every card and bank account that can carry a recurring charge. Search for known merchants, then scan for anything monthly or annual you did not already list. Build a table: merchant, amount, cadence, last charge date, decision. Repeat next month because new trials appear.</p>
<h3>Where the manual pass stalls</h3>
<p>Households with several cards generate many pages. Merchant names on statements often differ from the consumer brand name. Annual charges hide if you only read one month. Sharing a spreadsheet of every subscription is itself a privacy decision many people do not want to make with a bank-linked app.</p>
<p>That's why I developed <a href="/pbj/">PocketBudJet</a> — because it imports a statement you already downloaded or shared to the phone (CSV, OFX, QFX, QIF, XLSX, PDF), surfaces recurring charges from those lines, and keeps the budget data on the device without a bank login. App page: <a href="/pbj/">PocketBudJet</a>. Related: <a href="/blog/budget-app-without-bank-login/">budget apps without bank login</a>.</p>
<h3>Concrete steps the app performs</h3>
<ul>
<li>Accepts a statement file you share or import — no Plaid-style bank login required for that path.</li>
<li>Parses transactions from the formats above.</li>
<li>Surfaces recurring / subscription-style charges from those transactions for review.</li>
<li>Lets you plan budgets and bills from the same on-phone data set.</li>
<li>Exports CSV or JSON when you want a copy outside the app.</li>
</ul>
<p>Honest limits: PocketBudJet can only see charges present in the statements you import. A card you never export will not appear. Merchant renaming and annual timing still need your eyes on the list. Premium features (including the fuller subscription tracker toolset) follow the pricing on the <a href="/pbj/">product page</a>.</p>

<h2>When a spreadsheet pass is enough vs. when to import</h2>
<p>Use a one-month PDF highlight pass if you have a single card and already know most merchants. Import into PocketBudJet when multiple statements are in play and you need recurring charges listed from the file instead of from memory — especially if you refuse a bank login for budgeting.</p>

<h2>FAQ</h2>
<h3>Do the $86 / $219 figures apply to my household?</h3>
<p>They are averages from C+R’s 2022 survey, not a prediction for you. Run the audit on your statements; your total may be lower or higher.</p>
<h3>Is a subscription audit the same as canceling everything?</h3>
<p>No. The audit produces a list and decisions. Keep what you use; cancel what you do not. The survey’s 42% figure is about paying after use stopped — the audit’s job is to make those lines visible.</p>
<h3>Why not link the bank so charges appear automatically?</h3>
<p>Some people prefer that. PocketBudJet is built for the path that keeps statements on the phone without a bank login. If you want live sync, other apps offer it; this product’s design choice is import-first.</p>
<h3>How often should I repeat the audit?</h3>
<p>After any month with new trials, and at least a few times a year for annual renewals. Importing the latest statements is the repeatable version of the same job.</p>
`,
  },
];

function writePost(p) {
  const dir = path.join(root, 'blog', p.slug);
  fs.mkdirSync(dir, { recursive: true });
  const html = shell({
    title: p.title,
    description: p.excerpt,
    canonicalPath: `/blog/${p.slug}/`,
    ogImage: p.ogImage,
    appLabel: p.app,
    appHref: p.appHref,
    bodyHtml: p.body.trim(),
  });
  fs.writeFileSync(path.join(dir, 'index.html'), html, 'utf8');
}

for (const p of posts) writePost(p);

// posts.json — newest first
const postsPath = path.join(root, 'blog', 'posts.json');
const existing = JSON.parse(fs.readFileSync(postsPath, 'utf8'));
const incoming = posts.map((p) => ({
  slug: p.slug,
  title: p.title,
  path: `/blog/${p.slug}/`,
  date: DATE,
  app: p.app,
  excerpt: p.excerpt,
}));
const bySlug = new Map(existing.map((x) => [x.slug, x]));
for (const row of incoming) bySlug.set(row.slug, row);
const merged = [...bySlug.values()].sort((a, b) => String(b.date).localeCompare(String(a.date)));
fs.writeFileSync(postsPath, JSON.stringify(merged, null, 2) + '\n', 'utf8');

// sitemap — append missing EN URLs before first locale blog entry
const smPath = path.join(root, 'sitemap.xml');
let sm = fs.readFileSync(smPath, 'utf8');
const marker = '  <url>\n    <loc>https://josspatech.com/blog/apps-for-antique-collectors/es/</loc>';
let block = '';
for (const p of posts) {
  const loc = `https://josspatech.com/blog/${p.slug}/`;
  if (sm.includes(`<loc>${loc}</loc>`)) continue;
  block += `  <url>\n    <loc>${loc}</loc>\n    <lastmod>${DATE}</lastmod>\n  </url>\n`;
}
if (block && sm.includes(marker)) sm = sm.replace(marker, block + marker);
sm = sm.replace(
  /(<loc>https:\/\/josspatech\.com\/blog\/<\/loc>\s*<lastmod>)[^<]+/,
  `$1${DATE}`,
);
fs.writeFileSync(smPath, sm, 'utf8');

// Product Guides links
function ensureGuide(fileRel, anchorHtml) {
  const fp = path.join(root, fileRel);
  let html = fs.readFileSync(fp, 'utf8');
  if (html.includes(anchorHtml.match(/href="([^"]+)"/)[1])) return;
  if (!html.includes('<h2>Guides</h2>')) {
    // PBJ has no Guides section — insert before FAQ
    html = html.replace(
      '<h2>FAQ</h2>',
      `<h2>Guides</h2>\n    <ul>\n      <li>${anchorHtml}</li>\n    </ul>\n    <p><a href="/blog/">All JosspaTech articles</a></p>\n\n    <h2>FAQ</h2>`,
    );
  } else {
    html = html.replace(
      /(<h2>Guides<\/h2>\s*<ul>)/,
      `$1\n      <li>${anchorHtml}</li>`,
    );
  }
  fs.writeFileSync(fp, html, 'utf8');
}

ensureGuide(
  'cvc/index.html',
  `<a href="/blog/error-coins-in-your-change/">Error coins you can find in your change</a>`,
);
ensureGuide(
  'cvc/index.html',
  `<a href="/blog/paper-money-seal-colors-and-series-years/">Paper money seal colors and series years</a>`,
);
ensureGuide(
  'hhh/index.html',
  `<a href="/blog/pocket-watch-grades-and-sizes-explained/">Pocket watch grades and sizes explained</a>`,
);
ensureGuide(
  'hhh/index.html',
  `<a href="/blog/how-to-date-a-vintage-watch-by-serial-number/">How to date a vintage watch by serial number</a>`,
);
ensureGuide(
  'pbj/index.html',
  `<a href="/blog/what-a-subscription-audit-actually-finds/">What a subscription audit actually finds</a>`,
);

console.log('Published', posts.map((p) => p.slug).join(', '));
console.log('posts.json count', merged.length);
