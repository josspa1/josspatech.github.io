const { chromium } = require('playwright');
const path = require('path');
const http = require('http');
const fs = require('fs');

const ROOT = path.resolve(__dirname, '..');
const PORT = 4177;

function serve(req, res) {
  let urlPath = req.url.split('?')[0];
  if (urlPath === '/') urlPath = '/index.html';
  const filePath = path.join(ROOT, decodeURIComponent(urlPath));
  if (!filePath.startsWith(ROOT) || !fs.existsSync(filePath) || fs.statSync(filePath).isDirectory()) {
    res.writeHead(404);
    res.end('Not found');
    return;
  }
  const ext = path.extname(filePath).toLowerCase();
  const types = { '.html': 'text/html', '.js': 'application/javascript', '.css': 'text/css', '.png': 'image/png' };
  res.writeHead(200, { 'Content-Type': types[ext] || 'application/octet-stream' });
  fs.createReadStream(filePath).pipe(res);
}

async function inspect(page, label, url) {
  await page.goto(url, { waitUntil: 'networkidle' });
  await page.evaluate(() => {
    const stage = document.querySelector('.walkthrough-stage') || document.querySelector('.walkthrough');
    if (stage) stage.scrollIntoView({ block: 'center' });
  });
  await page.waitForTimeout(400);

  return page.evaluate((label) => {
    function info(el) {
      if (!el) return null;
      const r = el.getBoundingClientRect();
      const cs = getComputedStyle(el);
      return {
        w: Math.round(r.width),
        h: Math.round(r.height),
        l: Math.round(r.left),
        t: Math.round(r.top),
        objectFit: cs.objectFit,
        objectPosition: cs.objectPosition,
        overflow: cs.overflow,
        transform: cs.transform,
        width: cs.width,
        height: cs.height,
      };
    }

    const frame = document.querySelector('.phone-frame');
    const viewport = document.querySelector('.phone-viewport');
    const slideshow = document.querySelector('.slideshow');
    const img = document.querySelector('.slide.active img') || document.querySelector('.slide img');

    const frameR = frame?.getBoundingClientRect();
    const imgR = img?.getBoundingClientRect();

    let alignment = null;
    if (frameR && imgR) {
      const frameInnerL = frameR.left + parseFloat(getComputedStyle(frame).borderLeftWidth || 0);
      const frameInnerR = frameR.right - parseFloat(getComputedStyle(frame).borderRightWidth || 0);
      alignment = {
        imgLeftGap: Math.round(imgR.left - frameInnerL),
        imgRightGap: Math.round(frameInnerR - imgR.right),
        imgOverflowLeft: imgR.left < frameInnerL - 1,
        imgOverflowRight: imgR.right > frameInnerR + 1,
      };
    }

    return { label, frame: info(frame), viewport: info(viewport), slideshow: info(slideshow), img: info(img), alignment };
  }, label);
}

(async () => {
  const server = http.createServer(serve);
  await new Promise((r) => server.listen(PORT, '127.0.0.1', r));

  const browser = await chromium.launch();
  const page = await browser.newPage();
  await page.setViewportSize({ width: 1920, height: 1080 });

  const results = [
    await inspect(page, 'user-guide', `http://127.0.0.1:${PORT}/videos/user-guide/index.html`),
    await inspect(page, 'import', `http://127.0.0.1:${PORT}/videos/import/index.html`),
  ];

  console.log(JSON.stringify(results, null, 2));

  await browser.close();
  server.close();
})();
