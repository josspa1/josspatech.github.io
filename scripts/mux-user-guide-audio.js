#!/usr/bin/env node
/** Mux existing pocketbudjet-user-guide MP4 with 89-slide narration (no re-record). */
'use strict';
const { spawnSync } = require('child_process');
const fs = require('fs');
const path = require('path');

const ROOT = path.resolve(__dirname, '..');
const OUT_DIR = path.join(ROOT, 'videos', 'user-guide');
const OUT_MP4 = path.join(OUT_DIR, 'pocketbudjet-user-guide.mp4');
const SLIDES = 89;
const SLIDE_SEC = 8;

function ffmpeg() {
  const w = spawnSync('where.exe', ['ffmpeg'], { encoding: 'utf8', shell: true });
  return w.stdout.trim().split(/\r?\n/)[0];
}

function run(ff, args) {
  const r = spawnSync(ff, args, { encoding: 'utf8', maxBuffer: 50 * 1024 * 1024 });
  if (r.status !== 0) throw new Error((r.stderr || r.stdout || '').slice(-800));
}

const ff = ffmpeg();
const audioDir = path.join(OUT_DIR, 'audio');
const combined = path.join(OUT_DIR, '_combined-narration.m4a');
const tmpDir = path.join(audioDir, '_mux_tmp');
fs.mkdirSync(tmpDir, { recursive: true });

const segPaths = [];
for (let i = 0; i < SLIDES; i++) {
  const mp3 = path.join(audioDir, `slide-${i}.mp3`);
  if (!fs.existsSync(mp3)) throw new Error(`Missing ${mp3}`);
  const seg = path.join(tmpDir, `seg-${String(i).padStart(3, '0')}.m4a`);
  run(ff, ['-y', '-i', mp3, '-af', `apad=whole_dur=${SLIDE_SEC}`, '-t', String(SLIDE_SEC), '-c:a', 'aac', '-b:a', '128k', seg]);
  segPaths.push(seg);
}
const listFile = path.join(tmpDir, 'concat.txt');
fs.writeFileSync(listFile, segPaths.map((p) => `file '${p.replace(/\\/g, '/')}'`).join('\n'));
run(ff, ['-y', '-f', 'concat', '-safe', '0', '-i', listFile, '-c:a', 'aac', '-b:a', '128k', combined]);

const tmpOut = OUT_MP4 + '.with-audio.mp4';
console.log('[mux] combining video + narration …');
run(ff, [
  '-y', '-i', OUT_MP4, '-i', combined,
  '-map', '0:v:0', '-map', '1:a:0',
  '-c:v', 'libx264', '-preset', 'fast', '-crf', '22',
  '-c:a', 'aac', '-b:a', '128k',
  '-pix_fmt', 'yuv420p', '-movflags', '+faststart',
  tmpOut,
]);
fs.renameSync(tmpOut, OUT_MP4);
try { fs.unlinkSync(combined); } catch { /* ignore */ }
for (const seg of segPaths) { try { fs.unlinkSync(seg); } catch { /* ignore */ } }
try { fs.unlinkSync(listFile); fs.rmdirSync(tmpDir); } catch { /* ignore */ }

const probe = spawnSync(ff, ['-i', OUT_MP4, '-hide_banner'], { encoding: 'utf8' });
const hasAudio = /Audio:/.test(probe.stderr || '');
const stat = fs.statSync(OUT_MP4);
console.log(JSON.stringify({ ok: true, path: OUT_MP4, sizeMb: (stat.size / 1048576).toFixed(2), hasAudio }, null, 2));
