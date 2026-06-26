#!/usr/bin/env node
/** Build MP4 from cached frames + audio/ MP3s only (no Playwright). */
'use strict';
const { spawnSync } = require('child_process');
const fs = require('fs');
const path = require('path');

const ROOT = path.resolve(__dirname, '..');
const OUT_DIR = path.join(ROOT, 'videos', 'user-guide');
const SHOT_DIR = path.join(OUT_DIR, '_frames_tmp');
const AUDIO_DIR = path.join(OUT_DIR, 'audio');
const OUT_MP4 = path.join(OUT_DIR, 'pocketbudjet-user-guide.mp4');
const SLIDE_COUNT = 89;
const SLIDE_SEC = 8;

function resolveFfmpeg() {
  const w = spawnSync('where.exe', ['ffmpeg'], { encoding: 'utf8', shell: true });
  return w.status === 0 ? w.stdout.trim().split(/\r?\n/)[0] : null;
}

function runFfmpeg(ffmpeg, ffArgs) {
  const r = spawnSync(ffmpeg, ffArgs, { encoding: 'utf8', maxBuffer: 50 * 1024 * 1024 });
  if (r.status !== 0) throw new Error((r.stderr || '').slice(-800));
}

function buildSlideAudioTrack(ffmpeg, slideCount, slideSec, outPath) {
  const tmpDir = path.join(AUDIO_DIR, '_mux_tmp');
  fs.mkdirSync(tmpDir, { recursive: true });
  const segPaths = [];
  for (let i = 0; i < slideCount; i++) {
    const mp3 = path.join(AUDIO_DIR, `slide-${i}.mp3`);
    const seg = path.join(tmpDir, `seg-${String(i).padStart(3, '0')}.m4a`);
    runFfmpeg(ffmpeg, ['-y', '-i', mp3, '-af', `apad=whole_dur=${slideSec}`, '-t', String(slideSec), '-c:a', 'aac', '-b:a', '128k', seg]);
    segPaths.push(seg);
  }
  const listFile = path.join(tmpDir, 'concat.txt');
  fs.writeFileSync(listFile, segPaths.map((p) => `file '${p.replace(/\\/g, '/')}'`).join('\n'));
  runFfmpeg(ffmpeg, ['-y', '-f', 'concat', '-safe', '0', '-i', listFile, '-c:a', 'aac', '-b:a', '128k', outPath]);
}

function buildVideoFromScreenshots(ffmpeg, slideCount, slideSec, outPath) {
  const listFile = path.join(SHOT_DIR, 'frames.txt');
  const lines = [];
  for (let i = 0; i < slideCount; i++) {
    const png = path.join(SHOT_DIR, `frame-${String(i).padStart(3, '0')}.png`);
    lines.push(`file '${png.replace(/\\/g, '/')}'`);
    lines.push(`duration ${slideSec}`);
  }
  const lastPng = path.join(SHOT_DIR, `frame-${String(slideCount - 1).padStart(3, '0')}.png`);
  lines.push(`file '${lastPng.replace(/\\/g, '/')}'`);
  fs.writeFileSync(listFile, lines.join('\n'));
  runFfmpeg(ffmpeg, [
    '-y', '-f', 'concat', '-safe', '0', '-i', listFile,
    '-vf', 'scale=1280:800:force_original_aspect_ratio=decrease,pad=1280:800:(ow-iw)/2:(oh-ih)/2',
    '-c:v', 'libx264', '-preset', 'medium', '-crf', '20', '-pix_fmt', 'yuv420p', '-r', '30', '-an', outPath,
  ]);
}

const ffmpeg = resolveFfmpeg();
const videoOnly = OUT_MP4 + '.video-only.mp4';
const combined = path.join(OUT_DIR, '_combined-narration.m4a');
console.log('[mux] video from frames …');
buildVideoFromScreenshots(ffmpeg, SLIDE_COUNT, SLIDE_SEC, videoOnly);
console.log('[mux] audio track …');
buildSlideAudioTrack(ffmpeg, SLIDE_COUNT, SLIDE_SEC, combined);
console.log('[mux] final …');
runFfmpeg(ffmpeg, ['-y', '-i', videoOnly, '-i', combined, '-c:v', 'copy', '-c:a', 'aac', '-b:a', '128k', '-map', '0:v:0', '-map', '1:a:0', '-shortest', '-movflags', '+faststart', OUT_MP4]);
const stat = fs.statSync(OUT_MP4);
console.log(JSON.stringify({ ok: true, path: OUT_MP4, sizeMb: (stat.size / 1048576).toFixed(2) }, null, 2));
