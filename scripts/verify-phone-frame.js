#!/usr/bin/env node
'use strict';

const http = require('http');
const fs = require('fs');
const path = require('path');
const { chromium } = require('playwright');

const ROOT = path.resolve(__dirname, '..');
const PORT = 4177;
const OUT = path.join(ROOT, '_verify-phone-frame.png');

function contentType(filePath) {
  const ext = path.extname(filePath).toLowerCase();
  const map = {
    '.html': 'text/html; charset=utf-8',
    '.css': 'text/css; charset=utf-8',
    '.js': 'application/javascript; charset=utf-8',
    '.png': 'image/png',
    '.jpg': 'image/jpeg',
    '.svg': 'image/svg+xml',
    '.mp3': 'audio/mpeg',
  };
  return map[ext] || 'application/octet-stream';
}

function startServer() {
  return new Promise((resolve) => {
    const server = http.createServer((req, res) => {
      let urlPath = decodeURIComponent((req.url || '/').split('?')[0].split('#')[0]);
      if (urlPath.endsWith('/')) urlPath += 'index.html';
      const rel = urlPath.replace(/^\/+/, '') || 'index.html';
      const filePath = path.normalize(path.join(ROOT, rel));
      if (!filePath.startsWith(ROOT)) {
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
    server.listen(PORT, () => resolve(server));
  });
}

async function measure(page, label) {
  return page.evaluate((label) => {
    const frame = document.querySelector('.phone-frame');
    const screen = document.querySelector('.phone-screen, .slideshow');
    const img = document.querySelector('.slide.active img');
    const rect = (el) => {
      if (!el) return null;
      const r = el.getBoundingClientRect();
      const cs = getComputedStyle(el);
      return {
        w: Math.round(r.width),
        h: Math.round(r.height),
        left: Math.round(r.left),
        top: Math.round(r.top),
        width: cs.width,
        height: cs.height,
        objectFit: el.tagName === 'IMG' ? cs.objectFit : undefined,
        objectPosition: el.tagName === 'IMG' ? cs.objectPosition : undefined,
        transform: cs.transform,
      };
    };
    return { label, frame: rect(frame), screen: rect(screen), img: rect(img) };
  }, label);
}

(async () => {
  const server = await startServer();
  const browser = await chromium.launch();
  const page = await browser.newPage({ viewport: { width: 1280, height: 900 } });

  await page.goto(`http://127.0.0.1:${PORT}/videos/user-guide/`, { waitUntil: 'networkidle' });
  await page.click('#tapToStart', { timeout: 5000 }).catch(() => {});
  await page.evaluate(() => { if (typeof goTo === 'function') goTo(9); });
  await page.waitForTimeout(400);

  const ug = await measure(page, 'user-guide');
  await page.screenshot({ path: OUT, fullPage: false });
  console.log('Screenshot:', OUT);
  console.log(JSON.stringify(ug, null, 2));

  await page.goto(`http://127.0.0.1:${PORT}/videos/import/`, { waitUntil: 'networkidle' });
  await page.click('#tapToStart', { timeout: 5000 }).catch(() => {});
  const imp = await measure(page, 'import');
  console.log(JSON.stringify(imp, null, 2));

  const fw = ug.frame?.w || 0;
  const fh = ug.frame?.h || 0;
  const iw = ug.img?.w || 0;
  const sw = ug.screen?.w || 0;
  const issues = [];
  if (Math.abs(fw - 340) > 12) issues.push(`phone-frame width ${fw}px (expected ~340)`);
  if (Math.abs(iw - sw) > 4) issues.push(`img width ${iw}px vs screen ${sw}px`);
  if (ug.img?.left !== ug.screen?.left) issues.push(`img left ${ug.img?.left} vs screen left ${ug.screen?.left}`);
  if (issues.length) {
    console.error('ISSUES:', issues.join('; '));
    process.exitCode = 1;
  } else {
    console.log('OK: phone frame and slide img aligned');
  }

  await browser.close();
  server.close();
})();
