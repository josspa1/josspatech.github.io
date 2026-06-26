#!/usr/bin/env node
/**
 * Render videos/user-guide/index.html to MP4 with muxed per-slide narration.
 *
 * Captures one viewport screenshot per slide (phone frame + transcript), then
 * assembles 8s/slide video via ffmpeg and muxes edge-tts MP3s from audio/.
 *
 * Usage:
 *   node scripts/render-user-guide-video.js [--preview] [--port=4174] [--fast]
 *
 *   --preview   Slides 0–26 only
 *   --fast      2s/slide (smoke test)
 */
'use strict';

const { spawnSync } = require('child_process');
const fs = require('fs');
const http = require('http');
const path = require('path');

const ROOT = path.resolve(__dirname, '..');
const OUT_DIR = path.join(ROOT, 'videos', 'user-guide');
const OUT_MP4 = path.join(OUT_DIR, 'pocketbudjet-user-guide.mp4');
const PREVIEW_MP4 = path.join(OUT_DIR, 'pocketbudjet-user-guide-preview.mp4');

const args = process.argv.slice(2);
const preview = args.includes('--preview');
const fast = args.includes('--fast');
const portArg = args.find((a) => a.startsWith('--port='));
const PORT = portArg ? parseInt(portArg.split('=')[1], 10) : 4174;

const SLIDE_COUNT = preview ? 27 : 28;
const SLIDE_SEC = fast ? 2 : 8;

function resolveFfmpeg() {
  const fromEnv = process.env.FFMPEG_PATH;
  if (fromEnv && fs.existsSync(fromEnv)) return fromEnv;
  const w = spawnSync('where.exe', ['ffmpeg'], { encoding: 'utf8', shell: true });
  if (w.status === 0 && w.stdout.trim()) return w.stdout.trim().split(/\r?\n/)[0];
  return null;
}

function contentType(filePath) {
  const ext = path.extname(filePath).toLowerCase();
  const map = {
    '.html': 'text/html; charset=utf-8',
    '.css': 'text/css; charset=utf-8',
    '.js': 'application/javascript; charset=utf-8',
    '.png': 'image/png',
    '.jpg': 'image/jpeg',
    '.jpeg': 'image/jpeg',
    '.webp': 'image/webp',
    '.svg': 'image/svg+xml',
    '.json': 'application/json',
    '.pdf': 'application/pdf',
    '.mp3': 'audio/mpeg',
    '.mp4': 'video/mp4',
    '.woff2': 'font/woff2',
    '.ico': 'image/x-icon',
  };
  return map[ext] || 'application/octet-stream';
}

function startStaticServer(rootDir, port) {
  return new Promise((resolve, reject) => {
    const server = http.createServer((req, res) => {
      let urlPath = decodeURIComponent((req.url || '/').split('?')[0].split('#')[0]);
      if (urlPath.endsWith('/')) urlPath += 'index.html';
      const rel = urlPath.replace(/^\/+/, '') || 'index.html';
      const filePath = path.normalize(path.join(rootDir, rel));
      if (!filePath.startsWith(rootDir)) {
        res.writeHead(403);
        res.end('Forbidden');
        return;
      }
      fs.readFile(filePath, (err, data) => {
        if (err) {
          res.writeHead(404);
          res.end('Not found');
          return;
        }
        res.writeHead(200, { 'Content-Type': contentType(filePath) });
        res.end(data);
      });
    });
    server.on('error', reject);
    server.listen(port, '127.0.0.1', () => resolve(server));
  });
}

function runFfmpeg(ffmpeg, ffArgs) {
  const r = spawnSync(ffmpeg, ffArgs, { encoding: 'utf8', maxBuffer: 50 * 1024 * 1024 });
  if (r.status !== 0) {
    throw new Error(`ffmpeg failed: ${(r.stderr || r.stdout || '').slice(-800)}`);
  }
}

function probeDuration(ffmpeg, filePath) {
  const r = spawnSync(ffmpeg, ['-i', filePath, '-f', 'null', '-'], { encoding: 'utf8' });
  const m = (r.stderr || '').match(/Duration:\s*(\d+):(\d+):(\d+(?:\.\d+)?)/);
  if (!m) return null;
  return parseInt(m[1], 10) * 3600 + parseInt(m[2], 10) * 60 + parseFloat(m[3]);
}

function buildSlideAudioTrack(ffmpeg, audioDir, slideCount, slideSec, outPath) {
  const tmpDir = path.join(audioDir, '_mux_tmp');
  fs.mkdirSync(tmpDir, { recursive: true });
  const segPaths = [];

  for (let i = 0; i < slideCount; i++) {
    const mp3 = path.join(audioDir, `slide-${i}.mp3`);
    if (!fs.existsSync(mp3)) {
      throw new Error(`Missing narration MP3: slide-${i}.mp3 (run: npm run gen:user-guide-audio)`);
    }
    const seg = path.join(tmpDir, `seg-${String(i).padStart(3, '0')}.m4a`);
    runFfmpeg(ffmpeg, [
      '-y', '-i', mp3,
      '-af', `apad=whole_dur=${slideSec}`,
      '-t', String(slideSec),
      '-c:a', 'aac', '-b:a', '128k',
      seg,
    ]);
    segPaths.push(seg);
  }

  const listFile = path.join(tmpDir, 'concat.txt');
  const listBody = segPaths.map((p) => `file '${p.replace(/\\/g, '/').replace(/'/g, "'\\''")}'`).join('\n');
  fs.writeFileSync(listFile, listBody, 'utf8');

  runFfmpeg(ffmpeg, [
    '-y', '-f', 'concat', '-safe', '0', '-i', listFile,
    '-c:a', 'aac', '-b:a', '128k',
    outPath,
  ]);

  try {
    for (const seg of segPaths) fs.unlinkSync(seg);
    fs.unlinkSync(listFile);
    fs.rmdirSync(tmpDir);
  } catch { /* ignore */ }
}

function buildVideoFromScreenshots(ffmpeg, shotDir, slideCount, slideSec, outPath) {
  const listFile = path.join(shotDir, 'frames.txt');
  const lines = [];
  for (let i = 0; i < slideCount; i++) {
    const png = path.join(shotDir, `frame-${String(i).padStart(3, '0')}.png`);
    if (!fs.existsSync(png)) throw new Error(`Missing screenshot: ${png}`);
    lines.push(`file '${png.replace(/\\/g, '/').replace(/'/g, "'\\''")}'`);
    lines.push(`duration ${slideSec}`);
  }
  const lastPng = path.join(shotDir, `frame-${String(slideCount - 1).padStart(3, '0')}.png`);
  lines.push(`file '${lastPng.replace(/\\/g, '/').replace(/'/g, "'\\''")}'`);
  fs.writeFileSync(listFile, lines.join('\n'), 'utf8');

  runFfmpeg(ffmpeg, [
    '-y', '-f', 'concat', '-safe', '0', '-i', listFile,
    '-vf', 'scale=1280:800:force_original_aspect_ratio=decrease,pad=1280:800:(ow-iw)/2:(oh-ih)/2',
    '-c:v', 'libx264', '-preset', 'medium', '-crf', '20',
    '-pix_fmt', 'yuv420p', '-r', '30',
    '-an',
    outPath,
  ]);
}

function muxVideoAudio(ffmpeg, videoPath, audioPath, outPath) {
  runFfmpeg(ffmpeg, [
    '-y', '-i', videoPath, '-i', audioPath,
    '-c:v', 'copy', '-c:a', 'aac', '-b:a', '128k',
    '-map', '0:v:0', '-map', '1:a:0',
    '-shortest',
    '-movflags', '+faststart',
    outPath,
  ]);
}

async function captureSlideScreenshots(page, shotDir, slideCount) {
  fs.mkdirSync(shotDir, { recursive: true });
  await page.evaluate(() => {
    const tap = document.getElementById('tapToStart');
    if (tap && !tap.classList.contains('hidden')) tap.click();
    window.__pbjCaptureMode = true;
  });
  await page.waitForTimeout(500);

  for (let i = 0; i < slideCount; i++) {
    await page.evaluate((idx) => {
      const dots = document.getElementById('dots');
      if (dots && dots.children[idx]) dots.children[idx].click();
    }, i);
    await page.waitForTimeout(450);
    const out = path.join(shotDir, `frame-${String(i).padStart(3, '0')}.png`);
    await page.locator('.video-wrapper').screenshot({ path: out, type: 'png' });
    if ((i + 1) % 10 === 0 || i === slideCount - 1) {
      console.log(`[render] captured ${i + 1}/${slideCount} frames`);
    }
  }
}

async function main() {
  const ffmpeg = resolveFfmpeg();
  if (!ffmpeg) {
    console.error('[fatal] ffmpeg not found — install: winget install Gyan.FFmpeg');
    process.exit(1);
  }

  const playwright = require('playwright');

  fs.mkdirSync(OUT_DIR, { recursive: true });
  const shotDir = path.join(OUT_DIR, '_frames_tmp');
  const outPath = preview ? PREVIEW_MP4 : OUT_MP4;
  const videoOnlyPath = outPath + '.video-only.mp4';
  const combinedAudio = path.join(OUT_DIR, '_combined-narration.m4a');

  console.log(`[render] mode=${preview ? 'preview' : 'full'} slides=${SLIDE_COUNT} slideSec=${SLIDE_SEC}`);

  const server = await startStaticServer(ROOT, PORT);
  const recordUrl = `http://127.0.0.1:${PORT}/videos/user-guide/?record=1${preview ? '&preview=1' : ''}`;

  const browser = await playwright.chromium.launch({
    headless: true,
    args: ['--disable-dev-shm-usage', '--no-sandbox'],
  });
  const context = await browser.newContext({
    viewport: { width: 1280, height: 800 },
    deviceScaleFactor: 1,
    hasTouch: false,
    locale: 'en-US',
  });

  await context.addInitScript(() => {
    Object.defineProperty(navigator, 'maxTouchPoints', { get: () => 0 });
  });

  const page = await context.newPage();

  try {
    await page.goto(recordUrl, { waitUntil: 'networkidle', timeout: 120000 });
    await page.waitForSelector('.video-wrapper', { timeout: 30000 });
    console.log('[render] capturing slide screenshots …');
    await captureSlideScreenshots(page, shotDir, SLIDE_COUNT);
  } finally {
    await context.close();
    await browser.close();
    server.close();
  }

  console.log('[render] building video from frames …');
  buildVideoFromScreenshots(ffmpeg, shotDir, SLIDE_COUNT, SLIDE_SEC, videoOnlyPath);

  const audioDir = path.join(OUT_DIR, 'audio');
  console.log(`[render] building ${SLIDE_COUNT}-slide narration track (${SLIDE_SEC}s/slide) …`);
  buildSlideAudioTrack(ffmpeg, audioDir, SLIDE_COUNT, SLIDE_SEC, combinedAudio);

  console.log('[render] muxing video + narration …');
  muxVideoAudio(ffmpeg, videoOnlyPath, combinedAudio, outPath);

  try { fs.unlinkSync(videoOnlyPath); } catch { /* ignore */ }
  try { fs.unlinkSync(combinedAudio); } catch { /* ignore */ }
  try {
    for (const f of fs.readdirSync(shotDir)) fs.unlinkSync(path.join(shotDir, f));
    fs.rmdirSync(shotDir);
  } catch { /* ignore */ }

  const stat = fs.statSync(outPath);
  const duration = probeDuration(ffmpeg, outPath);
  const audioProbe = spawnSync(ffmpeg, [
    '-i', outPath, '-hide_banner',
  ], { encoding: 'utf8' });
  const hasAudio = /Audio:/.test(audioProbe.stderr || '');

  console.log(JSON.stringify({
    ok: true,
    path: outPath,
    sizeBytes: stat.size,
    sizeMb: (stat.size / (1024 * 1024)).toFixed(2),
    durationSec: duration ? Math.round(duration) : null,
    slides: SLIDE_COUNT,
    slideSec: SLIDE_SEC,
    hasAudio,
    preview,
  }, null, 2));
}

main().catch((err) => {
  console.error('[fatal]', err.message || err);
  process.exit(1);
});
