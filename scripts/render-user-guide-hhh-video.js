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
const portArg = process.argv.find((a) => a.startsWith('--port='));
const PORT = portArg ? parseInt(portArg.split('=')[1], 10) : 4175;
const SLIDE_COUNT = JSON.parse(fs.readFileSync(NARRATION_JSON, 'utf8')).length;
const CHANGE_BUFFER_SEC = fast ? 0.1 : 0.18;
const SAME_BUFFER_SEC = fast ? 0.05 : 0.06;
const INDEX_HTML = path.join(OUT_DIR, 'index.html');

function parseSlideImageKeys(htmlPath) {
  const html = fs.readFileSync(htmlPath, 'utf8');
  const keys = [];
  const blocks = html.split(/<div class="slide(?:\s+active)?"/);
  for (let i = 1; i < blocks.length; i++) {
    const img = blocks[i].match(/<img src="([^"]+)"/);
    keys.push(img ? img[1] : `placeholder:${i - 1}`);
  }
  return keys;
}

function parseSlideTapMeta(htmlPath) {
  const html = fs.readFileSync(htmlPath, 'utf8');
  const meta = [];
  const blocks = html.split(/<div class="slide(?:\s+active)?"/);
  for (let i = 1; i < blocks.length; i++) {
    const block = blocks[i];
    const tapNone = /\bdata-tap-none\b/.test(block.split('>')[0]);
    const tapX = block.match(/\bdata-tap-x="([^"]+)"/);
    const showAt = block.match(/\bdata-tap-show-at="([^"]+)"/);
    const duration = block.match(/\bdata-tap-duration="([^"]+)"/);
    meta.push({
      tapNone,
      hasTap: !tapNone && !!tapX,
      showAt: showAt ? parseFloat(showAt[1]) : 0.3,
      duration: duration ? parseFloat(duration[1]) : 2.5,
    });
  }
  return meta;
}

function advanceBufferSec(imageKeys, slideIndex) {
  const next = slideIndex < imageKeys.length - 1 ? slideIndex + 1 : slideIndex;
  return imageKeys[slideIndex] === imageKeys[next] ? SAME_BUFFER_SEC : CHANGE_BUFFER_SEC;
}

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

function probeDuration(ffmpeg, filePath) {
  const r = spawnSync(ffmpeg, ['-i', filePath, '-f', 'null', '-'], { encoding: 'utf8' });
  const m = (r.stderr || '').match(/Duration:\s*(\d+):(\d+):(\d+(?:\.\d+)?)/);
  if (!m) return null;
  return parseInt(m[1], 10) * 3600 + parseInt(m[2], 10) * 60 + parseFloat(m[3]);
}

function getSlideDurations(ffmpeg, audioDir, slideCount, imageKeys) {
  const durations = [];
  for (let i = 0; i < slideCount; i++) {
    const mp3 = path.join(audioDir, `slide-${i}.mp3`);
    if (!fs.existsSync(mp3)) throw new Error(`Missing slide-${i}.mp3 — run gen-user-guide-hhh-en-audio.py`);
    if (fast) {
      durations.push(2);
      continue;
    }
    const narrationSec = probeDuration(ffmpeg, mp3);
    if (narrationSec == null) throw new Error(`Could not probe duration for slide-${i}.mp3`);
    const bufferSec = advanceBufferSec(imageKeys, i);
    durations.push(Math.max(0.5, narrationSec + bufferSec));
  }
  return durations;
}

function buildSlideAudioTrack(ffmpeg, audioDir, slideDurations, outPath) {
  const tmpDir = path.join(audioDir, '_mux_tmp');
  fs.mkdirSync(tmpDir, { recursive: true });
  const segPaths = [];
  for (let i = 0; i < slideDurations.length; i++) {
    const slideSec = slideDurations[i];
    const mp3 = path.join(audioDir, `slide-${i}.mp3`);
    const seg = path.join(tmpDir, `seg-${String(i).padStart(3, '0')}.m4a`);
    runFfmpeg(ffmpeg, ['-y', '-i', mp3, '-af', `apad=whole_dur=${slideSec}`, '-t', String(slideSec),
      '-c:a', 'aac', '-b:a', '128k', seg]);
    segPaths.push(seg);
  }
  const listFile = path.join(tmpDir, 'concat.txt');
  fs.writeFileSync(listFile, segPaths.map((p) => `file '${p.replace(/\\/g, '/')}'`).join('\n'), 'utf8');
  runFfmpeg(ffmpeg, ['-y', '-f', 'concat', '-safe', '0', '-i', listFile, '-c:a', 'aac', '-b:a', '128k', outPath]);
}

function buildVideoFromScreenshots(ffmpeg, shotDir, slideDurations, tapMeta, outPath) {
  const listFile = path.join(shotDir, 'frames.txt');
  const lines = [];
  for (let i = 0; i < slideDurations.length; i++) {
    const slideSec = slideDurations[i];
    const meta = tapMeta[i] || { hasTap: false };
    const prePng = path.join(shotDir, `frame-${String(i).padStart(3, '0')}-pre.png`);
    const tapPng = path.join(shotDir, `frame-${String(i).padStart(3, '0')}-tap.png`);
    const singlePng = path.join(shotDir, `frame-${String(i).padStart(3, '0')}.png`);

    if (meta.hasTap && fs.existsSync(prePng) && fs.existsSync(tapPng)) {
      const showAt = Math.min(meta.showAt, Math.max(0, slideSec - meta.duration - 0.1));
      const tapDur = Math.min(meta.duration, Math.max(0.3, slideSec - showAt));
      const postDur = Math.max(0.05, slideSec - showAt - tapDur);
      const prePath = prePng.replace(/\\/g, '/');
      const tapPath = tapPng.replace(/\\/g, '/');
      lines.push(`file '${prePath}'`, `duration ${showAt}`);
      lines.push(`file '${tapPath}'`, `duration ${tapDur}`);
      if (postDur > 0.05) lines.push(`file '${prePath}'`, `duration ${postDur}`);
    } else {
      const png = fs.existsSync(singlePng) ? singlePng : prePng;
      lines.push(`file '${png.replace(/\\/g, '/')}'`, `duration ${slideSec}`);
    }
  }
  const lastIdx = slideDurations.length - 1;
  const lastMeta = tapMeta[lastIdx] || { hasTap: false };
  let lastPng;
  if (lastMeta.hasTap) {
    const postDur = Math.max(0.05, slideDurations[lastIdx] - lastMeta.showAt - lastMeta.duration);
    lastPng = postDur > 0.05
      ? path.join(shotDir, `frame-${String(lastIdx).padStart(3, '0')}-pre.png`)
      : path.join(shotDir, `frame-${String(lastIdx).padStart(3, '0')}-tap.png`);
  } else {
    lastPng = path.join(shotDir, `frame-${String(lastIdx).padStart(3, '0')}.png`);
  }
  lines.push(`file '${lastPng.replace(/\\/g, '/')}'`);
  fs.writeFileSync(listFile, lines.join('\n'), 'utf8');
  runFfmpeg(ffmpeg, ['-y', '-f', 'concat', '-safe', '0', '-i', listFile,
    '-vf', 'scale=1280:800:force_original_aspect_ratio=decrease,pad=1280:800:(ow-iw)/2:(oh-ih)/2',
    '-c:v', 'libx264', '-preset', 'medium', '-crf', '20', '-pix_fmt', 'yuv420p', '-r', '30', '-an', outPath]);
}

function muxVideoAudio(ffmpeg, videoPath, audioPath, outPath) {
  // Copy video — re-encoding here was a common source of A/V drift vs padded narration.
  const tmpOut = outPath + '.muxing.mp4';
  runFfmpeg(ffmpeg, ['-y', '-i', videoPath, '-i', audioPath, '-map', '0:v:0', '-map', '1:a:0',
    '-c:v', 'copy', '-c:a', 'aac', '-b:a', '128k', '-shortest',
    '-movflags', '+faststart', tmpOut]);
  fs.renameSync(tmpOut, outPath);
}

async function captureSlideScreenshots(page, shotDir, slideCount, tapMeta) {
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
    await page.waitForTimeout(400);

    const meta = tapMeta[i] || { hasTap: false };
    const pad = String(i).padStart(3, '0');
    const wrapper = page.locator('.video-wrapper');

    if (meta.hasTap) {
      await page.evaluate((idx) => {
        if (window.PBJWalkthrough && window.PBJWalkthrough.hideTapNow) {
          window.PBJWalkthrough.hideTapNow(idx);
        }
      }, i);
      await page.waitForTimeout(150);
      await wrapper.screenshot({ path: path.join(shotDir, `frame-${pad}-pre.png`), type: 'png' });

      await page.evaluate((idx) => {
        if (window.PBJWalkthrough && window.PBJWalkthrough.showTapNow) {
          window.PBJWalkthrough.showTapNow(idx);
        }
      }, i);
      await page.waitForTimeout(250);
      await wrapper.screenshot({ path: path.join(shotDir, `frame-${pad}-tap.png`), type: 'png' });

      await page.evaluate((idx) => {
        if (window.PBJWalkthrough && window.PBJWalkthrough.hideTapNow) {
          window.PBJWalkthrough.hideTapNow(idx);
        }
      }, i);
    } else {
      await wrapper.screenshot({ path: path.join(shotDir, `frame-${pad}.png`), type: 'png' });
    }

    if ((i + 1) % 5 === 0 || i === slideCount - 1) console.log(`captured ${i + 1}/${slideCount}`);
  }
}

async function main() {
  const ffmpeg = resolveFfmpeg();
  if (!ffmpeg) { console.error('ffmpeg not found'); process.exit(1); }
  const playwright = require('playwright');
  const audioDir = path.join(OUT_DIR, 'audio');
  const imageKeys = parseSlideImageKeys(INDEX_HTML);
  const tapMeta = parseSlideTapMeta(INDEX_HTML);
  if (imageKeys.length !== SLIDE_COUNT) {
    throw new Error(`Slide/image count mismatch: html=${imageKeys.length} narration=${SLIDE_COUNT}`);
  }
  if (tapMeta.length !== SLIDE_COUNT) {
    throw new Error(`Tap meta count mismatch: html=${tapMeta.length} narration=${SLIDE_COUNT}`);
  }
  const slideDurations = getSlideDurations(ffmpeg, audioDir, SLIDE_COUNT, imageKeys);
  const totalSec = slideDurations.reduce((a, b) => a + b, 0);
  const sameCount = imageKeys.slice(0, -1).filter((k, i) => k === imageKeys[i + 1]).length;
  console.log(`slides=${SLIDE_COUNT} totalSec=${totalSec.toFixed(1)} changeBuf=${CHANGE_BUFFER_SEC}s sameBuf=${SAME_BUFFER_SEC}s samePairs=${sameCount}`);

  const shotDir = path.join(OUT_DIR, '_frames_tmp');
  const videoOnlyPath = OUT_MP4 + '.video-only.mp4';
  const combinedAudio = path.join(OUT_DIR, '_combined-narration.m4a');
  const server = await startStaticServer(ROOT, PORT);
  const browser = await playwright.chromium.launch({ headless: true });
  const page = await (await browser.newContext({ viewport: { width: 1280, height: 800 } })).newPage();
  try {
    await page.goto(`http://127.0.0.1:${PORT}/videos/user-guide-hhh/?record=1`, { waitUntil: 'networkidle', timeout: 120000 });
    await page.waitForSelector('.video-wrapper', { timeout: 30000 });
    await captureSlideScreenshots(page, shotDir, SLIDE_COUNT, tapMeta);
  } finally {
    await browser.close();
    server.close();
  }
  buildVideoFromScreenshots(ffmpeg, shotDir, slideDurations, tapMeta, videoOnlyPath);
  buildSlideAudioTrack(ffmpeg, audioDir, slideDurations, combinedAudio);
  muxVideoAudio(ffmpeg, videoOnlyPath, combinedAudio, OUT_MP4);

  const duration = probeDuration(ffmpeg, OUT_MP4);
  console.log('Wrote', OUT_MP4, fs.statSync(OUT_MP4).size, 'bytes', 'durationSec=', duration ? duration.toFixed(1) : '?');
}

main().catch((e) => { console.error(e); process.exit(1); });
