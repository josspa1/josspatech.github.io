#!/usr/bin/env node
'use strict';

const { chromium } = require('playwright');

(async () => {
  const browser = await chromium.launch();
  const page = await browser.newPage({ viewport: { width: 1280, height: 900 } });
  await page.goto('https://josspatech.com/videos/user-guide/', { waitUntil: 'networkidle', timeout: 60000 });
  await page.click('#tapToStart', { timeout: 5000 }).catch(() => {});
  await page.evaluate(() => { if (typeof goTo === 'function') goTo(9); });
  await page.waitForTimeout(600);

  const m = await page.evaluate(() => {
    const f = document.querySelector('.phone-frame');
    const s = document.querySelector('.slideshow');
    const i = document.querySelector('.slide.active img');
    const r = (el) => (el ? el.getBoundingClientRect() : null);
    const fr = r(f);
    const sr = r(s);
    const ir = r(i);
    const hasCards = !!document.querySelector('.narration-card');
    const hasParas = document.querySelectorAll('.transcript-para').length;
    return {
      fw: Math.round(fr?.width || 0),
      fh: Math.round(fr?.height || 0),
      ioff: Math.round((ir?.left || 0) - (sr?.left || 0)),
      iw: Math.round(ir?.width || 0),
      sw: Math.round(sr?.width || 0),
      hasCards,
      hasParas,
      slideIdx: document.querySelector('.slide.active')?.getAttribute('data-index'),
    };
  });

  await page.screenshot({ path: '_verify-live-user-guide.png', fullPage: false });
  console.log(JSON.stringify(m, null, 2));
  const ok = m.fw >= 330 && m.fw <= 350 && m.ioff === 0 && m.iw === m.sw && !m.hasCards && m.hasParas > 0;
  console.log(ok ? 'LIVE OK' : 'LIVE ISSUES');
  process.exitCode = ok ? 0 : 1;
  await browser.close();
})();
