#!/usr/bin/env node
'use strict';

const http = require('http');
const fs = require('fs');
const path = require('path');
const { chromium } = require('playwright');

const ROOT = path.resolve(__dirname, '..');
const PORT = 4180;
const SLIDES = [0, 1, 2];

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

(async () => {
  const server = await startServer();
  const browser = await chromium.launch();
  const page = await browser.newPage({ viewport: { width: 1280, height: 900 } });

  await page.goto(`http://127.0.0.1:${PORT}/videos/user-guide/`, { waitUntil: 'networkidle' });
  await page.click('#tapToStart', { timeout: 5000 }).catch(() => {});

  const issues = [];
  const results = [];

  for (const slideIdx of SLIDES) {
    await page.evaluate((idx) => {
      const slides = document.querySelectorAll('.slide');
      const dots = document.querySelectorAll('.progress-dots .dot');
      slides.forEach((s, i) => s.classList.toggle('active', i === idx));
      dots.forEach((d, i) => d.classList.toggle('active', i === idx));
    }, slideIdx);
    await page.waitForTimeout(500);

    const m = await page.evaluate((idx) => {
      const frame = document.querySelector('.phone-frame');
      const slideshow = document.querySelector('.slideshow');
      const slide = document.querySelector('.slide.active');
      const img = slide?.querySelector('img');
      const r = (el) => (el ? el.getBoundingClientRect() : null);
      const fr = r(frame);
      const sr = r(slideshow);
      const ir = r(img);
      const cs = img ? getComputedStyle(img) : {};
      const fitInside =
        ir &&
        sr &&
        ir.top >= sr.top - 1 &&
        ir.left >= sr.left - 1 &&
        ir.bottom <= sr.bottom + 1 &&
        ir.right <= sr.right + 1;
      return {
        slideIdx: slide?.getAttribute('data-index'),
        fw: Math.round(fr?.width || 0),
        fh: Math.round(fr?.height || 0),
        sw: Math.round(sr?.width || 0),
        sh: Math.round(sr?.height || 0),
        iw: Math.round(ir?.width || 0),
        ih: Math.round(ir?.height || 0),
        fit: cs.objectFit,
        fitInside,
        src: img?.getAttribute('src') || '',
      };
    }, slideIdx);

    results.push(m);
    if (String(m.slideIdx) !== String(slideIdx)) issues.push(`slide ${slideIdx}: active data-index=${m.slideIdx}`);
    if (m.fit !== 'contain') issues.push(`slide ${slideIdx}: object-fit=${m.fit} (expected contain)`);
    if (!m.fitInside) issues.push(`slide ${slideIdx}: img clipped outside slideshow`);
    if (m.fw < 330 || m.fw > 350) issues.push(`slide ${slideIdx}: phone-frame width ${m.fw}px (expected ~340)`);
  }

  const sideBySide = await page.evaluate(() => {
    const wrapper = document.querySelector('.video-wrapper');
    const phone = document.querySelector('.phone-column');
    const narr = document.querySelector('.narration-panel');
    if (!wrapper || !phone || !narr) return false;
    const wr = wrapper.getBoundingClientRect();
    const pr = phone.getBoundingClientRect();
    const nr = narr.getBoundingClientRect();
    return pr.left < nr.left && pr.top <= nr.top + 20 && nr.height > 100;
  });
  if (!sideBySide) issues.push('side-by-side transcript layout broken at 1280px');

  await page.evaluate(() => { if (typeof goTo === 'function') goTo(0); });
  await page.waitForTimeout(300);
  await page.screenshot({ path: path.join(ROOT, '_verify-slides-0-2.png'), fullPage: false });

  console.log(JSON.stringify({ results, sideBySide, issues }, null, 2));
  if (issues.length) {
    console.error('FAIL:', issues.join('; '));
    process.exitCode = 1;
  } else {
    console.log('OK: slides 0-2 fully visible, contain fit, side-by-side layout');
  }

  await browser.close();
  server.close();
})();
