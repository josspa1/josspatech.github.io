#!/usr/bin/env node
/**
 * Render videos/user-guide-hhh/index.html to handy-horology-helper-user-guide.mp4
 * Usage: node scripts/render-user-guide-hhh-video.js [--fast]
 */
'use strict';

const { spawnSync } = require('child_process');
const fs = require('fs');
const http = require('http');
const path = require('path');

const ROOT = path.resolve(__dirname, '..');
const OUT_DIR = path.join(ROOT, 'videos', 'user-guide-hhh');
const OUT_MP4 = path.join(OUT_DIR, 'handy-horology-helper-user-guide.mp4');
const NARRATION_JSON = path.join(OUT_DIR, 'narration-en.json');

const fast = process.argv.includes('--fast');
const PORT = 4175;
const SLIDE_COUNT = JSON.parse(fs.readFileSync(NARRATION_JSON, 'utf8')).length;
const SLIDE_SEC = fast ? 2 : 8;

function resolveFfmpeg() {
  const w = spawnSync('where.exe', ['ffmpeg'], { encoding: 'utf8', shell: true });
  if (w.status === 0 && w.stdout.trim()) return w.stdout.trim().split(/\r?\n/)[0];
  return process.env.FFMPEG_PATH && fs.existsSync(process.env.FFMPEG_PATH) ? process.env.FFMPEG_PATH : null;
}

function contentType(filePath) {
  const ext = path.extname(filePath).toLowerCase();
  const map = { '.html': 'text/html; charset=utf-8', '.css': 'text/css', '.js': 'application/javascript',
    '.png': 'image/png', '.jpg': 'image/jpeg', '.mp3': 'audio/mpeg', '.json': 'application/json' };
  return map[ext] || 'application/octet-stream';
}

function startStaticServer(rootDir, port) {
  return new Promise((resolve, reject) => {
    const server = http.createServer((req, res) => {
      let urlPath = decodeURIComponent((req.url || '/').split('?')[0].split('#')[0]);
      if (urlPath.endsWith('/')) urlPath += 'index.html';
      const rel = urlPath.replace(/^\/+/, '') || 'index.html';
      const filePath = path.normalize(path.join(rootDir, rel));
      if (!filePath.startsWith(rootDir)) { res.writeHead(403); res.end('Forbidden'); return; }
      fs.readFile(filePath, (err, data) => {
        if (err) { res.writeHead(404); res.end('Not found'); return; }
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
  if (r.status !== 0) throw new Error((r.stderr || r.stdout || '').slice(-800));
}

function buildSlideAudioTrack(ffmpeg, audioDir, slideCount, slideSec, outPath) {
  const tmpDir = path.join(audioDir, '_mux_tmp');
  fs.mkdirSync(tmpDir, { recursive: true });
  const segPaths = [];
  for (let i = 0; i < slideCount; i++) {
    const mp3 = path.join(audioDir, `slide-${i}.mp3`);
    if (!fs.existsSync(mp3)) throw new Error(`Missing slide-${i}.mp3 — run gen-user-guide-hhh-en-audio.py`);
    const seg = path.join(tmpDir, `seg-${String(i).padStart(3, '0')}.m4a`);
    runFfmpeg(ffmpeg, ['-y', '-i', mp3, '-af', `apad=whole_dur=${slideSec}`, '-t', String(slideSec),
      '-c:a', 'aac', '-b:a', '128k', seg]);
    segPaths.push(seg);
  }
  const listFile = path.join(tmpDir, 'concat.txt');
  fs.writeFileSync(listFile, segPaths.map((p) => `file '${p.replace(/\\/g, '/')}'`).join('\n'), 'utf8');
  runFfmpeg(ffmpeg, ['-y', '-f', 'concat', '-safe', '0', '-i', listFile, '-c:a', 'aac', '-b:a', '128k', outPath]);
}

function buildVideoFromScreenshots(ffmpeg, shotDir, slideCount, slideSec, outPath) {
  const listFile = path.join(shotDir, 'frames.txt');
  const lines = [];
  for (let i = 0; i < slideCount; i++) {
    const png = path.join(shotDir, `frame-${String(i).padStart(3, '0')}.png`);
    lines.push(`file '${png.replace(/\\/g, '/')}'`, `duration ${slideSec}`);
  }
  lines.push(`file '${path.join(shotDir, `frame-${String(slideCount - 1).padStart(3, '0')}.png`).replace(/\\/g, '/')}'`);
  fs.writeFileSync(listFile, lines.join('\n'), 'utf8');
  runFfmpeg(ffmpeg, ['-y', '-f', 'concat', '-safe', '0', '-i', listFile,
    '-vf', 'scale=1280:800:force_original_aspect_ratio=decrease,pad=1280:800:(ow-iw)/2:(oh-ih)/2',
    '-c:v', 'libx264', '-preset', 'medium', '-crf', '20', '-pix_fmt', 'yuv420p', '-r', '30', '-an', outPath]);
}

function muxVideoAudio(ffmpeg, videoPath, audioPath, outPath) {
  const tmpOut = outPath + '.muxing.mp4';
  runFfmpeg(ffmpeg, ['-y', '-i', videoPath, '-i', audioPath, '-map', '0:v:0', '-map', '1:a:0',
    '-c:v', 'libx264', '-preset', 'fast', '-crf', '22', '-c:a', 'aac', '-b:a', '128k',
    '-pix_fmt', 'yuv420p', '-movflags', '+faststart', tmpOut]);
  fs.renameSync(tmpOut, outPath);
}

async function captureSlideScreenshots(page, shotDir, slideCount) {
  fs.mkdirSync(shotDir, { recursive: true });
  await page.evaluate(() => {
    const tap = document.getElementById('tapToStart');
    if (tap) tap.click();
  });
  await page.waitForTimeout(600);
  for (let i = 0; i < slideCount; i++) {
    await page.evaluate((idx) => {
      const dots = document.querySelectorAll('#progressDots .dot');
      if (dots[idx]) dots[idx].click();
    }, i);
    await page.waitForTimeout(500);
    await page.locator('.video-wrapper').screenshot({
      path: path.join(shotDir, `frame-${String(i).padStart(3, '0')}.png`), type: 'png',
    });
    if ((i + 1) % 5 === 0 || i === slideCount - 1) console.log(`captured ${i + 1}/${slideCount}`);
  }
}

async function main() {
  const ffmpeg = resolveFfmpeg();
  if (!ffmpeg) { console.error('ffmpeg not found'); process.exit(1); }
  const playwright = require('playwright');
  const shotDir = path.join(OUT_DIR, '_frames_tmp');
  const videoOnlyPath = OUT_MP4 + '.video-only.mp4';
  const combinedAudio = path.join(OUT_DIR, '_combined-narration.m4a');
  const server = await startStaticServer(ROOT, PORT);
  const browser = await playwright.chromium.launch({ headless: true });
  const page = await (await browser.newContext({ viewport: { width: 1280, height: 800 } })).newPage();
  try {
    await page.goto(`http://127.0.0.1:${PORT}/videos/user-guide-hhh/?record=1`, { waitUntil: 'networkidle', timeout: 120000 });
    await page.waitForSelector('.video-wrapper', { timeout: 30000 });
    await captureSlideScreenshots(page, shotDir, SLIDE_COUNT);
  } finally {
    await browser.close();
    server.close();
  }
  buildVideoFromScreenshots(ffmpeg, shotDir, SLIDE_COUNT, SLIDE_SEC, videoOnlyPath);
  buildSlideAudioTrack(ffmpeg, path.join(OUT_DIR, 'audio'), SLIDE_COUNT, SLIDE_SEC, combinedAudio);
  muxVideoAudio(ffmpeg, videoOnlyPath, combinedAudio, OUT_MP4);
  console.log('Wrote', OUT_MP4, fs.statSync(OUT_MP4).size, 'bytes');
}

main().catch((e) => { console.error(e); process.exit(1); });
