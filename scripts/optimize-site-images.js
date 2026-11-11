/**
 * Compress oversized site images in place (same path / extension).
 * Phone screenshots are often 1440×3120; web cards use ~168–560 CSS px.
 * Caps long edge / width so Pages + load time shrink without HTML churn.
 *
 * Usage: node scripts/optimize-site-images.js [--dry-run]
 */
const fs = require('fs');
const path = require('path');
const sharp = require('sharp');

const ROOT = path.resolve(__dirname, '..');
const DRY = process.argv.includes('--dry-run');

const ROOTS = [
  'assets/screenshots',
  'assets/studio',
  'assets/brand',
  'videos/pbj/intro/screens',
  'videos/hhh/intro/screens',
  'videos/cvc/intro/screens',
  'videos/unscribe/intro/screens',
];

const SKIP_DIR = new Set(['_spare', 'node_modules', '.git']);
const EXT = new Set(['.png', '.jpg', '.jpeg', '.webp']);

/** Max width for phone UI shots and studio stills. */
const MAX_W = {
  screenshots: 1080,
  studio: 1280,
  brand: 1200,
  intro: 1080,
  default: 1080,
};

function maxWidthFor(rel) {
  if (rel.includes(`${path.sep}screenshots${path.sep}`)) return MAX_W.screenshots;
  if (rel.includes(`${path.sep}studio${path.sep}`)) return MAX_W.studio;
  if (rel.includes(`${path.sep}brand${path.sep}`)) return MAX_W.brand;
  if (rel.includes(`${path.sep}intro${path.sep}screens`)) return MAX_W.intro;
  return MAX_W.default;
}

function walk(dir, out = []) {
  if (!fs.existsSync(dir)) return out;
  for (const ent of fs.readdirSync(dir, { withFileTypes: true })) {
    if (SKIP_DIR.has(ent.name)) continue;
    const full = path.join(dir, ent.name);
    if (ent.isDirectory()) walk(full, out);
    else if (EXT.has(path.extname(ent.name).toLowerCase())) out.push(full);
  }
  return out;
}

async function optimizeOne(file) {
  const rel = path.relative(ROOT, file);
  const before = fs.statSync(file).size;
  if (before < 40 * 1024) return null; // already tiny

  const ext = path.extname(file).toLowerCase();
  const maxW = maxWidthFor(rel);
  let pipeline = sharp(file, { failOn: 'none' }).rotate(); // honor EXIF
  const meta = await sharp(file, { failOn: 'none' }).metadata();
  if (meta.width && meta.width > maxW) {
    pipeline = pipeline.resize({ width: maxW, withoutEnlargement: true });
  }

  let buf;
  if (ext === '.png') {
    // Opaque UI shots compress well with palette; keep alpha when present.
    buf = await pipeline
      .png({
        compressionLevel: 9,
        effort: 10,
        quality: 80,
        adaptiveFiltering: true,
      })
      .toBuffer();
  } else if (ext === '.webp') {
    buf = await pipeline.webp({ quality: 80 }).toBuffer();
  } else {
    buf = await pipeline.jpeg({ quality: 82, mozjpeg: true }).toBuffer();
  }

  if (buf.length >= before * 0.98) return null; // not worth it
  if (!DRY) fs.writeFileSync(file, buf);
  return { rel, before, after: buf.length };
}

async function main() {
  const files = [];
  for (const r of ROOTS) walk(path.join(ROOT, r), files);
  let saved = 0;
  let changed = 0;
  let scanned = 0;
  for (const f of files) {
    scanned++;
    try {
      const res = await optimizeOne(f);
      if (!res) continue;
      changed++;
      saved += res.before - res.after;
      const pct = ((1 - res.after / res.before) * 100).toFixed(0);
      console.log(
        `${(res.before / 1e6).toFixed(2)}→${(res.after / 1e6).toFixed(2)} MB (−${pct}%)  ${res.rel}`
      );
    } catch (e) {
      console.warn('skip', path.relative(ROOT, f), e.message);
    }
  }
  console.log(
    `\n${DRY ? '[dry-run] ' : ''}scanned ${scanned}, changed ${changed}, saved ${(saved / 1e6).toFixed(1)} MB`
  );
}

main().catch((e) => {
  console.error(e);
  process.exit(1);
});
